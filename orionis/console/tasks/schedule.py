import asyncio
import logging
from collections.abc import Coroutine
from typing import Self, TYPE_CHECKING
from collections.abc import Callable
from apscheduler.events import SchedulerEvent as APSchedulerEvent
from apscheduler.events import JobEvent as APJobEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from orionis.console.contracts.schedule import ISchedule
from orionis.console.core.contracts.reactor import IReactor
from orionis.console.entities.scheduler_event import (
    SchedulerEvent as SchedulerEventEntity,
)
from orionis.console.enums.events import SchedulerEvent, TaskEvent
from orionis.console.fluent.contracts.task import ITask
from orionis.console.fluent.task import Task
from orionis.console.tasks.states import ScheduleStates
from orionis.failure.contracts.catch import ICatch
from orionis.support.facades.logger import Log
from orionis.support.time.local import LocalDateTime
from orionis.console.entities.task_event import TaskEvent as TaskEventEntity

if TYPE_CHECKING:
    from orionis.console.entities.task import Task as TaskEntity

class Schedule(ISchedule):

    # ruff: noqa: BLE001, PLW0108

    _SCHEDULER_NOT_STARTED_ERROR = "The Orionis task scheduler has not been started."

    def __init__(
        self,
        reactor: IReactor,
        exception_handler: ICatch,
    ) -> None:
        """
        Initialize the Schedule instance.

        Parameters
        ----------
        reactor : IReactor
            Reactor instance for command execution.
        exception_handler : ICatch
            Exception handler for managing errors.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        self.__reactor: IReactor = reactor
        self.__exception_handler: ICatch = exception_handler
        self.__available_command_signatures: set[str] = set()
        self.__scheduler: AsyncIOScheduler | None = None
        self.__scheduler_listeners: dict[SchedulerEvent, Callable] = {}
        self.__tasks_listeners: dict[str, dict[TaskEvent, Callable]] = {}
        self.__fluent_tasks: dict[str, ITask] = {}
        self.__tasks: dict[str, TaskEntity] = {}
        self.__state: ScheduleStates = ScheduleStates.STOPPED
        self.__running_tasks: set[str] = set()
        self.__paused_tasks: set[str] = set()
        self.__removed_tasks: set[str] = set()
        self.__pending_listener_tasks: set[asyncio.Task] = set()
        self.__shutdown_event = asyncio.Event()
        self.__wait_to_shutdown: float = 0.5

    async def __loadAvailableCommands(self) -> None:
        """
        Retrieve and cache available command signatures from the reactor.

        Queries the reactor for all available jobs/commands and stores their
        signatures in the internal set for quick lookup.

        Returns
        -------
        None
            This method does not return any value. It updates the internal set
            of available command signatures.
        """
        # Return early if command signatures are already cached
        if self.__available_command_signatures:
            return

        # Query the reactor for available commands and cache their signatures
        commands: list[dict] = await self.__reactor.info()
        for job in commands:
            signature = job.get("signature")
            if signature:
                self.__available_command_signatures.add(signature)

    def __suppressApschedulerLogging(self) -> None:
        """
        Disable APScheduler logging to prevent log message interference.

        Set APScheduler component loggers to CRITICAL level and disable message
        propagation to prevent internal scheduler logs from appearing in the
        application's logging output.

        Returns
        -------
        None
            Modifies APScheduler logging configuration in place.
        """
        # Disable main APScheduler logger
        apscheduler_logger = logging.getLogger("apscheduler")
        apscheduler_logger.setLevel(logging.CRITICAL)
        apscheduler_logger.disabled = True
        apscheduler_logger.propagate = False

        # Disable APScheduler executors logger
        executors_logger = logging.getLogger("apscheduler.executors")
        executors_logger.setLevel(logging.CRITICAL)
        executors_logger.disabled = True
        executors_logger.propagate = False

        # Disable APScheduler scheduler logger
        scheduler_logger = logging.getLogger("apscheduler.scheduler")
        scheduler_logger.setLevel(logging.CRITICAL)
        scheduler_logger.disabled = True
        scheduler_logger.propagate = False

    async def __validateAndLoadFluentTasks(self) -> None:
        """
        Validate and load fluent tasks from the internal registry.

        Ensures that all fluent tasks have signatures available in the reactor.
        Populates the internal tasks dictionary with validated task entities.

        Returns
        -------
        None
            This method updates the internal tasks dictionary in place.
        """
        # Validate and load each fluent task
        for signature, task in self.__fluent_tasks.items():
            if signature not in self.__available_command_signatures:
                error_msg = (
                    f"Task signature '{signature}' is not available in the reactor."
                )
                raise ValueError(error_msg)
            self.__tasks[signature] = task.entity()

    async def info(self) -> list[dict]:
        """
        Retrieve information about all loaded fluent tasks.

        Returns
        -------
        list of dict
            A list of dictionaries, each containing details about a loaded task.
        """
        # Ensure available command signatures are loaded before validating tasks
        await self.__loadAvailableCommands()

        # Validate that all fluent tasks have valid signatures and load their entities
        await self.__validateAndLoadFluentTasks()

        data: list[dict] = []
        # Collect details for each fluent task
        for signature, task in self.__tasks.items():
            data.append({
                "signature": signature,
                "args": task.args,
                "purpose": task.purpose,
                "random_delay": task.random_delay,
                "coalesce": task.coalesce,
                "max_instances": task.max_instances,
                "misfire_grace_time": task.misfire_grace_time,
                "start_date": (
                    task.start_date.strftime("%Y-%m-%d %H:%M:%S")
                    if task.start_date else None
                ),
                "end_date": (
                    task.end_date.strftime("%Y-%m-%d %H:%M:%S")
                    if task.end_date else None
                ),
                "details": task.details,
            })

        # Return the collected task details
        return data

    async def _reactorCall(
        self,
        signature: str,
        args: list[str] | None = None,
    ) -> int:
        """
        Execute a reactor command asynchronously.

        Parameters
        ----------
        signature : str
            The command signature to execute.
        args : list of str, optional
            Arguments to pass to the command. Defaults to an empty list.

        Returns
        -------
        int
            The result of the reactor call, typically an exit code or status.

        Notes
        -----
        This method wraps the reactor call for task execution.
        """
        # Call the reactor asynchronously with the provided signature and arguments
        return await self.__reactor.call(signature, args or [])

    def _dispatchSchedulerEventListener(
        self,
        event: APSchedulerEvent,
    ) -> None:
        """
        Call the registered global event listener for a scheduler event.

        Parameters
        ----------
        event : APSchedulerEvent
            The scheduler event that occurred.

        Returns
        -------
        None
            This method does not return a value. It triggers the appropriate
            listener for the event.
        """
        # Retrieve the registered listener for the event code
        listener = self.__scheduler_listeners.get(event.code)
        if not listener:
            return

        # Wrap the event in a SchedulerEventEntity for listener consumption
        event_entity = SchedulerEventEntity(
            code=event.code,
            jobstore=event.alias if hasattr(event, "alias") and event.alias else None,
        )

        # Handle synchronous listeners directly
        if not asyncio.iscoroutinefunction(listener):
            try:
                listener(event_entity)
            except Exception as e:
                Log.error(f"Error executing listener: {e}")
                self.__createManagedTask(self.__handleListenerException(e))
            return

        # Handle asynchronous listeners using an async wrapper
        async def _asyncListenerWrapper() -> None:
            try:
                await listener(event_entity)
            except Exception as e:
                Log.error(f"Error executing listener: {e}")
                await self.__handleListenerException(e)

        # Schedule the async listener wrapper as a managed task
        self.__createManagedTask(_asyncListenerWrapper())

    def _dispatchTaskEventListener(
        self,
        event: APJobEvent,
    ) -> None:
        """
        Dispatch registered task event listener for a specific job event.

        Parameters
        ----------
        event : APJobEvent
            The job event that occurred.

        Returns
        -------
        None
            This method does not return a value. It triggers the appropriate
            listener for the event.
        """
        # Extract the job signature from the event
        signature = event.job_id if hasattr(event, "job_id") else None
        if not signature:
            return

        # Retrieve listeners for this specific task signature
        listener_for_signature = self.__tasks_listeners.get(signature)
        if not listener_for_signature:
            return

        # Retrieve the registered listener for the event code
        listener = listener_for_signature.get(event.code)
        if not listener:
            return

        # Wrap the event in a TaskEventEntity for listener consumption
        event_entity = TaskEventEntity(
            code=event.code,
            signature=getattr(event, "job_id", None),
            jobstore=getattr(event, "jobstore", None),
            scheduled_run_times=getattr(event, "scheduled_run_times", None),
            scheduled_run_time=getattr(event, "scheduled_run_time", None),
            retval=getattr(event, "retval", None),
            exception=getattr(event, "exception", None),
            traceback=getattr(event, "traceback", None),
        )

        # Handle synchronous listeners directly
        if not asyncio.iscoroutinefunction(listener):
            try:
                listener(event_entity)
            except Exception as e:
                Log.error(f"Error executing listener: {e}")
                self.__createManagedTask(self.__handleListenerException(e))
            return

        # Handle asynchronous listeners using an async wrapper
        async def _asyncListenerWrapper() -> None:
            try:
                await listener(event_entity)
            except Exception as e:
                Log.error(f"Error executing listener: {e}")
                await self.__handleListenerException(e)

        # Schedule the async listener wrapper as a managed task
        self.__createManagedTask(_asyncListenerWrapper())

    def __createManagedTask(
        self,
        coroutine: Coroutine,
    ) -> None:
        """
        Create and manage an asyncio task with automatic cleanup.

        Parameters
        ----------
        coroutine : Coroutine
            The coroutine to be executed as an async task.

        Returns
        -------
        None
            This method does not return a value. It manages the lifecycle of
            the created asyncio task.
        """
        # Create and track the async task, ensuring cleanup on completion
        task = asyncio.create_task(coroutine)
        self.__pending_listener_tasks.add(task)
        task.add_done_callback(lambda t: self.__pending_listener_tasks.discard(t))

    async def __handleListenerException(
        self,
        exception: Exception,
    ) -> None:
        """
        Handle exceptions raised in event listeners.

        Parameters
        ----------
        exception : Exception
            The exception raised by the listener.

        Returns
        -------
        None
            This method does not return any value.
        """
        try:
            # Handle the exception using the provided exception handler
            await self.__exception_handler.exception(exception)
        except Exception as handler_error:
            # Log errors that occur within the exception handler itself
            Log.error(f"Error in exception handler: {handler_error}")

    async def boot(self) -> None:
        """
        Boot the scheduler and register all configured tasks.

        Load available command signatures, validate and load fluent tasks,
        initialize the scheduler, register event listeners, and add all jobs
        to the scheduler.

        Returns
        -------
        None
            This method does not return a value but initializes the scheduler.
        """
        # Load available command signatures from the CLI reactor
        await self.__loadAvailableCommands()

        # Validate and load task entities to be registered
        await self.__validateAndLoadFluentTasks()

        # Get the current asyncio event loop for scheduling async tasks
        loop = asyncio.get_running_loop()
        self.__scheduler = AsyncIOScheduler(
            event_loop=loop,
            timezone=LocalDateTime.getZoneinfo(),
        )

        # Add an in-memory jobstore for scheduled tasks
        self.__scheduler.add_jobstore(
            jobstore="memory",
            alias="memory",
        )

        # Register a global event listener to dispatch scheduler events
        self.__scheduler.add_listener(
            self._dispatchSchedulerEventListener,
            (
                SchedulerEvent.STARTED
                | SchedulerEvent.SHUTDOWN
                | SchedulerEvent.PAUSED
                | SchedulerEvent.RESUMED
            ),
        )

        # Register a global event listener to dispatch task events for all jobs
        self.__scheduler.add_listener(
            self._dispatchTaskEventListener,
            (
                TaskEvent.ADDED
                | TaskEvent.REMOVED
                | TaskEvent.MODIFIED
                | TaskEvent.EXECUTED
                | TaskEvent.ERROR
                | TaskEvent.MISSED
                | TaskEvent.SUBMITTED
                | TaskEvent.MAX_INSTANCES
            ),
        )

        # Start the scheduler and update its state
        self.__state = ScheduleStates.RUNNING
        self.__scheduler.start()

        # Register all jobs from the loaded task entities
        for task_entity in self.__tasks.values():

            # Register task-specific event listeners if any are defined
            if task_entity.listeners:
                for callback in task_entity.listeners:
                    event_code, func = callback
                    if task_entity.signature not in self.__tasks_listeners:
                        self.__tasks_listeners[task_entity.signature] = {}
                    self.__tasks_listeners[task_entity.signature][event_code] = func

            # Add the job to the scheduler with all configured parameters
            self.__scheduler.add_job(
                self._reactorCall,
                trigger=task_entity.trigger,
                args=[task_entity.signature, task_entity.args],
                id=task_entity.signature,
                name=task_entity.purpose,
                max_instances=task_entity.max_instances,
                coalesce=task_entity.coalesce,
                misfire_grace_time=task_entity.misfire_grace_time,
                start_date=task_entity.start_date,
                end_date=task_entity.end_date,
                jobstore="memory",
            )
            self.__running_tasks.add(task_entity.signature)

        # Suppress internal APScheduler logging to avoid duplicate logs
        self.__suppressApschedulerLogging()

    def on(
        self,
        event: SchedulerEvent,
        listener: Callable,
    ) -> Self:
        """
        Register a listener for a scheduler event.

        Parameters
        ----------
        event : SchedulerEvent
            The scheduler event to listen for.
        listener : Callable
            The callable to invoke when the event occurs.

        Returns
        -------
        Self
            The Schedule instance for method chaining.

        Raises
        ------
        RuntimeError
            If the scheduler has already been booted.
        TypeError
            If event is not a SchedulerEvent or listener is not callable.
        """
        # Prevent listener registration after scheduler boot
        if not self.isStopped():
            error_msg = (
                "The scheduler has already been booted, cannot register new listeners."
            )
            raise RuntimeError(error_msg)

        # Validate event type
        if not isinstance(event, SchedulerEvent):
            error_msg = "The event must be an instance of SchedulerEvent."
            raise TypeError(error_msg)

        # Validate listener is callable
        if not callable(listener):
            error_msg = "The listener must be a callable."
            raise TypeError(error_msg)

        # Register the event-listener pair for later subscription
        self.__scheduler_listeners[event] = listener
        return self

    def state(self) -> str:
        """
        Return the current scheduler state as a string.

        Returns
        -------
        str
            The current state of the scheduler, e.g., "RUNNING", "PAUSED", or "STOPPED".
        """
        # Return the value of the internal state enum
        return self.__state.value

    def isRunning(self) -> bool:
        """
        Determine if the scheduler is currently running.

        Returns
        -------
        bool
            True if the scheduler state is "RUNNING", otherwise False.
        """
        # Check if the internal state is RUNNING
        return self.__state == ScheduleStates.RUNNING

    def isPaused(self) -> bool:
        """
        Determine if the scheduler is currently paused.

        Returns
        -------
        bool
            True if the scheduler state is "PAUSED", otherwise False.
        """
        # Check if the internal state is PAUSED
        return self.__state == ScheduleStates.PAUSED

    def isStopped(self) -> bool:
        """
        Determine if the scheduler is currently stopped.

        Returns
        -------
        bool
            True if the scheduler state is "STOPPED", otherwise False.
        """
        # Check if the internal state is STOPPED
        return self.__state == ScheduleStates.STOPPED

    def command(
        self,
        signature: str,
        args: list[str] | None = None,
        purpose: str | None = None,
    ) -> ITask:
        """
        Add a command for fluent configuration.

        Parameters
        ----------
        signature : str
            Unique signature of the command to schedule.
        args : list[str] | None, optional
            Arguments for the command. Defaults to None.
        purpose : str | None, optional
            Description of the command's purpose.

        Returns
        -------
        ITask
            Task instance for further configuration.

        Raises
        ------
        RuntimeError
            If the scheduler has already been started.
        TypeError
            If the signature is not a non-empty string or arguments are invalid.
        """
        # Prevent adding new commands after the scheduler has started
        if not self.isStopped():
            error_msg = (
                "The Orionis task scheduler has already been started; "
                "new commands cannot be added."
            )
            raise RuntimeError(error_msg)

        # Validate that the command signature is a non-empty string
        if not isinstance(signature, str) or not signature.strip():
            error_msg = "The command signature must be a non-empty string."
            raise TypeError(error_msg)

        # Ensure arguments are a list of strings or None
        if args is not None:
            if not isinstance(args, list):
                error_msg = (
                    "Arguments must be provided as a list of strings or None."
                )
                raise TypeError(error_msg)
            for arg in args:
                if not isinstance(arg, str):
                    error_msg = "Each argument must be a string."
                    raise TypeError(error_msg)

        # Store the Task instance for fluent configuration
        self.__fluent_tasks[signature] = Task(
            signature,
            args or [],
            purpose,
        )
        return self.__fluent_tasks[signature]

    def pauseTask(
        self,
        signature: str,
    ) -> bool:
        """
        Pause a running task by its signature.

        Parameters
        ----------
        signature : str
            Unique identifier of the task to pause.

        Returns
        -------
        bool
            True if the task was successfully paused, otherwise raises an exception.

        Raises
        ------
        RuntimeError
            If the scheduler has not been started or the task is not running.
        ValueError
            If the specified task does not exist.

        Notes
        -----
        This method pauses a running task in the scheduler.
        """
        # Ensure the scheduler is initialized before pausing a task
        if not self.__scheduler:
            error_msg = self._SCHEDULER_NOT_STARTED_ERROR
            raise RuntimeError(error_msg)

        # Check if the task is currently running
        if signature not in self.__running_tasks:
            error_msg = (
                f"Task '{signature}' is not currently running and cannot be paused."
            )
            raise RuntimeError(error_msg)

        # Retrieve the job from the scheduler and pause it
        job = self.__scheduler.get_job(signature)
        if not job:
            error_msg = f"Task '{signature}' does not exist."
            raise ValueError(error_msg)

        # Pause the job and update internal state
        try:
            self.__scheduler.pause_job(signature)
            self.__running_tasks.remove(signature)
            self.__paused_tasks.add(signature)
            Log.info(f"Task '{signature}' paused.")
            return True
        except Exception as e:
            error_msg = f"Failed to pause task '{signature}': {e!s}"
            Log.error(error_msg)
            raise RuntimeError(error_msg) from e

    def resumeTask(
        self,
        signature: str,
    ) -> bool:
        """
        Resume a paused task by its signature.

        Parameters
        ----------
        signature : str
            Unique identifier of the task to resume.

        Returns
        -------
        bool
            True if the task was successfully resumed, otherwise raises an exception.

        Raises
        ------
        RuntimeError
            If the scheduler has not been started or the task is not paused.
        ValueError
            If the specified task does not exist.

        Notes
        -----
        This method resumes a paused task in the scheduler.
        """
        # Ensure the scheduler is initialized before resuming a task
        if not self.__scheduler:
            error_msg = self._SCHEDULER_NOT_STARTED_ERROR
            raise RuntimeError(error_msg)

        # Check if the task is currently paused
        if signature not in self.__paused_tasks:
            error_msg = (
                f"Task '{signature}' is not currently paused and cannot be resumed."
            )
            raise RuntimeError(error_msg)

        # Retrieve the job from the scheduler and resume it
        job = self.__scheduler.get_job(signature)
        if not job:
            error_msg = f"Task '{signature}' does not exist."
            raise ValueError(error_msg)

        # Resume the job and update internal state
        try:
            self.__scheduler.resume_job(signature)
            self.__paused_tasks.remove(signature)
            self.__running_tasks.add(signature)
            Log.info(f"Task '{signature}' resumed.")
            return True
        except Exception as e:
            error_msg = f"Failed to resume task '{signature}': {e!s}"
            Log.error(error_msg)
            raise RuntimeError(error_msg) from e

    def removeTask(
        self,
        signature: str,
    ) -> bool:
        """
        Remove a task from the scheduler by its signature.

        Parameters
        ----------
        signature : str
            Unique identifier of the task to remove.

        Returns
        -------
        bool
            True if the task was successfully removed, otherwise raises an exception.

        Raises
        ------
        RuntimeError
            If the scheduler has not been started or the task is not found.
        ValueError
            If the specified task does not exist.

        Notes
        -----
        This method removes a task from the scheduler and updates internal state.
        """
        # Ensure the scheduler is initialized before removing a task
        if not self.__scheduler:
            error_msg = self._SCHEDULER_NOT_STARTED_ERROR
            raise RuntimeError(error_msg)

        # Check if the task exists in either running or paused state
        if (
            signature not in self.__running_tasks and
            signature not in self.__paused_tasks
        ):
            error_msg = f"Task '{signature}' does not exist and cannot be removed."
            raise RuntimeError(error_msg)

        # Retrieve the job from the scheduler and remove it
        job = self.__scheduler.get_job(signature)
        if not job:
            error_msg = f"Task '{signature}' does not exist."
            raise ValueError(error_msg)

        try:
            self.__scheduler.remove_job(signature)
            self.__running_tasks.discard(signature)
            self.__paused_tasks.discard(signature)
            self.__removed_tasks.add(signature)
            Log.info(f"Task '{signature}' removed.")
            return True
        except Exception as e:
            error_msg = f"Failed to remove task '{signature}': {e!s}"
            Log.error(error_msg)
            raise RuntimeError(error_msg) from e

    def removeAllTasks(self) -> bool:
        """
        Remove all tasks from the scheduler.

        Returns
        -------
        bool
            True if all tasks were successfully removed, otherwise raises an exception.

        Raises
        ------
        RuntimeError
            If the scheduler has not been started or an error occurs during removal.

        Notes
        -----
        This method removes all tasks from the scheduler and updates internal state.
        """
        # Ensure the scheduler is initialized before removing tasks
        if not self.__scheduler:
            error_msg = self._SCHEDULER_NOT_STARTED_ERROR
            raise RuntimeError(error_msg)

        try:
            self.__scheduler.remove_all_jobs()
            self.__running_tasks.clear()
            self.__paused_tasks.clear()
            self.__removed_tasks.update(self.__tasks.keys())
            Log.info("All tasks removed from the scheduler.")
            return True
        except Exception as e:
            error_msg = f"Failed to remove all tasks: {e!s}"
            Log.error(error_msg)
            raise RuntimeError(error_msg) from e

    def pause(self) -> bool:
        """
        Pause the scheduler if it is running.

        Parameters
        ----------
        self : Schedule
            The Schedule instance.

        Returns
        -------
        bool
            True if the scheduler was successfully paused.

        Raises
        ------
        RuntimeError
            If the scheduler is not started or not running.
        """
        # Ensure the scheduler is initialized before pausing
        if not self.__scheduler:
            error_msg = self._SCHEDULER_NOT_STARTED_ERROR
            raise RuntimeError(error_msg)

        # Ensure the scheduler is running before attempting to pause
        if not self.isRunning():
            error_msg = "The task scheduler is not running and cannot be paused."
            raise RuntimeError(error_msg)

        try:
            self.__scheduler.pause()
            self.__state = ScheduleStates.PAUSED
            Log.info("Scheduler paused.")
            return True
        except Exception as e:
            error_msg = f"Failed to pause the scheduler: {e!s}"
            Log.error(error_msg)
            raise RuntimeError(error_msg) from e

    def resume(self) -> bool:
        """
        Resume the scheduler if it is paused.

        Parameters
        ----------
        self : Schedule
            The Schedule instance.

        Returns
        -------
        bool
            True if the scheduler was successfully resumed.

        Raises
        ------
        RuntimeError
            If the scheduler is not started or not paused.
        """
        # Ensure the scheduler is initialized before resuming
        if not self.__scheduler:
            error_msg = self._SCHEDULER_NOT_STARTED_ERROR
            raise RuntimeError(error_msg)

        # Ensure the scheduler is paused before attempting to resume
        if not self.isPaused():
            error_msg = "The task scheduler is not paused and cannot be resumed."
            raise RuntimeError(error_msg)

        try:
            self.__scheduler.resume()
            self.__state = ScheduleStates.RUNNING
            Log.info("Scheduler resumed.")
            return True
        except Exception as e:
            error_msg = f"Failed to resume the scheduler: {e!s}"
            Log.error(error_msg)
            raise RuntimeError(error_msg) from e

    def shutdown(self, wait: int | None = None) -> None:
        """
        Shut down the task scheduler safely without waiting for running tasks.

        This method terminates the scheduler execution safely. It does not wait
        for currently executing tasks to complete, but prevents new tasks from
        starting and cleans up scheduler resources. Ideal for console
        environments where the process stops immediately after calling this
        method.

        Parameters
        ----------
        wait : int | None, optional
            Time in seconds to wait before completing shutdown. Defaults to None.

        Returns
        -------
        None
            This method does not return a value. It initiates graceful shutdown.
        """
        # Set the wait time for graceful shutdown process
        self.__wait_to_shutdown = wait if isinstance(wait, int) and wait >= 0 else 0

        # Create and execute the shutdown task asynchronously
        self.__createManagedTask(self.__gracefulShutdown())

    async def __gracefulShutdown(self) -> None:
        """
        Execute graceful shutdown of the scheduler without blocking.

        This method runs the scheduler shutdown in a thread executor to avoid
        blocking the event loop, then sets the shutdown event to notify any
        waiting tasks that shutdown is complete.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Get the current event loop for executing shutdown in a separate thread
        loop = asyncio.get_running_loop()

        # Sleep briefly to allow any pending tasks to complete cleanup
        # before signaling shutdown completion
        await asyncio.sleep(self.__wait_to_shutdown)

        # Execute scheduler shutdown without blocking the main thread
        await loop.run_in_executor(
            None,
            lambda: self.__scheduler.shutdown(wait=True),
        )

        # Signal that shutdown is complete
        self.__shutdown_event.set()

    async def wait(self) -> None:
        """
        Wait for the scheduler shutdown to complete.

        This method blocks until the shutdown process initiated by the shutdown()
        method has finished. It provides a way to synchronize with the graceful
        shutdown process.

        Returns
        -------
        None
            This method does not return a value but blocks until shutdown
            completes.
        """
        # Wait for the shutdown event to be set by the graceful shutdown process
        await self.__shutdown_event.wait()
