from __future__ import annotations
import asyncio
import logging
import os
from typing import Any, TYPE_CHECKING
from zoneinfo import ZoneInfo
from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MAX_INSTANCES,
    EVENT_JOB_MISSED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_SUBMITTED,
    EVENT_SCHEDULER_PAUSED,
    EVENT_SCHEDULER_RESUMED,
    EVENT_SCHEDULER_SHUTDOWN,
    EVENT_SCHEDULER_STARTED,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler as APSAsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler, STATE_PAUSED, STATE_RUNNING
from apscheduler.triggers.date import DateTrigger
from rich.panel import Panel
from rich.text import Text
from orionis.console.contracts.schedule import ISchedule
from orionis.console.contracts.schedule_event_listener import IScheduleEventListener
from orionis.console.entities.event_job import EventJob
from orionis.console.entities.scheduler_error import SchedulerError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted
from orionis.console.enums.listener import ListeningEvent
from orionis.console.fluent.event import Event
from orionis.console.request.cli_request import CLIRequest
from orionis.failure.enums.kernel_type import KernelType
from orionis.support.time.local import LocalDateTime

if TYPE_CHECKING:
    from datetime import datetime
    from rich.console import Console
    from orionis.console.contracts.event import IEvent
    from orionis.console.contracts.reactor import IReactor
    from orionis.console.entities.event import Event as EventEntity
    from orionis.failure.contracts.catch import ICatch
    from orionis.foundation.contracts.application import IApplication
    from orionis.services.log.contracts.log_service import ILogger

class Schedule(ISchedule):

    # ruff: noqa: BLE001, TRY400

    # List of control operations for the scheduler
    CONTROL_OPERATIONS: tuple[str, ...] = (
        "schedule:pause",
        "schedule:resume",
        "schedule:shutdown",
    )

    # Error message constants
    SIGNATURE_REQUIRED_ERROR = "Signature must be a non-empty string."
    NOT_APPLICABLE = "Not Applicable"

    def __init__(
        self,
        reactor: IReactor,
        app: IApplication,
        rich_console: Console,
        logger: ILogger,
        catch: ICatch,
    ) -> None:
        """
        Initialize Schedule instance with dependencies and internal state.

        Set up the scheduler, timezone, logger, reactor, available commands,
        event tracking, listeners, and exception handling. Prepare all required
        internal structures for scheduling and event handling.

        Parameters
        ----------
        reactor : IReactor
            Reactor for command management and job execution.
        app : IApplication
            Application container for configuration and services.
        rich_console : Console
            Rich Console instance for output formatting.
        logger : ILogger
            Logger instance for logging.
        catch : ICatch
            Exception handler.

        Returns
        -------
        None
            This method always returns None.
        """
        # Store application instance for config and services
        self.__app: IApplication = app

        # Store rich console for output formatting
        self.__rich_console = rich_console

        # Set timezone from application config or default to UTC
        self.__tz = ZoneInfo(self.__app.config("app.timezone") or "UTC")

        # Initialize main and control AsyncIOScheduler with timezone
        self.__scheduler = APSAsyncIOScheduler(timezone=self.__tz)
        self.__control_scheduler = APSAsyncIOScheduler(timezone=self.__tz)

        # Suppress APScheduler internal logging
        self.__suppressApschedulerLogging()

        # Initialize logger
        self.__logger = logger

        # Store reactor for command management
        self.__reactor = reactor

        # Retrieve available commands from reactor
        self.__available_commands = self.__getAvailableCommands()

        # Initialize scheduled events dictionary
        self.__events: dict[str, IEvent] = {}

        # Initialize scheduled job entities list
        self.__jobs: list[EventEntity] = []

        # Initialize event listeners dictionary
        self.__listeners: dict[str, callable] = {}

        # Initialize asyncio event for scheduler shutdown signaling
        self._stopEvent: asyncio.Event | None = None

        # Store exception handler
        self.__catch = catch

        # Initialize paused timestamp
        self.__paused_at: datetime | None = None

        # Initialize cache for event entities
        self.__cache_scheduled_jobs: dict = {}

        # Store datetime contract for time operations
        self.__datetime = LocalDateTime

    def __suppressApschedulerLogging(self) -> None:
        """
        Suppress APScheduler logging.

        Disable logging for APScheduler and its main subcomponents to avoid duplicate or
        conflicting log messages. This method clears all handlers, disables propagation,
        and turns off the loggers. It is useful when the application manages its own
        logging configuration.

        Returns
        -------
        None
            This method always returns None. It modifies the logging configuration of
            APScheduler loggers in place.
        """
        # List of APScheduler logger names to disable
        for name in [
            "apscheduler",
            "apscheduler.scheduler",
            "apscheduler.executors.default",
        ]:
            # Retrieve the logger by name
            logger = logging.getLogger(name)

            # Remove all handlers to prevent output
            logger.handlers.clear()

            # Prevent log messages from propagating to ancestor loggers
            logger.propagate = False

            # Disable the logger entirely
            logger.disabled = True

    def __getAvailableCommands(self) -> dict:
        """
        Retrieve available commands from the reactor as a dictionary.

        Query the reactor for all available jobs/commands, extracting their
        signatures and descriptions. Return a dictionary where each key is the
        command signature and the value is a dictionary with the command's
        signature and description.

        Returns
        -------
        dict
            Dictionary mapping command signatures to their details. Each value is a
            dictionary with 'signature' and 'description' keys.
        """
        # Initialize the commands dictionary
        commands = {}

        # Iterate over all jobs provided by the reactor's info method
        for job in self.__reactor.info():

            # Extract the command signature
            signature: str = job.get("signature", None)

            # Skip invalid or special method signatures
            if not signature or (
                signature.startswith("__") and signature.endswith("__")
            ):
                continue

            # Extract the command description, defaulting if not provided
            description: str = job.get("description", "No description available.")

            # Store each job's signature and description in the commands dictionary
            commands[signature] = {
                "signature": signature,
                "description": description,
            }

        # Return the commands dictionary
        return commands

    def __getFormattedNow(self) -> str:
        """
        Format and return the current datetime as a string.

        Get the current timezone-aware datetime and format it as a string in
        'YYYY-MM-DD HH:MM:SS' format.

        Returns
        -------
        str
            The formatted current datetime string.
        """
        # Get the current datetime and format it as a string
        return self.__getCurrentTime().strftime("%Y-%m-%d %H:%M:%S")

    def __getCurrentTime(self) -> datetime:
        """
        Return the current timezone-aware datetime.

        Get the current date and time localized to the scheduler's configured timezone.
        This ensures all time operations are consistent with the application's timezone.

        Returns
        -------
        datetime
            The current timezone-aware datetime object.
        """
        # Return the current datetime using the scheduler's timezone
        return self.__datetime.now()

    def __safeGetAttr(
        self,
        obj: type[Any],
        attr: str,
        default: type[Any] | None = None,
    ) -> type[Any]:
        """
        Retrieve attribute value or return default if not present.

        Attempt to access the specified attribute of the given object. If the attribute
        exists, return its value. If not, return the provided default value. This avoids
        raising an AttributeError for missing attributes.

        Parameters
        ----------
        obj : Any
            Object from which to retrieve the attribute.
        attr : str
            Name of the attribute to retrieve.
        default : Any, optional
            Value to return if the attribute does not exist. Default is None.

        Returns
        -------
        Any
            Value of the attribute if it exists, otherwise the default value.
        """
        # Return the default value if the object is None or lacks the attribute
        if obj is None:
            return default

        # Use hasattr to check if the attribute exists
        if hasattr(obj, attr):
            return getattr(obj, attr)

        # Return the default value if the attribute is not found
        return default

    def __isCommandRegistered(self, signature: str) -> bool:
        """
        Check if a command exists in the registered commands.

        Parameters
        ----------
        signature : str
            Command signature to check.

        Returns
        -------
        bool
            True if the command exists in the available commands dictionary,
            otherwise False.
        """
        # Check if the signature exists in the available commands dictionary
        return signature in self.__available_commands

    def __getCommandDescription(self, signature: str) -> str | None:
        """
        Get the description for a command by its signature.

        Search the internal available commands dictionary for the given signature and
        return its description if found. If the signature does not exist, return None.

        Parameters
        ----------
        signature : str
            Unique signature identifying the command.

        Returns
        -------
        str or None
            Description string if found, otherwise None.
        """
        # Retrieve the command entry from the available commands dictionary
        command_entry = self.__available_commands.get(signature)

        # Return the description if the command exists, otherwise None
        return command_entry["description"] if command_entry else None

    def __getProcessID(self) -> int:
        """
        Get the current process ID (PID).

        Use the `os` module to retrieve the PID of the running Python process.
        This is useful for logging and monitoring the scheduler process.

        Returns
        -------
        int
            The process ID (PID) of the current Python process.
        """
        # Return the current process ID using os.getpid()
        return os.getpid()

    def __subscribeListeners(self) -> None:
        """
        Subscribe internal handlers to APScheduler events.

        Attach internal listener methods to the AsyncIOScheduler for various scheduler
        and job-related events. This enables the scheduler to respond to lifecycle
        changes and job execution events.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Register listener for scheduler start event
        self.__scheduler.add_listener(
            self.__startedListener, EVENT_SCHEDULER_STARTED,
        )

        # Register listener for scheduler shutdown event
        self.__scheduler.add_listener(
            self.__shutdownListener, EVENT_SCHEDULER_SHUTDOWN,
        )

        # Register listener for job execution errors
        self.__scheduler.add_listener(
            self.__errorListener, EVENT_JOB_ERROR,
        )

        # Register listener for job submission to executor
        self.__scheduler.add_listener(
            self.__submittedListener, EVENT_JOB_SUBMITTED,
        )

        # Register listener for job execution completion
        self.__scheduler.add_listener(
            self.__executedListener, EVENT_JOB_EXECUTED,
        )

        # Register listener for missed job execution
        self.__scheduler.add_listener(
            self.__missedListener, EVENT_JOB_MISSED,
        )

        # Register listener for max concurrent job instances exceeded
        self.__scheduler.add_listener(
            self.__maxInstancesListener, EVENT_JOB_MAX_INSTANCES,
        )

        # Register listener for job removal from scheduler
        self.__scheduler.add_listener(
            self.__removedListener, EVENT_JOB_REMOVED,
        )

    def __ensureListeningEvent(self, listening_vent: ListeningEvent) -> None:
        """
        Ensure that the provided event is an instance of ListeningEvent.

        Parameters
        ----------
        listening_vent : ListeningEvent
            The event to validate.

        Returns
        -------
        None
            Raises TypeError if the event is not a ListeningEvent.

        Raises
        ------
        TypeError
            If listening_vent is not an instance of ListeningEvent.
        """
        # Validate that the event is a ListeningEvent instance
        if not isinstance(listening_vent, ListeningEvent):
            error_msg = "The event must be an instance of ListeningEvent."
            raise TypeError(error_msg)

    def __ensureValidEventDataType(
        self,
        event_data: (
            SchedulerStarted
            | SchedulerPaused
            | SchedulerResumed
            | SchedulerShutdown
            | SchedulerError
            | EventJob
        ),
    ) -> None:
        """
        Validate that event_data is an instance of allowed event types.

        Parameters
        ----------
        event_data : SchedulerStarted or SchedulerPaused or SchedulerResumed or
            SchedulerShutdown or SchedulerError or EventJob
            Event data to validate.

        Returns
        -------
        None
            Raises TypeError if event_data is not an allowed type.

        Raises
        ------
        TypeError
            If event_data is not an instance of the allowed types.
        """
        # Define allowed event types for validation
        valid_types = (
            SchedulerStarted,
            SchedulerPaused,
            SchedulerResumed,
            SchedulerShutdown,
            SchedulerError,
            EventJob,
        )

        # Check if event_data is an instance of any allowed type
        if not isinstance(event_data, valid_types):
            error_msg = (
                "The event data must be an instance of SchedulerStarted, "
                "SchedulerPaused, SchedulerResumed, SchedulerShutdown, "
                "SchedulerError, or EventJob."
            )
            raise TypeError(error_msg)

        # Additional check for EventJob to ensure it has a non-empty 'id' attribute
        if (
            isinstance(event_data, EventJob)
            and (not hasattr(event_data, "id") or not event_data.id)
        ):
            error_msg = "EventJob must have a non-empty 'id' attribute."
            raise TypeError(error_msg)

    def __handleException(
        self,
        exception: BaseException,
        command: str = "schedule:work",
    ) -> None:
        """
        Delegate exception to the application's error catching system.

        Centralize exception handling by forwarding the exception to the application's
        error catching mechanism. This ensures consistent error processing according to
        the application's global policies.

        Parameters
        ----------
        exception : BaseException
            Exception instance raised during scheduler or command execution.
        command : str, optional
            Command context for the CLIRequest, by default "schedule:work".

        Returns
        -------
        None
            This method does not return any value. The exception is delegated to the
            application's error handling system.
        """
        # Create a CLIRequest object representing the current scheduler context.
        request = CLIRequest(command)

        # Delegate the exception to the application's error catching system.
        self.__catch.exception(KernelType.CONSOLE, request, exception)

    def __getEventJobDetailsById(
        self,
        job_id: str,
        code: int | None = None,
    ) -> EventJob | None:
        """
        Retrieve a scheduled job entity by its unique ID.

        Fetch a job from the AsyncIOScheduler using its unique identifier. Extract
        relevant attributes and create an `EventJob` entity with the details. If the
        job does not exist, return an empty `EventJob` or `None` as appropriate.

        Parameters
        ----------
        job_id : str
            Unique identifier of the job to retrieve.
        code : int or None, optional
            Event code associated with the job, by default None.

        Returns
        -------
        EventJob or None
            An `EventJob` entity with job details if found, otherwise an empty
            `EventJob` or `None`.
        """
        # Extract event data from the internal events list if available
        event_data: dict = self.getScheduledJobDetails(job_id)

        # Retrieve the job data from the scheduler using the provided job ID
        data = self.__scheduler.get_job(job_id)

        # Get the job ID safely
        _id = self.__safeGetAttr(data, "id", None)

        # Handle special cases for missed or removed jobs
        if not _id and code in (EVENT_JOB_MISSED, EVENT_JOB_REMOVED):
            _id = event_data.get("signature")

        # If the job ID is still not found, return an empty EventJob
        elif not _id:
            return EventJob()

        # Extract job attributes with safe defaults
        _code = code if code is not None else 0
        _name = self.__safeGetAttr(data, "name", None)
        _func = self.__safeGetAttr(data, "func", None)
        _args = self.__safeGetAttr(data, "args", tuple(event_data.get("args", [])))
        _trigger = self.__safeGetAttr(data, "trigger", None)
        _executor = self.__safeGetAttr(data, "executor", None)
        _jobstore = self.__safeGetAttr(data, "jobstore", None)
        _misfire_grace_time = self.__safeGetAttr(data, "misfire_grace_time", None)
        _max_instances = self.__safeGetAttr(data, "max_instances", 1)
        _coalesce = self.__safeGetAttr(data, "coalesce", default=False)
        _next_run_time = self.__safeGetAttr(data, "next_run_time", None)
        _purpose = event_data.get("purpose")
        _start_date = event_data.get("start_date")
        _end_date = event_data.get("end_date")
        _details = event_data.get("details")

        # Return an EventJob entity with the extracted attributes
        return EventJob(
            id=_id,
            code=_code,
            name=_name,
            func=_func,
            args=_args,
            trigger=_trigger,
            executor=_executor,
            jobstore=_jobstore,
            misfire_grace_time=_misfire_grace_time,
            max_instances=_max_instances,
            coalesce=_coalesce,
            next_run_time=_next_run_time,
            exception=None,
            traceback=None,
            retval=None,
            purpose=_purpose,
            start_date=_start_date,
            end_date=_end_date,
            details=_details,
        )

    def __globalCallableListener(
        self,
        event_data: (
            SchedulerStarted
            | SchedulerPaused
            | SchedulerResumed
            | SchedulerShutdown
            | SchedulerError
        ),
        listening_vent: ListeningEvent,
    ) -> None:
        """
        Invoke the registered global listener for a scheduler event.

        Validate the event type and check for a registered listener. If present,
        call the listener with the event data and scheduler instance. Raise a
        TypeError if the event is not a ListeningEvent or if the listener is not
        callable.

        Parameters
        ----------
        event_data : SchedulerStarted or SchedulerPaused or SchedulerResumed or
            SchedulerShutdown or SchedulerError
            Event data associated with the scheduler event.
        listening_vent : ListeningEvent
            Enum value representing the scheduler event.

        Returns
        -------
        None
            Always returns None. No value is returned.
        """
        try:

            # Ensure the event is a ListeningEvent instance
            self.__ensureListeningEvent(listening_vent)

            # Validate that event_data is of an allowed type
            self.__ensureValidEventDataType(event_data)

            # Check if a listener is registered for this global event
            if (
                listening_vent.value in self.__listeners
                and self.__listeners[listening_vent.value] is not None
            ):
                # Retrieve the listener callable for the event
                listener = self.__listeners[listening_vent.value]

                # If the listener is callable, invoke it with event data and scheduler
                if callable(listener):

                    # Use the application container to invoke the listener
                    self.__app.invoke(
                        listener,
                        event=event_data,
                        schedule=self,
                    )

                else:

                    # Raise an error if the listener is not callable
                    error_msg = (
                        f"The listener for event '{listening_vent.value}' "
                        "must be callable."
                    )
                    raise TypeError(error_msg)

        except Exception as e:

            # Handle any exceptions raised during listener invocation
            self.__handleException(e)

    def __taskCallableListener(
        self,
        event_data: EventJob,
        listening_vent: ListeningEvent,
    ) -> None:
        """
        Invoke the registered listener for a specific job event.

        This method handles job-specific events such as errors, executions, and
        submissions. It checks if a listener is registered for the job ID and
        invokes the appropriate method on the listener. The listener can be a
        class implementing `IScheduleEventListener` or a callable.

        Parameters
        ----------
        event_data : EventJob
            Event data associated with the job event, including job ID and context.
        listening_vent : ListeningEvent
            Enum instance representing the job event type.

        Returns
        -------
        None
            This method does not return any value. It invokes the listener if found.

        Raises
        ------
        Exception
            Any exception raised during listener invocation is handled internally.
        """
        # Fallback command signature for error handling context
        command = "schedule:work"

        try:

            # Ensure the event is a valid ListeningEvent
            self.__ensureListeningEvent(listening_vent)

            # Validate that event_data is a valid EventJob with a non-empty id
            self.__ensureValidEventDataType(event_data)

            # Get the string identifier for the event from the ListeningEvent enum
            scheduler_event = listening_vent.value

            # Store the signature of the command associated with the event
            command = event_data.id

            # Check if a listener is registered for this job ID
            if command in self.__listeners:

                # Retrieve the listener for the job ID
                listener = self.__listeners[command]

                # If the listener is a subclass of IScheduleEventListener
                if issubclass(listener, IScheduleEventListener):

                    # If the listener is a class, instantiate it using the app container
                    if isinstance(listener, type):
                        listener = self.__app.build(listener)

                    # If the listener has the event method and it is callable, invoke it
                    if hasattr(listener, scheduler_event) and callable(
                        getattr(listener, scheduler_event),
                    ):
                        self.__app.call(
                            listener,
                            scheduler_event,
                            event=event_data,
                            schedule=self,
                        )

                else:

                    # Raise an error if the listener is not a subclass
                    # of IScheduleEventListener
                    error_msg = (
                        f"The listener for command '{command}' must be a subclass"
                        " of IScheduleEventListener."
                    )
                    raise ValueError(error_msg)

        except Exception as e:

            # Handle any exceptions raised during listener invocation
            self.__handleException(e, command)

    def __startedListener(self, event: type[Any]) -> None:
        """
        Handle the scheduler started event and invoke registered listeners.

        Display a formatted message on the rich console when the scheduler starts.
        Log the start event and timezone. Invoke any registered listener for the
        scheduler started event.

        Parameters
        ----------
        event
            Event object with details about the scheduler start.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Get the current time in the configured timezone
        now = self.__getFormattedNow()

        # Display a start message for the scheduler worker on the rich console
        self.__rich_console.line()
        panel_content = Text.assemble(
            ("🚀 Orionis Scheduler Worker ", "bold white on green"),
            ("\n\n", ""),
            ("✅ The scheduled tasks worker has started successfully.\n", "white"),
            (
                f"🕒 Started at: {now} | "
                f"🌐 Timezone: {self.__tz.key} | "
                f"🆔 PID: {self.__getProcessID()}\n",
                "dim",
            ),
            ("🛑 To stop the worker, press ", "white"),
            ("Ctrl+C", "bold yellow"),
        )

        # Print the message in a styled panel
        self.__rich_console.print(
            Panel(
                panel_content,
                border_style="green",
                padding=(1, 2),
            ),
        )

        # Print a separating line
        self.__rich_console.line()

        # Prepare event data for the listener
        event_data = SchedulerStarted(
            code=self.__safeGetAttr(event, "code", 0),
            time=self.__getCurrentTime(),
        )

        # Invoke the global listener for the scheduler started event
        self.__globalCallableListener(
            event_data,
            ListeningEvent.SCHEDULER_STARTED,
        )

        # Log the scheduler start
        log_msg = f"Orionis Scheduler started successfully at: {now}."
        self.__logger.info(log_msg)

        # Log the timezone assigned to the scheduler
        log_msg = f"Timezone assigned to the scheduler: {self.__tz.key}."
        self.__logger.info(log_msg)

    def __shutdownListener(self, event: type[Any]) -> None:
        """
        Handle the scheduler shutdown event and invoke registered listeners.

        Create an event data object for the scheduler shutdown, invoke any registered
        global listener for the shutdown event, and log the shutdown time.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Prepare event data for the scheduler shutdown
        event_data = SchedulerShutdown(
            code=self.__safeGetAttr(event, "code", 0),
            time=self.__getCurrentTime(),
        )

        # Invoke the global listener for the scheduler shutdown event if registered
        self.__globalCallableListener(
            event_data,
            ListeningEvent.SCHEDULER_SHUTDOWN,
        )

        # Log the scheduler shutdown with the current formatted time
        log_msg = (
            "Orionis Scheduler shut down successfully at: "
            f"{self.__getFormattedNow()}."
        )
        self.__logger.info(log_msg)

    def __errorListener(self, event: type[Any]) -> None:
        """
        Handle job error events and invoke listeners.

        Log error details, update job event data with error information, and invoke
        registered listeners for both the specific job error and the global scheduler
        error event. Delegate exception handling to the application's error catching
        mechanism.

        Parameters
        ----------
        event
            Event object with details about the errored job, including its ID,
            exception, traceback, and event code.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Extract job ID, event code, exception, and traceback from the event object
        event_id = self.__safeGetAttr(event, "job_id", None)
        event_code = self.__safeGetAttr(event, "code", 0)
        event_exception = self.__safeGetAttr(event, "exception", None)
        event_traceback = self.__safeGetAttr(event, "traceback", None)

        # Retrieve the job event data and update it with error details
        job_event_data = self.__getEventJobDetailsById(event_id)
        job_event_data.code = event_code
        job_event_data.exception = event_exception
        job_event_data.traceback = event_traceback

        # Invoke the task-specific listener for job errors, if registered
        self.__taskCallableListener(job_event_data, ListeningEvent.JOB_ON_FAILURE)

        # Prepare the global scheduler error event data
        event_data = SchedulerError(
            code=event_code,
            time=self.__getCurrentTime(),
            exception=event_exception,
            traceback=event_traceback,
        )

        # Invoke the global listener for scheduler errors, if registered
        self.__globalCallableListener(event_data, ListeningEvent.SCHEDULER_ERROR)

    def __submittedListener(self, event: type[Any]) -> None:
        """
        Handle job submission event and invoke registered listeners.

        This method is triggered when a job is submitted to its executor by the
        scheduler. It logs the submission, creates an event entity for the job,
        and invokes any registered listeners for the submitted job. This allows
        for custom pre-execution logic or notifications.

        Parameters
        ----------
        event
            Event object containing details about the submitted job, such as its
            ID and event code.

        Returns
        -------
        None
            This method does not return any value. It performs logging and
            invokes any registered listener for the job submission event.

        Notes
        -----
        The method ensures that job submissions are logged and that any custom
        listeners associated with the job are notified.
        """
        # Extract job ID and code from the event object, using default
        # values if not present
        event_id = self.__safeGetAttr(event, "job_id", None)
        event_code = self.__safeGetAttr(event, "code", 0)

        # Create an event entity for the submitted job, including its ID and code
        data_event = self.__getEventJobDetailsById(event_id, event_code)

        # If a listener is registered for this job ID, invoke the listener
        # with the event details
        self.__taskCallableListener(data_event, ListeningEvent.JOB_BEFORE)

    def __executedListener(self, event: type[Any]) -> None:
        """
        Handle job execution events and invoke listeners.

        Log job execution, report errors, and notify listeners for the executed job.
        Extract job details and trigger the corresponding listener if registered.

        Parameters
        ----------
        event
            Event object with job execution details.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Extract job ID and event code from the event object
        event_id = self.__safeGetAttr(event, "job_id", None)
        event_code = self.__safeGetAttr(event, "code", 0)

        # Create an event entity for the executed job
        data_event = self.__getEventJobDetailsById(event_id, event_code)

        # Invoke the listener for this job if registered
        self.__taskCallableListener(data_event, ListeningEvent.JOB_AFTER)

    def __missedListener(self, event: type[Any]) -> None:
        """
        Handle missed job events and invoke registered listeners.

        Extract the job ID and event code from the event object. Create an event
        entity for the missed job and invoke any registered listeners for the missed
        job event. Log and report missed executions to ensure custom logic is executed.

        Parameters
        ----------
        event
            Event object containing details about the missed job, including its ID,
            event code, and scheduled run time.

        Returns
        -------
        None
            Always returns None. No value is returned.
        """
        # Extract the job ID from the event object, or None if not present
        event_id = self.__safeGetAttr(event, "job_id", None)

        # Extract the event code from the event object, defaulting to 0 if not present
        event_code = self.__safeGetAttr(event, "code", 0)

        # Create an event entity for the missed job, including its ID and code
        data_event = self.__getEventJobDetailsById(event_id, event_code)

        # If a listener is registered for this job ID
        # invoke the listener with the event details
        self.__taskCallableListener(data_event, ListeningEvent.JOB_ON_MISSED)

    def __maxInstancesListener(self, event: type[Any]) -> None:
        """
        Handle job max instances event and invoke registered listeners.

        Triggered when a job exceeds its allowed concurrent instances. Log an error,
        create an event entity for the affected job, and invoke any registered
        listener for this job's max instances event.

        Parameters
        ----------
        event
            Event object with job ID and event code.

        Returns
        -------
        None
            Always returns None. No value is returned.

        Notes
        -----
        This method is for internal use to centralize handling of job max instances
        events.
        """
        # Extract job ID and event code from the event object
        event_id = self.__safeGetAttr(event, "job_id", None)
        event_code = self.__safeGetAttr(event, "code", 0)

        # Create an event entity for the job that exceeded max instances
        data_event = self.__getEventJobDetailsById(event_id, event_code)

        # Invoke the listener for this job's max instances event if registered
        self.__taskCallableListener(data_event, ListeningEvent.JOB_ON_MAXINSTANCES)

    def __removedListener(self, event: type[Any]) -> None:
        """
        Handle job removal event and invoke registered listeners.

        Retrieve the job ID and event code from the event object. Log the removal
        of the job and create an event entity for the removed job. If a listener
        is registered for the job, invoke the listener with the event details.

        Parameters
        ----------
        event : JobRemoved
            Event object containing details about the removed job.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        - Retrieves job ID and event code from the event object.
        - Logs the removal of the job.
        - Invokes the registered listener for the removed job event.
        """
        # Retrieve the job ID from the event object
        event_id = self.__safeGetAttr(event, "job_id", None)

        # Retrieve the event code from the event object
        event_code = self.__safeGetAttr(event, "code", 0)

        # Create an event entity for the removed job
        data_event = self.__getEventJobDetailsById(event_id, event_code)

        # Invoke the listener for the removed job event if registered
        self.__taskCallableListener(data_event, ListeningEvent.JOB_ON_REMOVED)

    def __convertEventToEntity(self, event: type[Any]) -> EventEntity:
        """
        Convert the event object to an EventEntity.

        Ensure the event implements a `toEntity` method and use it to obtain
        the EventEntity representation for internal scheduler management.

        Parameters
        ----------
        event : Any
            Scheduled event object. Must implement a `toEntity` method.

        Returns
        -------
        EventEntity
            The converted EventEntity instance.

        Raises
        ------
        ValueError
            If the event does not implement a `toEntity` method.
        """
        # Check if the event has a toEntity method for conversion
        if not hasattr(event, "toEntity"):
            error_msg = "The event must have a 'toEntity' method for conversion."
            raise ValueError(error_msg)

        # Convert the event to its entity representation
        to_entity = event.toEntity
        return to_entity()

    def __triggerIsPast(self, signature: str, entity: EventEntity) -> bool:
        """
        Check if the event trigger is a DateTrigger set in the past.

        This method determines whether the trigger for the given event entity is a
        `DateTrigger` and if its `run_date` is earlier than the current time in the
        scheduler's timezone. If so, it logs a warning and returns True to indicate
        the event should be skipped.

        Parameters
        ----------
        signature : str
            Unique identifier for the scheduled event.
        entity : EventEntity
            Event entity containing trigger and scheduling information.

        Returns
        -------
        bool
            True if the trigger is a DateTrigger with a run date in the past,
            otherwise False.
        """
        # Only check for DateTrigger type triggers
        if isinstance(entity.trigger, DateTrigger):

            # Get the run_date from the trigger
            run_date = getattr(entity.trigger, "run_date", None)

            # Get the current time in the scheduler's timezone
            now = self.__getCurrentTime()

            # If run_date is set and is before now, skip scheduling
            if run_date is not None and run_date < now:

                # Log a warning about the past run_date
                log_msg = (
                    f"Scheduled command '{signature}' has a run_date in the past "
                    f"({run_date}); skipping."
                )
                self.__logger.warning(log_msg)
                return True

        # Return False if not a past DateTrigger
        return False

    def __syncScheduledlistScheduledJobs(self) -> None:
        """
        Synchronize scheduled events with the AsyncIOScheduler.

        Update the internal jobs list by converting each event in the internal events
        dictionary to its entity representation. Schedule jobs in the appropriate
        scheduler (control or main) based on their signature. Skip events with triggers
        set in the past. Register listeners for each job as needed.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It updates the internal jobs list
            and registers jobs with the AsyncIOScheduler.
        """
        # Only load events if the jobs list is empty to avoid duplicate scheduling
        if not self.__jobs or len(self.__jobs) == 0:

            # Lists to separate control jobs and custom jobs
            control_jobs = []
            custom_jobs = []

            # Iterate through all scheduled events in the internal events dictionary
            for signature, event in self.__events.items():

                # Convert the event to its entity representation (EventEntity)
                entity = self.__convertEventToEntity(event)

                # Skip loading events with a DateTrigger set in the past
                if self.__triggerIsPast(signature, entity):
                    continue

                # Add the job entity to the internal jobs list
                self.__jobs.append(entity)

                # Determine which scheduler to use based on the job signature
                if signature in self.CONTROL_OPERATIONS:
                    control_jobs.append((signature, entity))
                else:
                    custom_jobs.append((signature, entity))

            # Register control jobs with the control scheduler
            self.__registerJobs(self.__control_scheduler, control_jobs)

            # Register custom jobs with the main scheduler
            self.__registerJobs(self.__scheduler, custom_jobs)

            # Log the successful loading of the scheduled events for debugging
            log_msg = f"Total scheduled events loaded: {len(self.__jobs)}."
            self.__logger.debug(log_msg)

    def __registerJobs(
        self,
        scheduler: BaseScheduler,
        events: list[tuple[str, EventEntity]],
    ) -> None:
        """
        Register jobs in the specified scheduler.

        Iterate over the provided list of event tuples, each containing a job
        signature and its corresponding EventEntity. For each event, create a
        job function that invokes the reactor with the given command and
        arguments, and add the job to the scheduler with the appropriate
        configuration. If the event entity has an associated listener, register
        it using the setListener method.

        Parameters
        ----------
        scheduler : BaseScheduler
            The scheduler instance where jobs will be registered.
        events : list of tuple of (str, EventEntity)
            List of tuples, each with a job signature and its EventEntity.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Helper function to create a job function that calls the reactor with
        # the given command and arguments
        def create_job_func(cmd: str, args_list: list[str]) -> callable:
            return lambda: self.__reactor.call(cmd, args_list)

        # Iterate over each event tuple and add the job to the scheduler
        for signature, entity in events:

            # Add the job to the scheduler with the specified configuration
            scheduler.add_job(
                func=create_job_func(signature, list(entity.args)),
                trigger=entity.trigger,
                id=signature,
                name=entity.purpose,
                replace_existing=True,
                max_instances=entity.max_instances,
                misfire_grace_time=entity.misfire_grace_time,
                coalesce=entity.coalesce,
            )

            # Register the listener for the job if it exists
            if entity.listener:
                self.__listeners[signature] = entity.listener

    def registerListener(
        self,
        event: str | ListeningEvent,
        listener: IScheduleEventListener | callable,
    ) -> None:
        """
        Register a listener for a scheduler event or job.

        Register a callback or an instance of IScheduleEventListener for a global
        scheduler event or a specific job ID. The listener will be invoked when
        the event occurs.

        Parameters
        ----------
        event : str or ListeningEvent
            Event name or job ID to listen for. Can be a string or a ListeningEvent
            instance.
        listener : IScheduleEventListener or callable
            Listener to register. Must be callable or an instance of
            IScheduleEventListener.

        Returns
        -------
        None
            This method always returns None. No value is returned.

        Raises
        ------
        TypeError
            If the event name is not a non-empty string.
        ValueError
            If the event is not a valid ListeningEvent or job ID string.
        TypeError
            If the listener is not callable or not an instance of
            IScheduleEventListener.
        """
        # Convert ListeningEvent to its string value if necessary
        if isinstance(event, ListeningEvent):
            event = event.value

        # Validate event name is a non-empty string
        if not isinstance(event, str) or not event.strip():
            error_msg = "Event name must be a non-empty string."
            raise TypeError(error_msg)

        # Validate event is a valid ListeningEvent or a job ID string
        valid_events = {c.value for c in ListeningEvent}
        if event not in valid_events:
            error_msg = "Event must be a valid ListeningEvent or a job ID string."
            raise ValueError(error_msg)

        # Validate listener is callable or IScheduleEventListener instance
        if not callable(listener) and not isinstance(listener, IScheduleEventListener):
            error_msg = (
                "Listener must be callable or an instance of IScheduleEventListener."
            )
            raise TypeError(error_msg)

        # Register the listener for the event in the internal dictionary
        self.__listeners[event] = listener

    def command(
        self,
        signature: str,
        args: list[str] | None = None,
    ) -> IEvent:
        """
        Register an Event instance for a command signature and arguments.

        Validate the command signature and arguments, ensuring the command exists
        and arguments are in the correct format. If valid, create and register an
        Event object representing the scheduled command, storing it internally.

        Parameters
        ----------
        signature : str
            Unique signature identifying the command to schedule. Must be non-empty.
        args : list of str or None, optional
            List of string arguments for the command. Defaults to None.

        Returns
        -------
        IEvent
            The registered Event instance for further scheduling configuration.

        Raises
        ------
        RuntimeError
            If attempting to add a command while the scheduler is running.
        TypeError
            If the signature is not a non-empty string, or if arguments are not a
            list of strings.
        ValueError
            If the command signature is not registered.
        """
        # Prevent adding commands while the scheduler is running
        if self.isRunning():
            error_msg = (
                "Cannot add new commands while the scheduler is running. "
                "Please stop the scheduler before adding new commands."
            )
            raise RuntimeError(error_msg)

        # Validate that the command signature is a non-empty string
        if not isinstance(signature, str) or not signature.strip():
            error_msg = "Signature must be a non-empty string."
            raise TypeError(error_msg)

        # Check if the command is registered
        if not self.__isCommandRegistered(signature):
            error_msg = (
                f"Command with signature '{signature}' is not registered."
            )
            raise ValueError(error_msg)

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

        # Clear existing jobs and cached events before adding a new command
        self.__jobs.clear()
        self.__cache_scheduled_jobs.clear()

        # Register the command and its arguments in the internal events dictionary
        self.__events[signature] = Event(
            signature=signature,
            args=args or [],
            purpose=self.__getCommandDescription(signature),
        )

        # Return the Event instance for further configuration
        return self.__events[signature]

    async def start(self) -> None:
        """
        Start the AsyncIO scheduler and keep it running.

        Initialize and start the AsyncIOScheduler, ensuring all scheduled events are
        loaded and listeners are subscribed. The scheduler runs within an asyncio
        context until a stop signal is received. Handles graceful shutdowns and
        interruptions.

        Returns
        -------
        None
            This method does not return any value. The scheduler runs until stopped.

        Raises
        ------
        RuntimeError
            If the scheduler fails to start due to missing an asyncio event loop or
            other runtime issues.
        """
        try:

            # Ensure this method is called within an asyncio event loop
            asyncio.get_running_loop()

            # Create an asyncio event for clean shutdowns
            self._stop_event = asyncio.Event()

            # Load all scheduled events into the internal jobs list
            self.__syncScheduledlistScheduledJobs()

            # Subscribe to scheduler events for monitoring and handling
            self.__subscribeListeners()

            # Start the scheduler if it is not already running
            if not self.isRunning():
                self.__scheduler.start()
                self.__control_scheduler.start()

            # Log that the scheduler is now active and waiting for events
            log_msg = "Orionis Scheduler started successfully."
            self.__logger.info(log_msg)

            try:

                # Wait for the stop event to be set, which signals a shutdown
                await self._stop_event.wait()

            except (KeyboardInterrupt, asyncio.CancelledError):

                # Handle graceful shutdown when an interruption signal is received
                log_msg = "Shutdown signal received, stopping scheduler..."
                self.__logger.info(log_msg)
                await self.shutdown(wait=True)

            except Exception as e:

                # Log and raise any unexpected exceptions during scheduler operation
                log_msg = f"Unexpected error during scheduler operation: {e!s}"
                self.__logger.error(log_msg)
                error_msg = f"Scheduler operation failed: {e!s}"
                raise RuntimeError(error_msg) from e

            finally:

                # Ensure the scheduler is shut down properly, even if an error occurs
                if self.__scheduler.running:
                    await self.shutdown(wait=False)

        except RuntimeError as e:

            # Handle the case where no asyncio event loop is running
            if "no running event loop" in str(e):
                error_msg = (
                    "Scheduler must be started within an asyncio event loop"
                )
                raise RuntimeError(error_msg) from e
            error_msg = f"Failed to start the scheduler: {e!s}"
            raise RuntimeError(error_msg) from e

        except Exception as e:

            # Raise a runtime error for any other issues during startup
            error_msg = f"Failed to start the scheduler: {e!s}"
            raise RuntimeError(error_msg) from e

    def pause(self) -> None:
        """
        Pause all user jobs managed by the scheduler.

        Pause all currently scheduled user jobs in the AsyncIOScheduler if the
        scheduler is running. Iterate through all jobs, attempt to pause each one,
        and trigger listeners for the pause event. After all jobs are paused,
        trigger a global listener for the scheduler pause event. Clear the set of
        paused jobs before pausing to ensure only currently paused jobs are tracked.

        Returns
        -------
        None
            This method does not return any value. It pauses all user jobs and
            triggers the appropriate listeners and logging.
        """
        # Only pause jobs if the scheduler is currently running
        if not self.isRunning():
            return

        # Try to pause all jobs and handle any exceptions
        try:

            # Retrieve all jobs currently managed by the scheduler
            all_jobs = self.__scheduler.get_jobs()

            # Iterate through each job and attempt to pause it
            for job in all_jobs:

                # Get the job ID safely
                job_id = self.__safeGetAttr(job, "id", None)

                # Skip jobs without a valid user-defined ID
                if not job_id or not isinstance(job_id, str) or job_id.strip() == "":
                    continue

                # Retrieve event data for the paused job
                event_data = self.__getEventJobDetailsById(job_id)

                # Invoke the listener for the paused job event
                self.__taskCallableListener(
                    event_data,
                    ListeningEvent.JOB_ON_PAUSED,
                )

            # Prepare global event data for scheduler pause
            global_event_data = SchedulerPaused(
                code=EVENT_SCHEDULER_PAUSED,
                time=self.__getCurrentTime(),
            )

            # After all jobs are paused, invoke the global listener for scheduler pause
            self.__globalCallableListener(
                global_event_data,
                ListeningEvent.SCHEDULER_PAUSED,
            )

            # Get the current time in the configured timezone for logging
            now = self.__getFormattedNow()

            # Pause the scheduler and clear the set of previously paused jobs
            self.__scheduler.pause()

            # Store the timestamp when the scheduler was paused
            self.__paused_at = self.__getCurrentTime()

            # Log that all tasks have been paused
            log_msg = f"Orionis Scheduler paused all tasks successfully at: {now}."
            self.__logger.info(log_msg)

        except Exception as e:

            # Handle any exceptions that occur during the pause operation
            self.__handleException(e)

    def resume(self) -> None:
        """
        Resume all user jobs previously paused by the scheduler.

        Resume jobs only if the scheduler is currently paused. After resuming,
        trigger the global listener for the scheduler resume event and log the
        action. For jobs that missed execution while paused, trigger the missed
        event listener. The method does not return any value.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Only resume jobs if the scheduler is currently paused
        if not self.isPaused():
            return

        # Try to resume all jobs and handle any exceptions
        try:

            # Prepare global event data for scheduler resume
            global_event_data = SchedulerResumed(
                code=EVENT_SCHEDULER_RESUMED,
                time=self.__getCurrentTime(),
            )

            # Trigger the global listener for scheduler resume
            self.__globalCallableListener(
                global_event_data, ListeningEvent.SCHEDULER_RESUMED,
            )

            # Get the current time for logging
            now = self.__getFormattedNow()

            # Store the time when resuming
            resumed_at = self.__getCurrentTime()

            # Resume the main scheduler
            self.__scheduler.resume()

            # Iterate through all jobs to check for missed executions
            for job in self.__scheduler.get_jobs():

                # If the job was supposed to run while paused, trigger the missed event
                if (
                    job.next_run_time
                    and self.__paused_at <= job.next_run_time < resumed_at
                ):
                    # Retrieve event data for the missed job
                    event_data = self.__getEventJobDetailsById(job.id)

                    # Trigger the missed job event listener
                    self.__taskCallableListener(
                        event_data,
                        ListeningEvent.JOB_ON_MISSED,
                    )

            # Log that the scheduler has been resumed
            log_msg = f"Orionis Scheduler resumed all tasks successfully at: {now}."
            self.__logger.info(log_msg)

        except Exception as e:

            # Handle any exceptions that occur during the resume operation
            self.__handleException(e)

    async def shutdown(self, *, wait: bool = True) -> None:
        """
        Shut down the AsyncIO scheduler asynchronously.

        Gracefully stop the AsyncIOScheduler and signal the main event loop to
        terminate waiting. Ensures clean shutdown of both main and control schedulers.

        Parameters
        ----------
        wait : bool, optional
            If True, wait for currently executing jobs to finish. Default is True.

        Returns
        -------
        None
            Always returns None.
        """
        # If the scheduler is not running, exit early
        if not self.isRunning():
            return

        try:
            # Validate the wait parameter type
            if not isinstance(wait, bool):
                error_msg = "The 'wait' parameter must be a boolean."
                raise TypeError(error_msg)

            # Shut down both main and control schedulers
            self.__scheduler.shutdown(wait=wait)
            self.__control_scheduler.shutdown(wait=wait)

            # Signal the stop event to break the wait in start()
            if self._stop_event and not self._stop_event.is_set():
                self._stop_event.set()

            # Allow time for cleanup if waiting
            if wait:
                await asyncio.sleep(0.1)

            # Log the successful shutdown with current time
            now = self.__getFormattedNow()
            log_msg = f"Orionis Scheduler has been shut down successfully at: {now}."
            self.__logger.info(log_msg)

        except Exception as e:

            # Delegate exception handling to the application's error catcher
            self.__handleException(e)

    def pauseCommand(self, signature: str) -> bool:
        """
        Pause a scheduled job in the AsyncIO scheduler.

        Validate the signature and attempt to pause the job. Log the action and
        invoke the paused job listener if successful. Return True if paused,
        otherwise return False.

        Parameters
        ----------
        signature : str
            Unique signature (ID) of the job to pause.

        Returns
        -------
        bool
            True if the job was successfully paused, False otherwise.
        """
        # Check if the job signature is registered
        if signature not in self.__jobs:
            return False

        try:
            # Pause the job in the scheduler by its signature
            self.__scheduler.pause_job(signature)

            # Retrieve event data for the paused job
            event_data = self.__getEventJobDetailsById(signature)

            # Invoke the listener for the paused job event
            self.__taskCallableListener(
                event_data,
                ListeningEvent.JOB_ON_PAUSED,
            )

            # Log the successful pausing of the job
            log_msg = f"Task '{signature}' has been paused."
            self.__logger.info(log_msg)

            # Return True to indicate the job was successfully paused
            return True

        except Exception:

            # Return False if the job could not be paused
            return False

    def resumeCommand(self, signature: str) -> bool:
        """
        Resume a paused job in the AsyncIO scheduler.

        Validate the job signature and attempt to resume the job if it exists
        and is paused. Log the action and invoke the resumed job listener.
        Return True if the job was resumed, otherwise return False.

        Parameters
        ----------
        signature : str
            Unique signature (ID) of the job to resume.

        Returns
        -------
        bool
            True if the job was resumed, False otherwise.
        """
        # Check if the job signature is registered
        if signature not in self.__jobs:
            return False

        try:

            # Resume the job in the scheduler
            self.__scheduler.resume_job(signature)

            # Get event data for the resumed job
            event_data = self.__getEventJobDetailsById(signature)

            # Trigger the resumed job event listener
            self.__taskCallableListener(
                event_data,
                ListeningEvent.JOB_ON_RESUMED,
            )

            # Log the job resumption
            log_msg = f"Task '{signature}' has been resumed."
            self.__logger.info(log_msg)

            return True

        except Exception:

            # Return False if resume fails
            return False

    def removeCommand(self, signature: str) -> bool:
        """
        Remove a scheduled job from the scheduler by its signature.

        Validate the signature and attempt to remove the job from both the scheduler
        and the internal jobs list. Log the removal and return True if successful.
        Return False if the job does not exist or an error occurs.

        Parameters
        ----------
        signature : str
            Unique signature (ID) of the job to remove.

        Returns
        -------
        bool
            True if the job was removed, False otherwise.
        """
        # Check if the job signature exists in the internal jobs list
        if signature not in self.__jobs:
            return False

        try:
            # Remove the job from the scheduler using its signature
            self.__scheduler.remove_job(signature)

            # Remove the job from the internal jobs list
            for job in self.__jobs:
                if job.signature == signature:
                    self.__jobs.remove(job)
                    break

            # Log the removal of the job
            log_msg = f"Task '{signature}' has been removed from the scheduler."
            self.__logger.info(log_msg)

            # Explicitly return True if removal was successful
            return True

        except Exception:

            # Return False if removal fails
            return False

    def listScheduledJobs(self) -> list[dict]:
        """
        Retrieve all scheduled jobs managed by the scheduler.

        Ensure all scheduled events are loaded into the internal jobs list. Iterate
        through each job and collect its details in a dictionary format. Each dictionary
        contains the command signature, arguments, purpose, random delay, start and end
        dates, and additional job details.

        Returns
        -------
        list of dict
            List of dictionaries, each representing a scheduled job with keys:
            'signature', 'args', 'purpose', 'random_delay', 'start_date', 'end_date',
            'details', 'coalesce', 'max_instances', 'misfire_grace_time'. Returns an
            empty list if no jobs are scheduled.
        """
        # Return cached events if available
        if self.__cache_scheduled_jobs:
            return list(self.__cache_scheduled_jobs.values())

        # Ensure all events are loaded into the internal jobs list
        self.__syncScheduledlistScheduledJobs()

        # Clear the cache before populating it
        self.__cache_scheduled_jobs.clear()

        # Iterate over each job in the internal jobs list
        for job in self.__jobs:

            # Safely extract job details with default values if attributes are missing
            signature = self.__safeGetAttr(job, "signature", "")
            args = self.__safeGetAttr(job, "args", [])
            purpose = self.__safeGetAttr(job, "purpose", "No Description")
            random_delay = self.__safeGetAttr(job, "random_delay", 0)
            start_date: datetime | None = self.__safeGetAttr(job, "start_date", None)
            end_date: datetime | None = self.__safeGetAttr(job, "end_date", None)
            details = self.__safeGetAttr(job, "details", "Not Available")
            coalesce = self.__safeGetAttr(job, "coalesce", default=False)
            max_instances = self.__safeGetAttr(job, "max_instances", 1)
            misfire_grace_time = self.__safeGetAttr(job, "misfire_grace_time", None)

            # Format the start and end dates as strings, or None if not set
            formatted_start = (
                start_date.strftime("%Y-%m-%d %H:%M:%S") if start_date else None
            )
            formatted_end = (
                end_date.strftime("%Y-%m-%d %H:%M:%S") if end_date else None
            )

            # Store job details in the cache dictionary
            self.__cache_scheduled_jobs[signature] = {
                "signature": signature,
                "args": args,
                "purpose": purpose,
                "random_delay": random_delay,
                "start_date": formatted_start,
                "end_date": formatted_end,
                "details": details,
                "coalesce": coalesce,
                "max_instances": max_instances,
                "misfire_grace_time": misfire_grace_time,
            }

        # Return the list of scheduled job details
        return list(self.__cache_scheduled_jobs.values())

    def getScheduledJobDetails(self, signature: str) -> dict | None:
        """
        Retrieve job details by signature.

        Search the internal jobs list for a job matching the provided signature.
        Ensure all events are loaded before searching. Return a dictionary with
        job details if found, otherwise return None.

        Parameters
        ----------
        signature : str
            Unique signature (ID) of the job to retrieve.

        Returns
        -------
        dict or None
            Dictionary with job details if found, otherwise None.

        Notes
        -----
        Returns None if no job matches the signature.
        """
        if not self.__cache_scheduled_jobs:
            self.listScheduledJobs()
        return self.__cache_scheduled_jobs.get(signature, None)

    def isRunning(self) -> bool:
        """
        Check if the scheduler is running.

        Inspect the internal state of the AsyncIOScheduler to determine if it is active.
        The scheduler is running if it has been started and is not paused or shut down.

        Returns
        -------
        bool
            True if the scheduler is running and its state is STATE_RUNNING.
            False otherwise.
        """
        # Return True if the scheduler is running and its state is STATE_RUNNING
        return self.__scheduler.running and self.__scheduler.state == STATE_RUNNING

    def isPaused(self) -> bool:
        """
        Check if the scheduler is paused.

        Determine if the scheduler is currently in a paused state by inspecting its
        running status and internal state.

        Returns
        -------
        bool
            True if the scheduler is running and its state is paused, otherwise False.
        """
        # Scheduler is paused if running and state is STATE_PAUSED
        return self.__scheduler.running and self.__scheduler.state == STATE_PAUSED

    def forceStop(self) -> None:
        """
        Force stop the scheduler immediately without waiting for jobs to finish.

        This method shuts down the AsyncIOScheduler and control scheduler instantly,
        bypassing any graceful shutdown procedures. It also sets the internal stop
        event to interrupt the scheduler's main loop.

        Returns
        -------
        None
            Always returns None. The scheduler is stopped and the stop event is set.

        Notes
        -----
        Use with caution. Running jobs may be interrupted.
        """
        # Shut down the main scheduler if running, without waiting for jobs
        if self.__scheduler.running:
            self.__scheduler.shutdown(wait=False)
            self.__control_scheduler.shutdown(wait=False)

        # Signal the stop event to interrupt the main loop if not already set
        if self._stop_event and not self._stop_event.is_set():
            self._stop_event.set()

    def stop(self) -> None:
        """
        Signal the scheduler to stop synchronously by setting the internal stop event.

        Set the internal asyncio stop event to request a graceful shutdown of the
        scheduler from a synchronous context. If an asyncio event loop is running,
        set the stop event in a thread-safe manner using `call_soon_threadsafe`.
        If no event loop is running, set the stop event directly.

        Returns
        -------
        None
            Always returns None. Signals the scheduler to stop by setting the internal
            stop event.

        Notes
        -----
        If the stop event is already set or does not exist, this method does nothing.
        Any exceptions encountered while setting the stop event are logged as warnings,
        but the method will still attempt to set the event directly.
        """
        # Check if the stop event exists and is not already set
        if self._stop_event and not self._stop_event.is_set():

            try:
                # Try to get the current running event loop
                loop = asyncio.get_running_loop()

                # Set the stop event in a thread-safe manner
                # if the event loop is running
                loop.call_soon_threadsafe(self._stop_event.set)

            except RuntimeError:

                # No running event loop, set the stop event directly
                self._stop_event.set()

            except Exception as e:

                # Log any unexpected error but still try to set the event directly
                log_msg = f"Failed to set stop event in thread-safe manner: {e!s}"
                self.__logger.warning(log_msg)
                self._stop_event.set()
