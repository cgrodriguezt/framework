import asyncio
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
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
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.schedulers.base import STATE_PAUSED, STATE_RUNNING
from apscheduler.triggers.date import DateTrigger
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from orionis.console.contracts.event import IEvent
from orionis.console.contracts.reactor import IReactor
from orionis.console.contracts.schedule import ISchedule
from orionis.console.contracts.schedule_event_listener import IScheduleEventListener
from orionis.console.entities.event_job import EventJob
from orionis.console.entities.scheduler_error import SchedulerError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted
from orionis.console.entities.event import Event as EventEntity
from orionis.console.enums.listener import ListeningEvent
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.console.exceptions import CLIOrionisValueError
from orionis.console.request.cli_request import CLIRequest
from orionis.failure.contracts.catch import ICatch
from orionis.foundation.contracts.application import IApplication
from orionis.services.log.contracts.log_service import ILogger
from zoneinfo import ZoneInfo

class Schedule(ISchedule):

    # Error message constants
    SIGNATURE_REQUIRED_ERROR = "Signature must be a non-empty string."
    NOT_APPLICABLE = "Not Applicable"

    def __init__(
        self,
        reactor: IReactor,
        app: IApplication,
        rich_console: Console
    ) -> None:
        """
        Initialize a new instance of the Schedule class.

        This constructor sets up the internal state required for scheduling commands,
        including references to the application instance, the AsyncIOScheduler, the
        command reactor, and job tracking structures. It also initializes properties
        for managing the current scheduling context, logging, and event listeners.

        Parameters
        ----------
        reactor : IReactor
            An instance implementing the IReactor interface, used to retrieve available
            commands and execute scheduled jobs.
        app : IApplication
            The application container instance, used for configuration, dependency injection,
            and service resolution.
        rich_console : Console
            An instance of Rich's Console for advanced output formatting.

        Returns
        -------
        None
            This method does not return any value. It initializes the Schedule instance
            and prepares all required internal structures for scheduling and event handling.
        """

        # List of operations that can be performed on the scheduler
        self.__control_operations = [
            'schedule:pause',
            'schedule:resume',
            'schedule:shutdown'
        ]

        # Store the application instance for configuration and service access.
        self.__app: IApplication = app

        # Store the rich console instance for advanced output formatting.
        self.__rich_console = rich_console

        # Save the timezone configuration from the application settings.
        self.__tz = ZoneInfo(self.__app.config('app.timezone') or 'UTC')

        # Initialize the AsyncIOScheduler with the configured timezone.
        self.__scheduler = APSAsyncIOScheduler(timezone=self.__tz)
        self.__control_scheduler = APSAsyncIOScheduler(timezone=self.__tz)

        # Disable APScheduler's internal logging to avoid duplicate/conflicting logs.
        self.__disableLogging()

        # Initialize the logger using the application's dependency injection.
        self.__logger: ILogger = self.__app.make(ILogger)

        # Store the reactor instance for command management and job execution.
        self.__reactor: IReactor = reactor

        # Retrieve and store all available commands from the reactor.
        self.__available_commands = self.__getCommands()

        # Initialize the dictionary to keep track of scheduled events.
        self.__events: Dict[str, IEvent] = {}

        # Initialize the list to keep track of all scheduled job entities.
        self.__jobs: List[EventEntity] = []

        # Initialize the dictionary to manage event listeners.
        self.__listeners: Dict[str, callable] = {}

        # Initialize the asyncio event used to signal scheduler shutdown.
        self._stopEvent: Optional[asyncio.Event] = None

        # Retrieve and initialize the catch instance for exception handling.
        self.__catch: ICatch = app.make(ICatch)

        # Initialize the paused at timestamp
        self.__paused_at: Optional[datetime] = None

    def __disableLogging(
        self
    ) -> None:
        """
        Disable APScheduler logging to prevent conflicts and duplicate log messages.

        This method disables logging for the APScheduler library and its key subcomponents.
        It clears all handlers attached to the APScheduler loggers, disables log propagation,
        and turns off the loggers entirely. This is useful in applications that have their
        own logging configuration and want to avoid duplicate or unwanted log output from
        APScheduler.

        Returns
        -------
        None
            This method does not return any value. It modifies the logging configuration
            of APScheduler loggers in place.
        """

        # List of APScheduler logger names to disable
        for name in ["apscheduler", "apscheduler.scheduler", "apscheduler.executors.default"]:
            logger = logging.getLogger(name)
            logger.handlers.clear()                 # Remove all handlers to prevent output
            logger.propagate = False                # Prevent log messages from propagating to ancestor loggers
            logger.disabled = True                  # Disable the logger entirely

    def __getCommands(
        self
    ) -> dict:
        """
        Retrieve available commands from the reactor and return them as a dictionary.

        This method queries the reactor for all available jobs/commands, extracting their
        signatures and descriptions. The result is a dictionary where each key is the command
        signature and the value is another dictionary containing the command's signature and
        its description.

        Returns
        -------
        dict
            A dictionary mapping command signatures to their details. Each value is a dictionary
            with 'signature' and 'description' keys.
        """

        # Initialize the commands dictionary
        commands = {}

        # Iterate over all jobs provided by the reactor's info method
        for job in self.__reactor.info():

            signature: str = job.get('signature', None)
            description: str = job.get('description', 'No description available.')

            # Skip invalid or special method signatures
            if not signature or (signature.startswith('__') and signature.endswith('__')):
                continue

            # Store each job's signature and description in the commands dictionary
            commands[signature] = {
                'signature': signature,
                'description': description
            }

        # Return the commands dictionary
        return commands

    def __getCurrentTime(
        self
    ) -> str:
        """
        Retrieve the current date and time as a formatted string in the configured timezone.

        This method obtains the current date and time using the timezone specified in the application's
        configuration (defaulting to UTC if not set). The result is formatted as a string in the
        "YYYY-MM-DD HH:MM:SS" format, which is suitable for logging, display, or timestamping events.

        Returns
        -------
        str
            The current date and time as a string in the format "YYYY-MM-DD HH:MM:SS", localized to the
            scheduler's configured timezone.
        """

        # Get the current time in the scheduler's configured timezone
        now = datetime.now(self.__tz)

        # Return the formatted current time string
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def __getNow(
        self
    ) -> datetime:
        """
        Retrieve the current date and time as a timezone-aware datetime object.

        This method returns the current date and time, localized to the timezone configured
        for the scheduler instance. The timezone is determined by the application's configuration
        (typically set during initialization). This is useful for ensuring that all time-related
        operations within the scheduler are consistent and respect the application's timezone settings.

        Returns
        -------
        datetime
            A timezone-aware `datetime` object representing the current date and time
            in the scheduler's configured timezone.
        """

        # Return the current datetime localized to the scheduler's timezone
        return datetime.now(self.__tz)

    def __getAttribute(
        self,
        obj: Any,
        attr: str,
        default: Any = None
    ) -> Any:
        """
        Safely retrieve an attribute from an object, returning a default value if the attribute does not exist.

        This method attempts to access the specified attribute of the given object. If the attribute
        exists, its value is returned. If the attribute does not exist, the provided default value
        is returned instead. This prevents `AttributeError` exceptions when accessing attributes
        that may not be present on the object.

        Parameters
        ----------
        obj : Any
            The object from which to retrieve the attribute.
        attr : str
            The name of the attribute to retrieve.
        default : Any, optional
            The value to return if the attribute does not exist. Defaults to None.

        Returns
        -------
        Any
            The value of the specified attribute if it exists on the object; otherwise, the value
            of `default`.

        Notes
        -----
        This method is a wrapper around Python's built-in `getattr()` function, providing a safe
        way to access attributes that may or may not exist on an object.
        """

        # If the object is None, return the default value immediately
        if obj is None:
            return default

        # Use Python's built-in getattr to safely retrieve the attribute,
        # returning the default value if the attribute is not found.
        return getattr(obj, attr, default)

    def __isAvailable(
        self,
        signature: str
    ) -> bool:
        """
        Check if a command with the given signature is available among registered commands.

        This method determines whether the provided command signature exists in the internal
        dictionary of available commands. It is used to validate if a command can be scheduled
        or executed by the scheduler.

        Parameters
        ----------
        signature : str
            The signature of the command to check for availability.

        Returns
        -------
        bool
            Returns True if the command with the specified signature exists in the available
            commands dictionary; otherwise, returns False.

        Notes
        -----
        The method performs a simple membership check in the internal commands dictionary.
        It does not validate the format or correctness of the signature itself, only its
        presence among the registered commands.
        """

        # Check if the signature exists in the available commands dictionary
        return signature in self.__available_commands

    def __getDescription(
        self,
        signature: str
    ) -> Optional[str]:
        """
        Retrieve the description for a command based on its signature.

        This method searches the internal dictionary of available commands for the provided
        command signature and returns the corresponding description if found. If the signature
        does not exist in the available commands, the method returns None.

        Parameters
        ----------
        signature : str
            The unique signature identifying the command whose description is to be retrieved.

        Returns
        -------
        Optional[str]
            The description string associated with the command signature if it exists;
            otherwise, returns None.

        Notes
        -----
        This method is useful for displaying human-readable information about commands
        when scheduling or listing tasks.
        """

        # Attempt to retrieve the command entry from the available commands dictionary
        command_entry = self.__available_commands.get(signature)

        # If the command entry exists, return its description; otherwise, return None
        return command_entry['description'] if command_entry else None

    def command(
        self,
        signature: str,
        args: Optional[List[str]] = None
    ) -> 'IEvent':
        """
        Prepare and register an Event instance for a given command signature and its arguments.

        This method validates the provided command signature and arguments, ensuring that the command
        exists among the registered commands and that the arguments are in the correct format. If validation
        passes, it creates and registers an Event object representing the scheduled command, including its
        signature, arguments, and description. The Event instance is stored internally for later scheduling.

        Parameters
        ----------
        signature : str
            The unique signature identifying the command to be scheduled. Must be a non-empty string.
        args : Optional[List[str]], optional
            A list of string arguments to be passed to the command. Defaults to None.

        Returns
        -------
        IEvent
            The Event instance containing the command signature, arguments, and its description.
            This instance is also stored internally for further scheduling configuration.

        Raises
        ------
        CLIOrionisValueError
            If the command signature is not a non-empty string, if the arguments are not a list
            of strings or None, or if the command does not exist among the registered commands.
        """

        # Prevent adding new commands while the scheduler is running
        if self.isRunning():
            self.__raiseException(
                CLIOrionisValueError(
                    "Cannot add new commands while the scheduler is running. Please stop the scheduler before adding new commands."
                )
            )

        # Validate that the command signature is a non-empty string
        if not isinstance(signature, str) or not signature.strip():
            raise CLIOrionisValueError(
                "The command signature must be a non-empty string. Please provide a valid command signature."
            )

        # Ensure that arguments are either a list of strings or None
        if args is not None:
            if not isinstance(args, list):
                raise CLIOrionisValueError(
                    "Arguments must be provided as a list of strings or None. Please check your arguments."
                )
            for arg in args:
                if not isinstance(arg, str):
                    raise CLIOrionisValueError(
                        f"Invalid argument '{arg}'. Each argument must be a string."
                    )

        # Check if the command is available in the registered commands
        if not self.__isAvailable(signature):
            raise CLIOrionisValueError(
                f"The command '{signature}' is not available or does not exist. Please check the command signature."
            )

        # Import Event here to avoid circular dependency issues
        from orionis.console.fluent.event import Event

        # Store the command and its arguments for scheduling in the internal events dictionary
        self.__events[signature] = Event(
            signature=signature,
            args=args or [],
            purpose=self.__getDescription(signature)
        )

        # Return the Event instance for further scheduling configuration
        return self.__events[signature]

    def __getTaskFromSchedulerById(
        self,
        id: str,
        code: int = None
    ) -> Optional[EventJob]:
        """
        Retrieve a scheduled job from the AsyncIOScheduler by its unique ID.

        This method fetches a job from the AsyncIOScheduler using its unique identifier (ID).
        It extracts the job's attributes and creates a `Job` entity containing the relevant
        details. If the job does not exist, the method returns `None`.

        Parameters
        ----------
        id : str
            The unique identifier (ID) of the job to retrieve. This must be a non-empty string.

        Returns
        -------
        Optional[Job]
            A `Job` entity containing the details of the scheduled job if it exists.
            If the job does not exist, returns `None`.
        """

        # Extract event data from the internal events list if available
        event_data: dict = self.event(id)

        # Retrieve the job data from the scheduler using the provided job ID
        data = self.__scheduler.get_job(id)

        # If no job is found, return EventJob with default values
        _id = self.__getAttribute(data, 'id', None)
        if not _id and code in (EVENT_JOB_MISSED, EVENT_JOB_REMOVED):
            _id = event_data.get('signature')
        elif not _id:
            return EventJob()

        # Extract the job code if available
        _code = code if code is not None else 0

        # Extract the job name if available
        _name = self.__getAttribute(data, 'name', None)

        # Extract the job function if available
        _func = self.__getAttribute(data, 'func', None)

        # Extract the job arguments if available
        _args = self.__getAttribute(data, 'args', tuple(event_data.get('args', [])))

        # Extract the job trigger if available
        _trigger = self.__getAttribute(data, 'trigger', None)

        # Extract the job executor if available
        _executor = self.__getAttribute(data, 'executor', None)

        # Extract the job jobstore if available
        _jobstore = self.__getAttribute(data, 'jobstore', None)

        # Extract the job misfire_grace_time if available
        _misfire_grace_time = self.__getAttribute(data, 'misfire_grace_time', None)

        # Extract the job max_instances if available
        _max_instances = self.__getAttribute(data, 'max_instances', 1)

        # Extract the job coalesce if available
        _coalesce = self.__getAttribute(data, 'coalesce', False)

        # Extract the job next_run_time if available
        _next_run_time = self.__getAttribute(data, 'next_run_time', None)

        # Extract additional event data if available
        _purpose = event_data.get('purpose', None)

        # Extract additional event data if available
        _start_date = event_data.get('start_date', None)

        # Extract additional event data if available
        _end_date = event_data.get('end_date', None)

        # Extract additional event data if available
        _details = event_data.get('details', None)

        # Create and return a Job entity based on the retrieved job data
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
            exception = None,
            traceback = None,
            retval = None,
            purpose = _purpose,
            start_date = _start_date,
            end_date = _end_date,
            details = _details
        )

    def __subscribeListeners(
        self
    ) -> None:
        """
        Subscribe internal handlers to APScheduler events for monitoring and control.

        This method attaches internal listener methods to the AsyncIOScheduler instance for a variety of
        scheduler and job-related events. These listeners enable the scheduler to respond to lifecycle
        changes (such as start, shutdown, pause, and resume) and job execution events (such as submission,
        execution, errors, missed runs, max instance violations, and removals).

        Each listener is responsible for logging, invoking registered callbacks, and handling errors or
        missed jobs as appropriate. This setup ensures that the scheduler's state and job execution
        are monitored and managed effectively.

        Returns
        -------
        None
            This method does not return any value. It registers event listeners on the scheduler instance.

        Notes
        -----
        The listeners are attached to the following APScheduler events:
            - Scheduler started
            - Scheduler shutdown
            - Job error
            - Job submitted
            - Job executed
            - Job missed
            - Job max instances exceeded
            - Job removed

        These listeners enable the scheduler to handle and react to all critical scheduling events.
        """

        # Register listener for when the scheduler starts
        self.__scheduler.add_listener(self.__startedListener, EVENT_SCHEDULER_STARTED)

        # Register listener for when the scheduler shuts down
        self.__scheduler.add_listener(self.__shutdownListener, EVENT_SCHEDULER_SHUTDOWN)

        # Register listener for job execution errors
        self.__scheduler.add_listener(self.__errorListener, EVENT_JOB_ERROR)

        # Register listener for when a job is submitted to its executor
        self.__scheduler.add_listener(self.__submittedListener, EVENT_JOB_SUBMITTED)

        # Register listener for when a job has finished executing
        self.__scheduler.add_listener(self.__executedListener, EVENT_JOB_EXECUTED)

        # Register listener for when a job is missed (not run at its scheduled time)
        self.__scheduler.add_listener(self.__missedListener, EVENT_JOB_MISSED)

        # Register listener for when a job exceeds its maximum allowed concurrent instances
        self.__scheduler.add_listener(self.__maxInstancesListener, EVENT_JOB_MAX_INSTANCES)

        # Register listener for when a job is removed from the scheduler
        self.__scheduler.add_listener(self.__removedListener, EVENT_JOB_REMOVED)

    def __globalCallableListener(
        self,
        event_data: Optional[Union[SchedulerStarted, SchedulerPaused, SchedulerResumed, SchedulerShutdown, SchedulerError]],
        listening_vent: ListeningEvent
    ) -> None:
        """
        Invoke registered listeners for global scheduler events.

        This method is responsible for handling global scheduler events such as when the scheduler starts, pauses, resumes,
        shuts down, or encounters an error. It checks if a listener is registered for the specified event type and, if so,
        invokes the listener with the provided event data and the current scheduler instance. The listener can be either a
        coroutine or a regular callable.

        Parameters
        ----------
        event_data : Optional[Union[SchedulerStarted, SchedulerPaused, SchedulerResumed, SchedulerShutdown, SchedulerError]]
            The event data associated with the global scheduler event. This may include details about the event,
            such as its type, code, time, or context. If no specific data is available, this parameter can be None.
        listening_vent : ListeningEvent
            An instance of the ListeningEvent enum representing the global scheduler event to handle.

        Returns
        -------
        None
            This method does not return any value. It executes the registered listener for the specified event if one exists.

        Raises
        ------
        CLIOrionisValueError
            If the provided `listening_vent` is not an instance of ListeningEvent.

        Notes
        -----
        This method is intended for internal use to centralize the invocation of global event listeners.
        It ensures that only valid event types are processed and that exceptions raised by listeners are
        properly handled through the application's error handling mechanism.
        """

        # Ensure the provided event is a valid ListeningEvent instance
        if not isinstance(listening_vent, ListeningEvent):
            self.__raiseException(CLIOrionisValueError("The event must be an instance of ListeningEvent."))

        # Retrieve the string identifier for the event from the ListeningEvent enum
        scheduler_event = listening_vent.value

        # Check if a listener is registered for this global event
        if scheduler_event in self.__listeners:

            # Retrieve the listener callable for the event
            listener = self.__listeners[scheduler_event]

            # If the listener is callable, invoke it with event data and the scheduler instance
            if callable(listener):

                try:

                    # Execute the listener, handling both coroutine and regular functions
                    self.__app.invoke(listener, event_data, self)

                except Exception as e:

                    # Handle any exceptions raised by the listener using the application's error handler
                    self.__raiseException(e)

    def __taskCallableListener( # NOSONAR
        self,
        event_data: EventJob,
        listening_vent: ListeningEvent
    ) -> None:
        """
        Invoke registered listeners for specific task/job events.

        This method is responsible for handling task/job-specific events such as job errors,
        executions, submissions, missed jobs, and max instance violations. It checks if a
        listener is registered for the specific job ID associated with the event and, if so,
        invokes the appropriate method on the listener. The listener can be either a class
        implementing `IScheduleEventListener` or a callable.

        Parameters
        ----------
        event_data : EventJob
            The event data associated with the task/job event. This includes details about the job,
            such as its ID, exception (if any), and other context. If no specific data is available,
            this parameter can be None.
        listening_vent : ListeningEvent
            An instance of the `ListeningEvent` enum representing the task/job event to handle.

        Returns
        -------
        None
            This method does not return any value. It invokes the registered listener for the
            specified job event, if one exists.

        Raises
        ------
        CLIOrionisValueError
            If the provided `listening_vent` is not an instance of `ListeningEvent`.
            If the listener for the job ID is not a subclass of `IScheduleEventListener`.

        Notes
        -----
        This method is intended for internal use to centralize the invocation of task/job event listeners.
        It ensures that only valid event types and listeners are processed, and that exceptions raised
        by listeners are properly handled through the application's error handling mechanism.
        """

        # Ensure the provided event is a valid ListeningEvent instance
        if not isinstance(listening_vent, ListeningEvent):
            self.__raiseException(CLIOrionisValueError("The event must be an instance of ListeningEvent."))

        # Validate that event_data is a valid EventJob with a non-empty id
        if not isinstance(event_data, EventJob) or not hasattr(event_data, 'id') or not event_data.id:
            return

        # Retrieve the string identifier for the event from the ListeningEvent enum
        scheduler_event = listening_vent.value

        # Check if a listener is registered for this specific job ID
        if event_data.id in self.__listeners:

            # Retrieve the listener for the specific job ID
            listener = self.__listeners[event_data.id]

            # If the listener is a subclass of IScheduleEventListener, invoke the appropriate method
            if issubclass(listener, IScheduleEventListener):
                try:
                    # If the listener is a class, instantiate it using the application container
                    if isinstance(listener, type):
                        listener = self.__app.make(listener)

                    # Check if the listener has a method corresponding to the event type and is callable
                    if hasattr(listener, scheduler_event) and callable(getattr(listener, scheduler_event)):
                        # Call the event method on the listener, passing event data and the scheduler instance
                        self.__app.call(listener, scheduler_event, event_data, self)

                except Exception as e:

                    # Handle any exceptions raised by the listener using the application's error handler
                    self.__raiseException(e)

            else:
                # If the listener is not a subclass of IScheduleEventListener, raise an exception
                self.__raiseException(
                    CLIOrionisValueError(
                        f"The listener for job ID '{event_data.id}' must be a subclass of IScheduleEventListener."
                    )
                )

    def __getPID(
        self
    ) -> int:
        """
        Retrieve the current process ID (PID) of the running scheduler.

        This method obtains the process ID of the current Python process using the `os` module.
        The PID is a unique identifier assigned by the operating system to each running process.
        This information can be useful for logging, monitoring, or managing the scheduler process.

        Returns
        -------
        int
            The process ID (PID) of the current Python process.
        """

        import os

        # Return the current process ID using os.getpid()
        return os.getpid()

    def __startedListener(
        self,
        event
    ) -> None:
        """
        Handle the scheduler started event for logging and invoking registered listeners.

        This method is triggered when the scheduler starts. It logs an informational
        message indicating that the scheduler has started successfully and displays
        a formatted message on the rich console. If a listener is registered for the
        scheduler started event, it invokes the listener with the event details.

        Parameters
        ----------
        event : SchedulerStarted
            An event object containing details about the scheduler start event.

        Returns
        -------
        None
            This method does not return any value. It performs logging, displays
            a message on the console, and invokes any registered listener for the
            scheduler started event.
        """

        # Get the current time in the configured timezone
        now = self.__getCurrentTime()

        # Display a start message for the scheduler worker on the rich console
        # Add a blank line for better formatting
        self.__rich_console.line()
        panel_content = Text.assemble(
            ("🚀 Orionis Scheduler Worker ", "bold white on green"),
            ("\n\n", ""),
            ("✅ The scheduled tasks worker has started successfully.\n", "white"),
            (f"🕒 Started at: {now} | 🌐 Timezone: {self.__tz.key} | 🆔 PID: {self.__getPID()}\n", "dim"),
            ("🛑 To stop the worker, press ", "white"),
            ("Ctrl+C", "bold yellow")
        )

        # Display the message in a styled panel
        self.__rich_console.print(
            Panel(panel_content, border_style="green", padding=(1, 2))
        )

        # Add another blank line for better formatting
        self.__rich_console.line()

        # Check if a listener is registered for the scheduler started event
        event_data = SchedulerStarted(
            code=self.__getAttribute(event, 'code', 0),
            time=self.__getNow()
        )

        # If a listener is registered for this event, invoke the listener with the event details
        self.__globalCallableListener(event_data, ListeningEvent.SCHEDULER_STARTED)

        # Log an informational message indicating that the scheduler has started
        self.__logger.info(f"Orionis Scheduler started successfully at: {now}.")

        # Log the timezone currently assigned to the scheduler for traceability
        self.__logger.info(
            f"Timezone assigned to the scheduler: {self.__tz.key}."
        )

    def __shutdownListener(
        self,
        event
    ) -> None:
        """
        Handle the scheduler shutdown event for logging and invoking registered listeners.

        This method is triggered when the scheduler shuts down. It logs an informational
        message indicating that the scheduler has shut down successfully and displays
        a formatted message on the rich console. If a listener is registered for the
        scheduler shutdown event, it invokes the listener with the event details.

        Parameters
        ----------
        event : SchedulerShutdown
            An event object containing details about the scheduler shutdown event.

        Returns
        -------
        None
            This method does not return any value. It performs logging, displays
            a message on the console, and invokes any registered listener for the
            scheduler shutdown event.
        """

        # Get the current time in the configured timezone
        now = self.__getCurrentTime()

        # Check if a listener is registered for the scheduler shutdown event
        event_data = SchedulerShutdown(
            code=self.__getAttribute(event, 'code', 0),
            time=self.__getNow()
        )

        # If a listener is registered for this event, invoke the listener with the event details
        self.__globalCallableListener(event_data, ListeningEvent.SCHEDULER_SHUTDOWN)

        # Log an informational message indicating that the scheduler has shut down
        self.__logger.info(f"Orionis Scheduler shut down successfully at {now}.")

    def __errorListener(
        self,
        event
    ) -> None:
        """
        Handle job error events for logging, error reporting, and listener invocation.

        This method is triggered when a scheduled job raises an exception during execution.
        It logs an error message with the job ID and exception details, updates the job event
        data with error information, and invokes any registered listeners for both the specific
        job error and the global scheduler error event. The method also delegates exception
        handling to the application's error catching mechanism.

        Parameters
        ----------
        event : JobError
            An event object containing details about the errored job, including its ID,
            exception, traceback, and event code.

        Returns
        -------
        None
            This method does not return any value. It performs logging, error reporting,
            and invokes any registered listeners for the job error and scheduler error events.

        Notes
        -----
        - The method updates the job event data with the exception and traceback.
        - Both job-specific and global error listeners are invoked if registered.
        - All exceptions are delegated to the application's error handling system.
        """

        # Extract job ID, event code, exception, and traceback from the event object
        event_id = self.__getAttribute(event, 'job_id', None)
        event_code = self.__getAttribute(event, 'code', 0)
        event_exception = self.__getAttribute(event, 'exception', None)
        event_traceback = self.__getAttribute(event, 'traceback', None)

        # Retrieve the job event data and update it with error details
        job_event_data = self.__getTaskFromSchedulerById(event_id)
        job_event_data.code = event_code
        job_event_data.exception = event_exception
        job_event_data.traceback = event_traceback

        # Invoke the task-specific listener for job errors, if registered
        self.__taskCallableListener(job_event_data, ListeningEvent.JOB_ON_FAILURE)

        # Prepare the global scheduler error event data
        event_data = SchedulerError(
            code=event_code,
            time=self.__getNow(),
            exception=event_exception,
            traceback=event_traceback
        )

        # Invoke the global listener for scheduler errors, if registered
        self.__globalCallableListener(event_data, ListeningEvent.SCHEDULER_ERROR)

        # Delegate exception handling to the application's error catching mechanism
        self.__raiseException(event_exception)

    def __submittedListener(
        self,
        event
    ) -> None:
        """
        Handle job submission events for logging and invoking registered listeners.

        This internal method is triggered when a job is submitted to its executor by the scheduler.
        It logs an informational message about the job submission, creates an event entity representing
        the job submission, and invokes any registered listeners for the submitted job. This allows
        for custom pre-execution logic or notifications to be handled externally.

        Parameters
        ----------
        event : JobSubmitted
            An event object containing details about the submitted job, such as its ID and
            any associated event code.

        Returns
        -------
        None
            This method does not return any value. It performs logging and invokes any
            registered listener for the job submission event.

        Notes
        -----
        This method is intended for internal use to centralize the handling of job submission
        events. It ensures that job submissions are logged and that any custom listeners
        associated with the job are properly notified.
        """

        # Extract job ID and code from the event object, using default values if not present
        event_id = self.__getAttribute(event, 'job_id', None)
        event_code = self.__getAttribute(event, 'code', 0)

        # Create an event entity for the submitted job, including its ID and code
        data_event = self.__getTaskFromSchedulerById(event_id, event_code)

        # If a listener is registered for this job ID, invoke the listener with the event details
        self.__taskCallableListener(data_event, ListeningEvent.JOB_BEFORE)

    def __executedListener(
        self,
        event
    ) -> None:
        """
        Handle job execution events for logging, error reporting, and listener invocation.

        This method is triggered when a job has finished executing in the scheduler. It logs an informational
        message indicating the successful execution of the job. If the job execution resulted in an exception,
        the error is logged and reported using the application's error handling system. Additionally, if a
        listener is registered for the executed job, this method invokes the listener with the event details.

        Parameters
        ----------
        event : JobExecuted
            An event object containing details about the executed job, including its ID, return value,
            exception (if any), and traceback.

        Returns
        -------
        None
            This method does not return any value. It performs logging, error reporting, and invokes
            any registered listener for the executed job.

        Notes
        -----
        This method is intended for internal use to centralize the handling of job execution events.
        It ensures that job executions are logged, errors are reported, and any custom listeners
        associated with the job are properly notified.
        """

        # Extract the job ID and event code from the event object, using default values if not present
        event_id = self.__getAttribute(event, 'job_id', None)
        event_code = self.__getAttribute(event, 'code', 0)

        # Create an event entity for the executed job, including its ID and code
        data_event = self.__getTaskFromSchedulerById(event_id, event_code)

        # If a listener is registered for this job ID, invoke the listener with the event details
        self.__taskCallableListener(data_event, ListeningEvent.JOB_AFTER)

    def __missedListener(
        self,
        event
    ) -> None:
        """
        Handle job missed events for logging, reporting, and invoking registered listeners.

        This method is triggered when a scheduled job is missed (i.e., it was not executed at its scheduled time)
        by the scheduler. It logs a warning message indicating the missed job and its scheduled run time, creates
        an event entity for the missed job, and invokes any registered listeners for the missed job event. This
        ensures that missed executions are tracked and that any custom logic associated with missed jobs is executed.

        Parameters
        ----------
        event : JobMissed
            An event object containing details about the missed job, including its ID (`job_id`), event code (`code`),
            and the scheduled run time (`scheduled_run_time`).

        Returns
        -------
        None
            This method does not return any value. It performs logging, reporting, and invokes any registered
            listener for the missed job event.

        Notes
        -----
        - This method is intended for internal use to centralize the handling of missed job events.
        - It ensures that missed jobs are logged and that any custom listeners associated with the job are properly notified.
        - The event entity created provides structured information to listeners for further processing.
        """

        # Extract the job ID from the event object, or None if not present
        event_id = self.__getAttribute(event, 'job_id', None)

        # Extract the event code from the event object, defaulting to 0 if not present
        event_code = self.__getAttribute(event, 'code', 0)

        # Create an event entity for the missed job, including its ID and code
        data_event = self.__getTaskFromSchedulerById(event_id, event_code)

        # If a listener is registered for this job ID, invoke the listener with the event details
        self.__taskCallableListener(data_event, ListeningEvent.JOB_ON_MISSED)

    def __maxInstancesListener(
        self,
        event
    ) -> None:
        """
        Handle job max instances events for logging, error reporting, and listener invocation.

        This method is triggered when a job execution exceeds the maximum allowed concurrent instances.
        It logs an error message indicating the job ID that exceeded its instance limit, creates an event
        entity for the affected job, and invokes any registered listener for this job's max instances event.
        This allows for custom handling, notification, or recovery logic to be executed in response to
        the max instances violation.

        Parameters
        ----------
        event : JobMaxInstances
            An event object containing details about the job that exceeded the maximum allowed instances,
            including its job ID and event code.

        Returns
        -------
        None
            This method does not return any value. It performs logging, error reporting, and invokes
            any registered listener for the job max instances event.

        Notes
        -----
        This method is intended for internal use to centralize the handling of job max instances events.
        It ensures that such events are logged and that any custom listeners associated with the job
        are properly notified. No value is returned.
        """

        # Extract the job ID and event code from the event object, using default values if not present
        event_id = self.__getAttribute(event, 'job_id', None)
        event_code = self.__getAttribute(event, 'code', 0)

        # Create an event entity for the job that exceeded max instances
        data_event = self.__getTaskFromSchedulerById(event_id, event_code)

        # If a listener is registered for this job ID, invoke the listener with the event details
        self.__taskCallableListener(data_event, ListeningEvent.JOB_ON_MAXINSTANCES)

    def __removedListener(
        self,
        event
    ) -> None:
        """
        Handle job removal events for logging and invoking registered listeners.

        This method is triggered when a job is removed from the scheduler. It logs an informational
        message indicating that the job has been removed. If the application is in debug mode, it
        may display a message on the console. Additionally, if a listener is registered for the
        removed job, this method invokes the listener with the event details.

        Parameters
        ----------
        event : JobRemoved
            An event object containing details about the removed job, such as its ID and event code.

        Returns
        -------
        None
            This method does not return any value. It performs logging and invokes any registered
            listener for the job removal event.

        Notes
        -----
        - The method retrieves the job ID and event code from the event object.
        - It logs the removal of the job and creates an event entity for the removed job.
        - If a listener is registered for the job, it is invoked with the event details.
        """

        # Retrieve the job ID and event code from the event object
        event_id = self.__getAttribute(event, 'job_id', None)
        event_code = self.__getAttribute(event, 'code', 0)

        # Create an event entity for the removed job
        data_event = self.__getTaskFromSchedulerById(event_id, event_code)

        # If a listener is registered for this job ID, invoke the listener with the event details
        self.__taskCallableListener(data_event, ListeningEvent.JOB_ON_REMOVED)

    def __triggerIsPast(
        self,
        signature: str,
        entity: EventEntity
    ) -> bool:
        """
        Determine if the trigger for a scheduled event is set to a date in the past.

        This method checks whether the trigger associated with the given event entity is a
        `DateTrigger` and, if so, compares its `run_date` to the current time in the scheduler's
        configured timezone. If the trigger's run date is in the past, a warning is logged and
        the method returns True, indicating that the event should be skipped.

        Parameters
        ----------
        signature : str
            The unique signature identifying the scheduled event.
        entity : EventEntity
            The event entity containing the trigger and scheduling information.

        Returns
        -------
        bool
            True if the event's trigger is a `DateTrigger` with a run date in the past; False otherwise.

        Notes
        -----
        This method is used to prevent scheduling events that would immediately be considered expired.
        """

        # Check if the event's trigger is a DateTrigger and its run_date is in the past
        if isinstance(entity.trigger, DateTrigger):
            run_date = getattr(entity.trigger, 'run_date', None)
            now = self.__getNow()

            # If the run_date is set and is before the current time, log a warning and return True
            if run_date is not None and run_date < now:
                self.__logger.warning(
                    f"Scheduled event '{signature}' has a run_date in the past ({run_date}); skipping."
                )
                return True

        # Return False if the trigger is not a past DateTrigger
        return False

    def __eventToEntity(
        self,
        event
    ) -> EventEntity:
        """
        Convert a scheduled event object to its corresponding EventEntity representation.

        This method takes a scheduled event and transforms it into an `EventEntity` instance,
        which encapsulates all relevant attributes required for internal tracking and management
        within the scheduler. The conversion relies on the event implementing a `toEntity` method.

        Parameters
        ----------
        event : Any
            The scheduled event object to be converted. Must implement a `toEntity` method.

        Returns
        -------
        EventEntity
            An instance of `EventEntity` containing the extracted attributes from the event.

        Raises
        ------
        CLIOrionisValueError
            If the provided event does not implement a `toEntity` method.

        Notes
        -----
        This method is used internally to standardize event objects for consistent handling
        within the scheduler's job management system.
        """

        # Ensure the event has a toEntity method for conversion
        if not hasattr(event, 'toEntity'):
            raise CLIOrionisValueError("The event must have a 'toEntity' method for conversion.")

        # Convert the event to its entity representation (EventEntity)
        to_entity = getattr(event, 'toEntity')
        return to_entity()

    def __loadEvents(
        self
    ) -> None:
        """
        Synchronize and register all scheduled events with the AsyncIOScheduler.

        This method updates the internal jobs list (`self.__jobs`) by converting each event in the internal
        events dictionary to its corresponding entity representation. It then schedules these jobs in the
        appropriate scheduler (control or main) based on their signature. Events with triggers set in the
        past are skipped to prevent immediate expiration. Associated listeners are registered for each job
        as needed. This ensures that all scheduled jobs are properly tracked and managed by both the internal
        state and the scheduler.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It updates the internal jobs list and registers jobs
            with the AsyncIOScheduler.

        Raises
        ------
        CLIOrionisRuntimeError
            Raised if an error occurs while loading or scheduling an event.

        Notes
        -----
        - Events are loaded only if the internal jobs list is empty to avoid duplicate scheduling.
        - Each event must implement a `toEntity` method for conversion.
        - Jobs are added to the scheduler with their respective configuration, and listeners are registered if present.
        """

        # Only load events if the jobs list is empty to avoid duplicate scheduling
        if not self.__jobs:

            # Lists to separate control jobs and custom jobs
            control_jobs = []
            custom_jobs = []

            # Iterate through all scheduled events in the internal events dictionary
            for signature, event in self.__events.items():

                try:

                    # Convert the event to its entity representation (EventEntity)
                    entity = self.__eventToEntity(event)

                    # Skip loading events with a DateTrigger set in the past
                    if self.__triggerIsPast(signature, entity):
                        continue

                    # Add the job entity to the internal jobs list
                    self.__jobs.append(entity)

                    # Determine which scheduler to use based on the job signature
                    if signature in self.__control_operations:
                        control_jobs.append((signature, entity))
                    else:
                        custom_jobs.append((signature, entity))

                except Exception as e:

                    # Construct an error message for failed event loading
                    error_msg = f"Failed to load scheduled event '{signature}': {str(e)}"

                    # Log the error message
                    self.__logger.error(error_msg)

                    # Raise a runtime error to signal failure in loading the scheduled event
                    raise CLIOrionisRuntimeError(error_msg)

            # Register control jobs with the control scheduler
            self.__loadJobs(self.__control_scheduler, control_jobs)

            # Register custom jobs with the main scheduler
            self.__loadJobs(self.__scheduler, custom_jobs)

            # Log the successful loading of the scheduled events for debugging
            self.__logger.debug(f"Scheduled events loaded successfully: {len(self.__jobs)} jobs.")

    def __loadJobs(
        self,
        scheduler: BaseScheduler,
        events: List[Tuple[str, EventEntity]]
    ) -> None:
        """
        Load and register jobs into the specified scheduler.

        This method iterates over a list of event tuples, each containing a job signature and its corresponding
        EventEntity. For each event, it creates a job function that invokes the reactor with the provided command
        and arguments, then adds the job to the given scheduler with the appropriate configuration. If the event
        entity has an associated listener, the listener is registered for the job.

        Parameters
        ----------
        scheduler : BaseScheduler
            The scheduler instance (either control or main) where jobs will be registered.
        events : List[Tuple[str, EventEntity]]
            A list of tuples, each containing a job signature and its corresponding EventEntity.

        Returns
        -------
        None
            This method does not return any value. It registers jobs and listeners with the scheduler.

        Notes
        -----
        - The job function is created as a lambda that calls the reactor with the command and arguments.
        - Jobs are added with configuration options such as trigger, ID, name, max instances, misfire grace time, and coalesce.
        - If an event entity has a listener, it is registered using the setListener method.
        """

        # Helper function to create a job function that calls the reactor with the given command and arguments
        def create_job_func(cmd, args_list):

            # Returns a lambda that executes the reactor call for the specified command and arguments
            return lambda: self.__reactor.call(cmd, args_list)

        # Iterate over each event tuple and add the job to the scheduler
        for signature, entity in events:

            # Add the job to the scheduler with the specified configuration
            scheduler.add_job(
                func=create_job_func(signature, list(entity.args)),
                trigger=entity.trigger,
                id=signature,
                name=f"{signature}({', '.join(map(str, entity.args))})",
                replace_existing=True,
                max_instances=entity.max_instances,
                misfire_grace_time=entity.misfire_grace_time,
                coalesce=entity.coalesce
            )

            # If the event entity has an associated listener, register it
            if entity.listener:
                self.setListener(signature, entity.listener)

    def __raiseException(
        self,
        exception: BaseException
    ) -> None:
        """
        Centralized exception handling for the scheduler, delegating to the application's error catching system.

        This private method provides a unified mechanism for handling exceptions that occur within the scheduler's
        context. It forwards the exception to the application's error catching mechanism, ensuring consistent
        processing of errors according to the application's global error handling policies. This may include
        logging, reporting, or re-raising the exception, depending on the application's configuration.

        Parameters
        ----------
        exception : BaseException
            The exception instance raised during scheduler or command execution. This can be any subclass of
            BaseException, including system, runtime, or custom exceptions.

        Returns
        -------
        None
            This method always returns None. It delegates the exception to the application's error
            handling system for further processing.

        Notes
        -----
        This method is intended for internal use within the scheduler. The actual handling of the exception
        (such as logging or propagation) is determined by the application's error catching implementation.
        """

        # Create a CLIRequest object representing the current scheduler context
        request = CLIRequest(
            command="schedule:work",
            args={}
        )

        # Delegate the exception to the application's error catching system
        self.__catch.exception(
            self,
            request,
            exception
        )

    def setListener(
        self,
        event: Union[str, ListeningEvent],
        listener: Union[IScheduleEventListener, callable]
    ) -> None:
        """
        Register a listener for a specific scheduler event or job.

        This method allows you to associate a callback or an instance of
        `IScheduleEventListener` with a scheduler event. The event can be a global
        scheduler event (such as 'scheduler_started', 'scheduler_paused', etc.) or
        a specific job ID. When the specified event occurs, the registered listener
        will be invoked with the event data.

        Parameters
        ----------
        event : str or ListeningEvent
            The name of the event to listen for. This can be a string representing
            a global event name (e.g., 'scheduler_started') or a job ID, or an
            instance of `ListeningEvent`.
        listener : IScheduleEventListener or callable
            The listener to be registered. This can be a callable function or an
            instance of `IScheduleEventListener`. The listener should accept the
            event object as its parameter.

        Returns
        -------
        None
            This method does not return any value. It registers the listener for
            the specified event.

        Raises
        ------
        CLIOrionisValueError
            If the event name is not a non-empty string, or if the listener is not
            callable or an instance of `IScheduleEventListener`.

        Notes
        -----
        - If the event parameter is a `ListeningEvent`, its value is used as the event name.
        - The listener will be stored internally and invoked when the corresponding event occurs.
        """

        # If the event is an instance of ListeningEvent, extract its string value
        if isinstance(event, ListeningEvent):
            event = event.value

        # Validate that the event name is a non-empty string
        if not isinstance(event, str) or not event.strip():
            raise CLIOrionisValueError("Event name must be a non-empty string.")

        # Validate that the listener is either callable or an instance of IScheduleEventListener
        if not callable(listener) and not isinstance(listener, IScheduleEventListener):
            raise CLIOrionisValueError(
                "Listener must be a callable function or an instance of IScheduleEventListener."
            )

        # Register the listener for the specified event in the internal listeners dictionary
        self.__listeners[event] = listener

    def pause(
        self
    ) -> None:
        """
        Pause all user jobs managed by the scheduler.

        This method pauses all currently scheduled user jobs in the AsyncIOScheduler if the scheduler is running.
        It iterates through all jobs, attempts to pause each one, and tracks which jobs were paused by adding their
        IDs to an internal set. For each successfully paused job, the method logs the action and invokes any
        registered listeners for the pause event. After all jobs are paused, a global listener for the scheduler
        pause event is also invoked.

        Returns
        -------
        None
            This method does not return any value. It performs the pausing of all user jobs and triggers
            the appropriate listeners and logging.

        Notes
        -----
        - Only jobs with valid IDs are paused.
        - System jobs are not explicitly filtered out; all jobs returned by the scheduler are considered user jobs.
        - If an error occurs while pausing a job, the exception is handled by the application's error handler.
        - The set of paused jobs is cleared before pausing to ensure only currently paused jobs are tracked.
        """

        # Only pause jobs if the scheduler is currently running
        if self.isRunning():

            # Retrieve all jobs currently managed by the scheduler
            all_jobs = self.__scheduler.get_jobs()

            # Iterate through each job and attempt to pause it
            for job in all_jobs:

                try:

                    # Get the job ID safely
                    job_id = self.__getAttribute(job, 'id', None)

                    # Skip jobs without a valid user-defined ID (ignore system/operation jobs)
                    if not job_id or not isinstance(job_id, str) or job_id.strip() == "":
                        continue

                    # Retrieve event data for the paused job
                    event_data = self.__getTaskFromSchedulerById(job_id)

                    # Invoke the listener for the paused job event
                    self.__taskCallableListener(
                        event_data,
                        ListeningEvent.JOB_ON_PAUSED
                    )

                except Exception as e:

                    # Handle any errors that occur while pausing a job
                    self.__raiseException(e)

            # After all jobs are paused, invoke the global listener for scheduler pause
            self.__globalCallableListener(SchedulerPaused(
                code=EVENT_SCHEDULER_PAUSED,
                time=self.__getNow()
            ), ListeningEvent.SCHEDULER_PAUSED)

            # Get the current time in the configured timezone for logging
            now = self.__getCurrentTime()

            # Clear the set of previously paused jobs to avoid stale entries
            self.__scheduler.pause()

            # Store the timestamp when the scheduler was paused
            self.__paused_at = self.__getNow()

            # Log that all tasks have been paused
            self.__logger.info(f"Orionis Scheduler paused all tasks successfully at: {now}.")

    def resume(
        self
    ) -> None:
        """
        Resume all user jobs that were previously paused by the scheduler.

        This method resumes only those jobs that were paused using the `pause` method,
        as tracked by the internal set `__pausedByPauseEverything`. It iterates through
        each paused job, attempts to resume it, and triggers any registered listeners
        for the resumed job event. After all jobs are resumed, a global listener for the
        scheduler resume event is also invoked. The set of paused jobs is cleared after
        resumption to ensure accurate tracking.

        Returns
        -------
        None
            This method does not return any value. It resumes all jobs that were paused
            by the scheduler, triggers the appropriate listeners, and logs the actions.

        Notes
        -----
        - Only jobs that were paused by the `pause` method are resumed.
        - If an error occurs while resuming a job, the exception is handled by the application's error handler.
        - After resuming all jobs, the global scheduler resumed event is triggered.
        """

        # Only resume jobs if the scheduler is currently running
        if self.isPaused():

            # Execute the global callable listener after all jobs are resumed
            self.__globalCallableListener(SchedulerResumed(
                code=EVENT_SCHEDULER_RESUMED,
                time=self.__getNow()
            ), ListeningEvent.SCHEDULER_RESUMED)

            # Get the current time in the configured timezone for logging
            now = self.__getCurrentTime()

            # Cuando resumes:
            resumed_at = self.__getNow()

            # Resume main scheduler
            self.__scheduler.resume()

            # Iterate through all jobs to check for missed executions
            for job in self.__scheduler.get_jobs():

                # If the job was supposed to run while paused, trigger the missed event
                if job.next_run_time and self.__paused_at <= job.next_run_time < resumed_at:

                    # Retrieve event data for the missed job
                    event_data = self.__getTaskFromSchedulerById(job.id)

                    # Invoke the listener for the missed job event
                    self.__taskCallableListener(
                        event_data,
                        ListeningEvent.JOB_ON_MISSED
                    )

            # Log an informational message indicating that the scheduler has been resumed
            self.__logger.info(f"Orionis Scheduler resumed all tasks successfully at: {now}.")

    async def start(
        self
    ) -> None:
        """
        Start the AsyncIO scheduler instance and keep it running.

        This method initializes and starts the AsyncIOScheduler, which integrates with the asyncio event loop
        to manage asynchronous job execution. It ensures that all scheduled events are loaded, listeners are
        subscribed, and the scheduler is started within an asyncio context. The method keeps the scheduler
        running until a stop signal is received, handling graceful shutdowns and interruptions.

        Returns
        -------
        None
            This method does not return any value. It starts the AsyncIO scheduler, keeps it running, and
            ensures proper cleanup during shutdown.

        Raises
        ------
        CLIOrionisRuntimeError
            If the scheduler fails to start due to missing an asyncio event loop or other runtime issues.
        """
        try:

            # Ensure the method is called within an asyncio event loop
            asyncio.get_running_loop()

            # Create an asyncio event to manage clean shutdowns
            self._stop_event = asyncio.Event()

            # Load all scheduled events into the internal jobs list
            self.__loadEvents()

            # Subscribe to scheduler events for monitoring and handling
            self.__subscribeListeners()

            # Start the scheduler if it is not already running
            if not self.isRunning():
                self.__scheduler.start()
                self.__control_scheduler.start()

            # Log that the scheduler is now active and waiting for events
            self.__logger.info("Orionis Scheduler is now active and waiting for events...")

            try:
                # Wait for the stop event to be set, which signals a shutdown
                # This avoids using a busy loop and is more efficient
                await self._stop_event.wait()

            except (KeyboardInterrupt, asyncio.CancelledError):

                # Handle graceful shutdown when an interruption signal is received
                self.__logger.info("Received shutdown signal, stopping scheduler...")
                await self.shutdown(wait=True)

            except Exception as e:

                # Log and raise any unexpected exceptions during scheduler operation
                self.__logger.error(f"Error during scheduler operation: {str(e)}")
                raise CLIOrionisRuntimeError(f"Scheduler operation failed: {str(e)}") from e

            finally:

                # Ensure the scheduler is shut down properly, even if an error occurs
                if self.__scheduler.running:
                    await self.shutdown(wait=False)

        except RuntimeError as e:

            # Handle the case where no asyncio event loop is running
            if "no running event loop" in str(e):
                raise CLIOrionisRuntimeError("Scheduler must be started within an asyncio event loop") from e
            raise CLIOrionisRuntimeError(f"Failed to start the scheduler: {str(e)}") from e

        except Exception as e:

            # Raise a runtime error for any other issues during startup
            raise CLIOrionisRuntimeError(f"Failed to start the scheduler: {str(e)}") from e

    async def shutdown(
        self,
        wait: bool = True
    ) -> None:
        """
        Shut down the AsyncIO scheduler instance asynchronously.

        This method gracefully stops the AsyncIOScheduler and signals the main event loop
        to stop waiting, allowing for clean application shutdown.

        Parameters
        ----------
        wait : bool, optional
            If True, waits for currently executing jobs to complete. Default is True.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the 'wait' parameter is not a boolean value.
        CLIOrionisRuntimeError
            If an error occurs during the shutdown process.
        """

        # Validate the wait parameter
        if not isinstance(wait, bool):
            self.__raiseException(
                CLIOrionisValueError(
                    "The 'wait' parameter must be a boolean value (True or False) to indicate whether to wait for running jobs to finish before shutting down the scheduler."
                )
            )

        # If the scheduler is not running, there's nothing to shut down
        if not self.isRunning():
            return

        try:

            # Shut down the AsyncIOScheduler
            self.__scheduler.shutdown(wait=wait)
            self.__control_scheduler.shutdown(wait=wait)

            # Signal the stop event to break the wait in start()
            if self._stop_event and not self._stop_event.is_set():
                self._stop_event.set()

            # Allow time for cleanup if waiting
            if wait:
                await asyncio.sleep(0.1)

            # Get the current time in the configured timezone for logging
            now = self.__getCurrentTime()

            # Log the successful shutdown
            self.__logger.info(f"Orionis Scheduler has been shut down successfully at: {now}.")

        except Exception as e:

            # Handle exceptions that may occur during shutdown
            self.__raiseException(
                CLIOrionisRuntimeError(
                    f"Error while attempting to shut down Orionis Scheduler: {str(e)}"
                )
            )

    def pauseCommand(
        self,
        signature: str
    ) -> bool:
        """
        Pause a scheduled job in the AsyncIO scheduler.

        This method attempts to pause a job managed by the AsyncIOScheduler, identified by its unique signature.
        It first validates that the provided signature is a non-empty string. If the job exists and is successfully
        paused, the method logs the action and returns True. If the job does not exist or an error occurs during
        the pause operation, the method returns False.

        Parameters
        ----------
        signature : str
            The unique signature (ID) of the job to pause. Must be a non-empty string.

        Returns
        -------
        bool
            True if the job was successfully paused.
            False if the job does not exist or an error occurred during the pause operation.

        Raises
        ------
        CLIOrionisValueError
            If the `signature` parameter is not a non-empty string.

        Notes
        -----
        This method is intended for use with jobs managed by the AsyncIOScheduler. It does not raise
        an exception if the job does not exist; instead, it returns False to indicate failure.
        """

        # Validate that the signature is a non-empty string
        if not isinstance(signature, str) or not signature.strip():
            self.__raiseException(CLIOrionisValueError(self.SIGNATURE_REQUIRED_ERROR))

        try:

            # Attempt to pause the job with the given signature
            self.__scheduler.pause_job(signature)

            # Retrieve event data for the paused job
            event_data = self.__getTaskFromSchedulerById(signature)

            # Invoke the listener for the paused job event
            self.__taskCallableListener(
                event_data,
                ListeningEvent.JOB_ON_PAUSED
            )

            # Log the successful pausing of the job
            self.__logger.info(f"Pause '{signature}' has been paused.")

            # Return True to indicate the job was successfully paused
            return True

        except Exception:

            # Return False if the job could not be paused (e.g., it does not exist or another error occurred)
            return False

    def resumeCommand(
        self,
        signature: str
    ) -> bool:
        """
        Resume a paused job in the AsyncIO scheduler.

        This method attempts to resume a job that was previously paused in the AsyncIOScheduler.
        It first validates that the provided job signature is a non-empty string. If the job exists
        and is currently paused, the method resumes the job, logs the action, and returns True.
        If the job does not exist or an error occurs during the resume operation, the method returns False.

        Parameters
        ----------
        signature : str
            The unique signature (ID) of the job to resume. Must be a non-empty string.

        Returns
        -------
        bool
            True if the job was successfully resumed.
            False if the job does not exist or an error occurred during the resume operation.

        Raises
        ------
        CLIOrionisValueError
            If the `signature` parameter is not a non-empty string.

        Notes
        -----
        This method is intended for use with jobs managed by the AsyncIOScheduler. It does not raise
        an exception if the job does not exist; instead, it returns False to indicate failure.
        """

        # Validate that the signature is a non-empty string
        if not isinstance(signature, str) or not signature.strip():
            self.__raiseException(CLIOrionisValueError(self.SIGNATURE_REQUIRED_ERROR))

        try:

            # Attempt to resume the job with the given signature
            self.__scheduler.resume_job(signature)

            # Retrieve event data for the resumed job
            event_data = self.__getTaskFromSchedulerById(signature)

            # Invoke the listener for the resumed job event
            self.__taskCallableListener(
                event_data,
                ListeningEvent.JOB_ON_RESUMED
            )

            # Log the successful resumption of the job
            self.__logger.info(f"Task '{signature}' has been resumed.")

            # Return True to indicate the job was successfully resumed
            return True

        except Exception:

            # Return False if the job could not be resumed (e.g., it does not exist or another error occurred)
            return False

    def removeCommand(
        self,
        signature: str
    ) -> bool:
        """
        Remove a scheduled job from the AsyncIO scheduler by its signature.

        This method attempts to remove a job from the AsyncIOScheduler using its unique signature (ID).
        It first validates that the provided signature is a non-empty string. If the job exists,
        it is removed from both the scheduler and the internal jobs list. The method logs the removal
        and returns True if successful. If the job does not exist or an error occurs during removal,
        the method returns False.

        Parameters
        ----------
        signature : str
            The unique signature (ID) of the job to remove. Must be a non-empty string.

        Returns
        -------
        bool
            True if the job was successfully removed from both the scheduler and the internal jobs list.
            False if the job does not exist or an error occurred during removal.

        Raises
        ------
        CLIOrionisValueError
            If the `signature` parameter is not a non-empty string.

        Notes
        -----
        This method ensures that both the scheduler and the internal jobs list remain consistent
        after a job is removed. No exception is raised if the job does not exist; instead, False is returned.
        """

        # Validate that the signature is a non-empty string
        if not isinstance(signature, str) or not signature.strip():
            self.__raiseException(CLIOrionisValueError(self.SIGNATURE_REQUIRED_ERROR))

        try:

            # Attempt to remove the job from the scheduler using its signature
            self.__scheduler.remove_job(signature)

            # Remove the job from the internal jobs list if it exists
            for job in self.__jobs:
                if job.signature == signature:
                    self.__jobs.remove(job)
                    break

            # Log the successful removal of the job
            self.__logger.info(f"Task '{signature}' has been removed from the scheduler.")

            # Return True to indicate the job was successfully removed
            return True

        except Exception:

            # Return False if the job could not be removed (e.g., it does not exist or another error occurred)
            return False

    def events(
        self
    ) -> List[Dict]:
        """
        Retrieve a list of all scheduled jobs managed by the scheduler.

        This method ensures that all scheduled events are loaded into the internal jobs list,
        then iterates through each job to collect its details in a dictionary format. Each
        dictionary contains information such as the command signature, arguments, purpose,
        random delay, start and end dates, and any additional job details.

        Returns
        -------
        List[dict]
            A list of dictionaries, where each dictionary represents a scheduled job and contains:
                - 'signature' (str): The command signature of the job.
                - 'args' (list): The arguments passed to the command.
                - 'purpose' (str): The description or purpose of the job.
                - 'random_delay' (int): The random delay associated with the job, if any.
                - 'start_date' (str): The formatted start date and time of the job, or 'Not Applicable' if not set.
                - 'end_date' (str): The formatted end date and time of the job, or 'Not Applicable' if not set.
                - 'details' (str): Additional details about the job.
        Notes
        -----
        This method guarantees that the returned list reflects the current state of all jobs
        managed by this scheduler instance. If no jobs are scheduled, an empty list is returned.
        """

        # Ensure all events are loaded into the internal jobs list
        self.__loadEvents()

        # Initialize a list to hold details of each scheduled job
        events: list = []

        # Iterate over each job in the internal jobs list
        for job in self.__jobs:

            # Safely extract job details with default values if attributes are missing
            signature: str = self.__getAttribute(job, 'signature', '')
            args: list = self.__getAttribute(job, 'args', [])
            purpose: str = self.__getAttribute(job, 'purpose', 'No Description')
            random_delay: int = self.__getAttribute(job, 'random_delay', 0)
            start_date: datetime = self.__getAttribute(job, 'start_date', None)
            end_date: datetime = self.__getAttribute(job, 'end_date', None)
            details: str = self.__getAttribute(job, 'details', 'Not Available')
            coalesce: bool = self.__getAttribute(job, 'coalesce', False)
            max_instances: int = self.__getAttribute(job, 'max_instances', 1)
            misfire_grace_time: int = self.__getAttribute(job, 'misfire_grace_time', None)

            # Format the start and end dates as strings, or mark as 'Not Applicable' if not set
            formatted_start = start_date.strftime('%Y-%m-%d %H:%M:%S') if start_date else self.NOT_APPLICABLE
            formatted_end = end_date.strftime('%Y-%m-%d %H:%M:%S') if end_date else self.NOT_APPLICABLE

            # Append a dictionary with relevant job details to the events list
            events.append({
                'signature': signature,
                'args': args,
                'purpose': purpose,
                'random_delay': random_delay,
                'start_date': formatted_start,
                'end_date': formatted_end,
                'details': details,
                'coalesce': coalesce,
                'max_instances': max_instances,
                'misfire_grace_time': misfire_grace_time
            })

        # Return the list of scheduled job details
        return events

    def event(
        self,
        signature: str
    ) -> Optional[Dict]:
        """
        Retrieve the details of a specific scheduled job by its signature.

        This method searches the internal jobs list for a job whose signature matches
        the provided value. If a matching job is found, it returns a dictionary containing
        the job's details, such as its arguments, purpose, random delay, start and end dates,
        and additional details. If no job with the given signature exists, the method returns None.

        Parameters
        ----------
        signature : str
            The unique signature (ID) of the job to retrieve. Must be a non-empty string.

        Returns
        -------
        dict or None
            If a job with the specified signature is found, returns a dictionary with the following keys:
                - 'signature': str, the job's signature.
                - 'args': list, the arguments passed to the job.
                - 'purpose': str, the description or purpose of the job.
                - 'random_delay': int, the random delay associated with the job (if any).
                - 'start_date': str, the formatted start date and time of the job, or 'Not Applicable' if not set.
                - 'end_date': str, the formatted end date and time of the job, or 'Not Applicable' if not set.
                - 'details': str, additional details about the job.
            If no job with the given signature is found, returns None.

        Notes
        -----
        This method ensures that all events are loaded before searching for the job.
        The returned dictionary provides a summary of the job's configuration and metadata.
        """

        # Ensure all events are loaded into the internal jobs list
        self.__loadEvents()

        # Validate the signature parameter
        if not isinstance(signature, str) or not signature.strip():
            return None

        # Search for the job with the matching signature
        for job in self.__jobs:
            # Get the job's signature attribute safely
            job_signature = self.__getAttribute(job, 'signature', '')

            # If a matching job is found, return its details in a dictionary
            if job_signature == signature:

                # Extract job details safely with default values
                args: list = self.__getAttribute(job, 'args', [])
                purpose: str = self.__getAttribute(job, 'purpose', 'No Description')
                random_delay: int = self.__getAttribute(job, 'random_delay', 0)
                start_date: datetime = self.__getAttribute(job, 'start_date', None)
                end_date: datetime = self.__getAttribute(job, 'end_date', None)
                details: str = self.__getAttribute(job, 'details', 'Not Available')

                # Return the job details as a dictionary
                return {
                    'signature': job_signature,
                    'args': args,
                    'purpose': purpose,
                    'random_delay': random_delay,
                    'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S') if start_date else self.NOT_APPLICABLE,
                    'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S') if end_date else self.NOT_APPLICABLE,
                    'details': details
                }

        # Return None if no job with the given signature is found
        return None

    def isRunning(
        self
    ) -> bool:
        """
        Check if the scheduler is currently running.

        This method inspects the internal state of the AsyncIOScheduler instance to determine
        whether the scheduler is actively running. The scheduler is considered running if it
        has been started and has not been paused or shut down.

        Returns
        -------
        bool
            True if the AsyncIOScheduler is currently running; False otherwise.
        """

        # Return True if the scheduler is running, otherwise False
        return self.__scheduler.running and self.__scheduler.state == STATE_RUNNING

    def isPaused(
        self
    ) -> bool:
        """
        Check if the scheduler is currently paused.

        This method determines whether the scheduler is in a paused state by checking if there are
        any jobs that were paused using the `pause` method. If there are jobs in the internal set
        `__pausedByPauseEverything`, it indicates that the scheduler has been paused.

        Returns
        -------
        bool
            True if the scheduler is currently paused (i.e., there are jobs in the paused set);
            False otherwise.
        """

        # The scheduler is considered paused if there are any jobs in the paused set
        return self.__scheduler.running and self.__scheduler.state == STATE_PAUSED

    def forceStop(
        self
    ) -> None:
        """
        Forcefully stop the scheduler immediately, bypassing graceful shutdown.

        This method immediately shuts down the AsyncIOScheduler instance without waiting for any currently
        running jobs to finish. It is intended for emergency or critical situations where an abrupt stop
        is required, such as unrecoverable errors or forced application termination. In addition to shutting
        down the scheduler, it also signals the internal stop event to interrupt the scheduler's main loop,
        allowing the application to proceed with its shutdown procedures.

        Returns
        -------
        None
            This method does not return any value. It performs a forceful shutdown of the scheduler and
            signals the stop event to ensure the main loop is interrupted.

        Notes
        -----
        - This method should be used with caution, as it does not wait for running jobs to complete.
        - After calling this method, the scheduler will be stopped and any pending or running jobs may be interrupted.
        """

        # If the scheduler is currently running, shut it down immediately without waiting for jobs to finish
        if self.__scheduler.running:
            self.__scheduler.shutdown(wait=False)
            self.__control_scheduler.shutdown(wait=False)

        # If the stop event exists and has not already been set, signal it to interrupt the main loop
        if self._stop_event and not self._stop_event.is_set():
            self._stop_event.set()

    def stop(
        self
    ) -> None:
        """
        Signal the scheduler to stop synchronously by setting the internal stop event.

        This method is used to request a graceful shutdown of the scheduler from a synchronous context.
        It sets the internal asyncio stop event, which will cause the scheduler's main loop to exit.
        If an asyncio event loop is currently running, the stop event is set in a thread-safe manner
        using `call_soon_threadsafe`. If no event loop is running, the stop event is set directly.
        This method is safe to call from both asynchronous and synchronous contexts.

        Returns
        -------
        None
            This method does not return any value. It only signals the scheduler to stop by setting
            the internal stop event.

        Notes
        -----
        - If the stop event is already set or does not exist, this method does nothing.
        - Any exceptions encountered while setting the stop event are logged as warnings, but the
          method will still attempt to set the event directly.
        """
        # Check if the stop event exists and has not already been set
        if self._stop_event and not self._stop_event.is_set():

            try:

                # Try to get the current running event loop
                loop = asyncio.get_running_loop()

                # If the event loop is running, set the stop event in a thread-safe manner
                loop.call_soon_threadsafe(self._stop_event.set)

            except RuntimeError:

                # No running event loop, set the stop event directly
                self._stop_event.set()

            except Exception as e:

                # Log any unexpected error but still try to set the event directly
                self.__logger.warning(f"Error setting stop event through event loop: {str(e)}")
                self._stop_event.set()