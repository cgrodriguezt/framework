import asyncio
from datetime import datetime
import logging
from typing import Dict, List, Optional
import pytz
from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_JOB_SUBMITTED,
    EVENT_SCHEDULER_PAUSED,
    EVENT_SCHEDULER_RESUMED,
    EVENT_SCHEDULER_SHUTDOWN,
    EVENT_SCHEDULER_STARTED,
    EVENT_JOB_MAX_INSTANCES
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler as APSAsyncIOScheduler
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from orionis.console.contracts.reactor import IReactor
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.job_error import JobError
from orionis.console.entities.job_executed import JobExecuted
from orionis.console.entities.job_max_instances import JobMaxInstances
from orionis.console.entities.job_missed import JobMissed
from orionis.console.entities.job_submitted import JobSubmitted
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted
from orionis.console.enums.listener import ListeningEvent
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.console.output.contracts.console import IConsole
from orionis.console.tasks.event import Event
from orionis.foundation.contracts.application import IApplication
from orionis.services.log.contracts.log_service import ILogger

class Scheduler(ISchedule):

    def __init__(
        self,
        reactor: IReactor,
        app: IApplication,
        console: IConsole,
        rich_console: Console
    ) -> None:
        """
        Initialize a new instance of the Scheduler class.

        This constructor sets up the internal state required for scheduling commands,
        including references to the application instance, AsyncIOScheduler, the
        command reactor, and job tracking structures. It also initializes properties
        for managing the current scheduling context.

        Parameters
        ----------
        reactor : IReactor
            An instance of a class implementing the IReactor interface, used to
            retrieve available commands and execute scheduled jobs.

        Returns
        -------
        None
            This method does not return any value. It initializes the Scheduler instance.
        """

        # Store the application instance for configuration access.
        self.__app = app

        # Store the console instance for output operations.
        self.__console = console

        # Store the rich console instance for advanced output formatting.
        self.__rich_console = rich_console

        # Initialize AsyncIOScheduler instance with timezone configuration.
        self.__scheduler: APSAsyncIOScheduler = APSAsyncIOScheduler(
            timezone=pytz.timezone(self.__app.config('app.timezone', 'UTC'))
        )

        # Clear the APScheduler logger to prevent conflicts with other loggers.
        # This is necessary to avoid duplicate log messages or conflicts with other logging configurations.
        for name in ["apscheduler", "apscheduler.scheduler", "apscheduler.executors.default"]:
            logger = logging.getLogger(name)
            logger.handlers.clear()
            logger.propagate = False
            logger.disabled = True

        # Initialize the logger from the application instance.
        self.__logger: ILogger = self.__app.make('x-orionis.services.log.log_service')

        # Store the reactor instance for command management.
        self.__reactor = reactor

        # Retrieve and store all available commands from the reactor.
        self.__available_commands = self.__getCommands()

        # Initialize the jobs dictionary to keep track of scheduled jobs.
        self.__events: Dict[str, Event] = {}

        # Initialize the jobs list to keep track of all scheduled jobs.
        self.__jobs: List[dict] = []

        # Initialize the listeners dictionary to manage event listeners.
        self.__listeners: Dict[str, callable] = {}

    def __getCurrentTime(
        self
    ) -> str:
        """
        Get the current date and time formatted as a string.

        This method retrieves the current date and time in the timezone configured
        for the application and formats it as a string in the "YYYY-MM-DD HH:MM:SS" format.

        Returns
        -------
        str
            A string representing the current date and time in the configured timezone,
            formatted as "YYYY-MM-DD HH:MM:SS".
        """

        # Get the current time in the configured timezone
        now = pytz.timezone(self.__app.config('app.timezone', 'UTC')).localize(
            pytz.datetime.datetime.now()
        )

        # Return the formatted date and time string
        return now.strftime('%Y-%m-%d %H:%M:%S')

    def __suscribeListeners(
        self
    ) -> None:
        """
        Subscribe to scheduler events for monitoring and handling.

        This method sets up event listeners for the AsyncIOScheduler instance to monitor
        various scheduler events such as scheduler start, shutdown, pause, resume, job submission,
        execution, missed jobs, and errors. Each listener is associated with a specific event type
        and is responsible for handling the corresponding event.

        The listeners log relevant information, invoke registered callbacks, and handle errors
        or missed jobs as needed. This ensures that the scheduler's state and job execution
        are monitored effectively.

        Returns
        -------
        None
            This method does not return any value. It configures event listeners on the scheduler.
        """

        # Add a listener for the scheduler started event
        self.__scheduler.add_listener(self.__startedListener, EVENT_SCHEDULER_STARTED)

        # Add a listener for the scheduler shutdown event
        self.__scheduler.add_listener(self.__shutdownListener, EVENT_SCHEDULER_SHUTDOWN)

        # Add a listener for the scheduler paused event
        self.__scheduler.add_listener(self.__pausedListener, EVENT_SCHEDULER_PAUSED)

        # Add a listener for the scheduler resumed event
        self.__scheduler.add_listener(self.__resumedListener, EVENT_SCHEDULER_RESUMED)

        # Add a listener for job submission events
        self.__scheduler.add_listener(self.__submittedListener, EVENT_JOB_SUBMITTED)

        # Add a listener for job execution events
        self.__scheduler.add_listener(self.__executedListener, EVENT_JOB_EXECUTED)

        # Add a listener for missed job events
        self.__scheduler.add_listener(self.__missedListener, EVENT_JOB_MISSED)

        # Add a listener for job error events
        self.__scheduler.add_listener(self.__errorListener, EVENT_JOB_ERROR)

        # Add a listener for job max instances events
        self.__scheduler.add_listener(self.__maxInstancesListener, EVENT_JOB_MAX_INSTANCES)

    def __startedListener(
        self,
        event: SchedulerStarted
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

        # Log an informational message indicating that the scheduler has started
        self.__logger.info(f"Orionis Scheduler started successfully at {now}.")

        # Display a start message for the scheduler worker on the rich console
        # Add a blank line for better formatting
        if self.__app.config('app.debug', False):
            self.__rich_console.line()
            panel_content = Text.assemble(
                (" Orionis Scheduler Worker ", "bold white on green"),                      # Header text with styling
                ("\n\n", ""),                                                               # Add spacing
                ("The scheduled tasks worker has started successfully.\n", "white"),        # Main message
                (f"Started at: {now}\n", "dim"),                                            # Display the start time in dim text
                ("To stop the worker, press ", "white"),                                    # Instruction text
                ("Ctrl+C", "bold yellow"),                                                  # Highlight the key combination
                (".", "white")                                                              # End the instruction
            )

            # Display the message in a styled panel
            self.__rich_console.print(
                Panel(panel_content, border_style="green", padding=(1, 2))
            )

            # Add another blank line for better formatting
            self.__rich_console.line()

        # Retrieve the global identifier for the scheduler started event
        scheduler_started = ListeningEvent.SCHEDULER_STARTED.value

        # Check if a listener is registered for the scheduler started event
        if scheduler_started in self.__listeners:
            listener = self.__listeners[scheduler_started]

            # Ensure the listener is callable before invoking it
            if callable(listener):

                # Invoke the registered listener with the event details
                listener(event)

    def __shutdownListener(
        self,
        event: SchedulerShutdown
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

        # Create a shutdown message
        message = f"Orionis Scheduler shut down successfully at {now}."

        # Log an informational message indicating that the scheduler has shut down
        self.__logger.info(message)

        # Display a shutdown message for the scheduler worker on console
        if self.__app.config('app.debug', False):
            self.__console.info(message)

        # Retrieve the global identifier for the scheduler shutdown event
        scheduler_shutdown = GlobalListener.SCHEDULER_SHUTDOWN.value

        # Check if a listener is registered for the scheduler shutdown event
        if scheduler_shutdown in self.__listeners:
            listener = self.__listeners[scheduler_shutdown]

            # Ensure the listener is callable before invoking it
            if callable(listener):
                # Invoke the registered listener with the event details
                listener(event)

    def __pausedListener(
        self,
        event: SchedulerPaused
    ) -> None:
        """
        Handle the scheduler paused event for logging and invoking registered listeners.

        This method is triggered when the scheduler is paused. It logs an informational
        message indicating that the scheduler has been paused successfully and displays
        a formatted message on the rich console. If a listener is registered for the
        scheduler paused event, it invokes the listener with the event details.

        Parameters
        ----------
        event : SchedulerPaused
            An event object containing details about the scheduler paused event.

        Returns
        -------
        None
            This method does not return any value. It performs logging, displays
            a message on the console, and invokes any registered listener for the
            scheduler paused event.
        """

        # Get the current time in the configured timezone
        now = self.__getCurrentTime()

        # Create a paused message
        message = f"Orionis Scheduler paused successfully at {now}."

        # Log an informational message indicating that the scheduler has been paused
        self.__logger.info(message)

        # Display a paused message for the scheduler worker on console
        if self.__app.config('app.debug', False):
            self.__console.info(message)

        # Retrieve the global identifier for the scheduler paused event
        scheduler_paused = GlobalListener.SCHEDULER_PAUSED.value

        # Check if a listener is registered for the scheduler paused event
        if scheduler_paused in self.__listeners:
            listener = self.__listeners[scheduler_paused]

            # Ensure the listener is callable before invoking it
            if callable(listener):
                # Invoke the registered listener with the event details
                listener(event)

    def __resumedListener(
        self,
        event: SchedulerResumed
    ) -> None:
        """
        Handle the scheduler resumed event for logging and invoking registered listeners.

        This method is triggered when the scheduler resumes from a paused state. It logs an informational
        message indicating that the scheduler has resumed successfully and displays a formatted message
        on the rich console. If a listener is registered for the scheduler resumed event, it invokes
        the listener with the event details.

        Parameters
        ----------
        event : SchedulerResumed
            An event object containing details about the scheduler resumed event.

        Returns
        -------
        None
            This method does not return any value. It performs logging, displays
            a message on the console, and invokes any registered listener for the
            scheduler resumed event.
        """

        # Get the current time in the configured timezone
        now = self.__getCurrentTime()

        # Create a resumed message
        message = f"Orionis Scheduler resumed successfully at {now}."

        # Log an informational message indicating that the scheduler has resumed
        self.__logger.info(message)

        # Display a resumed message for the scheduler worker on console
        if self.__app.config('app.debug', False):
            self.__console.info(message)

        # Retrieve the global identifier for the scheduler resumed event
        scheduler_resumed = GlobalListener.SCHEDULER_RESUMED.value

        # Check if a listener is registered for the scheduler resumed event
        if scheduler_resumed in self.__listeners:
            listener = self.__listeners[scheduler_resumed]

            # Ensure the listener is callable before invoking it
            if callable(listener):
                # Invoke the registered listener with the event details
                listener(event)

    def __submittedListener(
        self,
        event: JobSubmitted
    ) -> None:
        """
        Handle job submission events for logging and error reporting.

        This method is triggered when a job is submitted to its executor. It logs an informational
        message indicating that the job has been submitted successfully. If the application is in
        debug mode, it also displays a message on the console. Additionally, if a listener is
        registered for the submitted job, it invokes the listener with the event details.

        Parameters
        ----------
        event : JobSubmitted
            An instance of the JobSubmitted containing details about the submitted job,
            including its ID and scheduled run times.

        Returns
        -------
        None
            This method does not return any value. It performs logging, error reporting,
            and listener invocation for the job submission event.
        """

        # Create a submission message
        message = f"Task {event.job_id} submitted to executor."

        # Log an informational message indicating that the job has been submitted
        self.__logger.info(message)

        # If the application is in debug mode, display a message on the console
        if self.__app.config('app.debug', False):
            self.__console.info(message)

        # If a listener is registered for this job ID, invoke the listener with the event details
        if event.job_id in self.__listeners:
            listener = self.__listeners[event.job_id]

            # Ensure the listener is callable before invoking it
            if callable(listener):

                # Invoke the registered listener with the event details
                listener(event)

    def __executedListener(
        self,
        event: JobExecuted
    ) -> None:
        """
        Handle job execution events for logging and error reporting.

        This method is triggered when a job is executed by its executor. It logs an informational
        message indicating that the job has been executed successfully. If the application is in
        debug mode, it also displays a message on the console. If the job execution resulted in
        an exception, it logs the error and reports it using the error reporter. Additionally,
        if a listener is registered for the executed job, it invokes the listener with the event details.

        Parameters
        ----------
        event : JobExecuted
            An instance of the JobExecuted containing details about the executed job,
            including its ID, return value, exception (if any), and traceback.

        Returns
        -------
        None
            This method does not return any value. It performs logging, error reporting,
            and listener invocation for the job execution event.
        """

        # Create an execution message
        message = f"Task {event.job_id} executed."

        # Log an informational message indicating that the job has been executed
        self.__logger.info(message)

        # If the application is in debug mode, display a message on the console
        if self.__app.config('app.debug', False):
            self.__console.info(message)

        # If a listener is registered for this job ID, invoke the listener with the event details
        if event.job_id in self.__listeners:
            listener = self.__listeners[event.job_id]

            # Ensure the listener is callable before invoking it
            if callable(listener):

                # Invoke the registered listener with the event details
                listener(event)

    def __missedListener(
        self,
        event: JobMissed
    ) -> None:
        """
        Handle job missed events for debugging and error reporting.

        This method is triggered when a scheduled job is missed. It logs a warning
        message indicating the missed job and its scheduled run time. If the application
        is in debug mode, it reports the missed job using the error reporter. Additionally,
        if a listener is registered for the missed job, it invokes the listener with the
        event details.

        Parameters
        ----------
        event : JobMissed
            An instance of the JobMissed event containing details about the missed job,
            including its ID and scheduled run time.

        Returns
        -------
        None
            This method does not return any value. It performs logging, error reporting,
            and listener invocation for the missed job event.
        """

        # Create a missed job message
        message = f"Task {event.job_id} was missed. It was scheduled to run at {event.scheduled_run_time}."

        # Log a warning indicating that the job was missed
        self.__logger.warning(message)

        # If the application is in debug mode, report the missed job using the error reporter
        if self.__app.config('app.debug', False):
            self.__console.warning(message)

        # If a listener is registered for this job ID, invoke the listener with the event details
        if event.job_id in self.__listeners:
            listener = self.__listeners[event.job_id]

            # Ensure the listener is callable before invoking it
            if callable(listener):

                # Invoke the registered listener with the event details
                listener(event)

    def __errorListener(
        self,
        event: JobError
    ) -> None:
        """
        Handle job error events for logging and error reporting.

        This method is triggered when a job execution results in an error. It logs an error
        message indicating the job ID and the exception raised. If the application is in
        debug mode, it also reports the error using the error reporter. Additionally, if a
        listener is registered for the errored job, it invokes the listener with the event details.

        Parameters
        ----------
        event : JobError
            An instance of the JobError event containing details about the errored job,
            including its ID and the exception raised.

        Returns
        -------
        None
            This method does not return any value. It performs logging, error reporting,
            and listener invocation for the job error event.
        """

        # Create an error message
        message = f"Task {event.job_id} raised an exception: {event.exception}"

        # Log an error message indicating that the job raised an exception
        self.__logger.error(message)

        # If the application is in debug mode, display a message on the console
        if self.__app.config('app.debug', False):
            self.__console.error(message)

        # If a listener is registered for this job ID, invoke the listener with the event details
        if event.job_id in self.__listeners:
            listener = self.__listeners[event.job_id]

            # Ensure the listener is callable before invoking it
            if callable(listener):

                # Invoke the registered listener with the event details
                listener(event)

    def __maxInstancesListener(
        self,
        event: JobMaxInstances
    ) -> None:
        """
        Handle job max instances events for logging and error reporting.

        This method is triggered when a job execution exceeds the maximum allowed
        concurrent instances. It logs an error message indicating the job ID and
        the exception raised. If the application is in debug mode, it also reports
        the error using the error reporter. Additionally, if a listener is registered
        for the job that exceeded max instances, it invokes the listener with the event details.

        Parameters
        ----------
        event : JobMaxInstances
            An instance of the JobMaxInstances event containing details about the job that
            exceeded max instances, including its ID and the exception raised.

        Returns
        -------
        None
            This method does not return any value. It performs logging, error reporting,
            and listener invocation for the job max instances event.
        """

        # Create a max instances error message
        message = f"Task {event.job_id} exceeded maximum instances"

        # Log an error message indicating that the job exceeded maximum instances
        self.__logger.error(message)

        # If the application is in debug mode, display a message on the console
        if self.__app.config('app.debug', False):
            self.__console.error(message)

        # If a listener is registered for this job ID, invoke the listener with the event details
        if event.job_id in self.__listeners:
            listener = self.__listeners[event.job_id]

            # Ensure the listener is callable before invoking it
            if callable(listener):

                # Invoke the registered listener with the event details
                listener(event)

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

            # Store each job's signature and description in the commands dictionary
            commands[job['signature']] = {
                'signature': job['signature'],
                'description': job.get('description', '')
            }

        # Return the commands dictionary
        return commands

    def __isAvailable(
        self,
        signature: str
    ) -> bool:
        """
        Check if a command with the given signature is available.

        This method iterates through the available commands and determines
        whether the provided signature matches any registered command.

        Parameters
        ----------
        signature : str
            The signature of the command to check for availability.

        Returns
        -------
        bool
            True if the command with the specified signature exists and is available,
            False otherwise.
        """

        # Iterate through all available command signatures
        for command in self.__available_commands.keys():

            # Return True if the signature matches an available command
            if command == signature:
                return True

        # Return False if the signature is not found among available commands
        return False

    def __getDescription(
        self,
        signature: str
    ) -> Optional[str]:
        """
        Retrieve the description of a command given its signature.

        This method looks up the available commands dictionary and returns the description
        associated with the provided command signature. If the signature does not exist,
        it returns None.

        Parameters
        ----------
        signature : str
            The unique signature identifying the command.

        Returns
        -------
        Optional[str]
            The description of the command if found; otherwise, None.
        """

        # Attempt to retrieve the command entry from the available commands dictionary
        command_entry = self.__available_commands.get(signature)

        # Return the description if the command exists, otherwise return None
        return command_entry['description'] if command_entry else None

    def __loadEvents(
        self
    ) -> None:
        """
        Load all scheduled events from the AsyncIOScheduler into the internal jobs dictionary.

        This method retrieves all jobs currently managed by the AsyncIOScheduler and populates
        the internal jobs dictionary with their details, including signature, arguments, purpose,
        type, trigger, start date, and end date.

        Returns
        -------
        None
            This method does not return any value. It updates the internal jobs dictionary.
        """

        # Only load events if the jobs list is empty
        if not self.__jobs:

            # Iterate through all scheduled jobs in the AsyncIOScheduler
            for signature, event in self.__events.items():

                # Convert the event to its entity representation
                entity = event.toEntity()

                # Add the job to the internal jobs list
                self.__jobs.append(entity.toDict())

                # Create a unique key for the job based on its signature
                self.__scheduler.add_job(
                    func= lambda command=signature, args=list(entity.args): self.__reactor.call(
                        command,
                        args
                    ),
                    trigger=entity.trigger,
                    id=signature,
                    name=signature,
                    replace_existing=True
                )

    def command(
        self,
        signature: str,
        args: Optional[List[str]] = None
    ) -> 'Event':
        """
        Prepare an Event instance for a given command signature and its arguments.

        This method validates the provided command signature and arguments, ensuring
        that the command exists among the registered commands and that the arguments
        are in the correct format. If validation passes, it creates and returns an
        Event object representing the scheduled command, including its signature,
        arguments, and description.

        Parameters
        ----------
        signature : str
            The unique signature identifying the command to be scheduled. Must be a non-empty string.
        args : Optional[List[str]], optional
            A list of string arguments to be passed to the command. Defaults to None.

        Returns
        -------
        Event
            An Event instance containing the command signature, arguments, and its description.

        Raises
        ------
        ValueError
            If the command signature is not a non-empty string, if the arguments are not a list
            of strings or None, or if the command does not exist among the registered commands.
        """

        # Validate that the command signature is a non-empty string
        if not isinstance(signature, str) or not signature.strip():
            raise ValueError("Command signature must be a non-empty string.")

        # Ensure that arguments are either a list of strings or None
        if args is not None and not isinstance(args, list):
            raise ValueError("Arguments must be a list of strings or None.")

        # Check if the command is available in the registered commands
        if not self.__isAvailable(signature):
            raise ValueError(f"The command '{signature}' is not available or does not exist.")

        # Store the command and its arguments for scheduling
        self.__events[signature] = Event(
            signature=signature,
            args=args or [],
            purpose=self.__getDescription(signature)
        )

        # Return the Event instance for further scheduling configuration
        return self.__events[signature]

    def _setListener(
        self,
        event: str,
        listener: callable
    ) -> None:
        """
        Register a listener callback for a specific scheduler event.

        This method allows the registration of a callable listener function that will be
        invoked when the specified scheduler event occurs. The event can be one of the
        predefined global events or a specific job ID. The listener must be a callable
        function that accepts a single argument, which will be the event object.

        Parameters
        ----------
        event : str
            The name of the event to listen for. This can be a global event name (e.g., 'scheduler_started')
            or a specific job ID.
        listener : callable
            A callable function that will be invoked when the specified event occurs.
            The function should accept one parameter, which will be the event object.

        Returns
        -------
        None
            This method does not return any value. It registers the listener for the specified event.

        Raises
        ------
        ValueError
            If the event name is not a non-empty string or if the listener is not callable.
        """

        # Validate that the event name is a non-empty string
        if not isinstance(event, str) or not event.strip():
            raise ValueError("Event name must be a non-empty string.")

        # Validate that the listener is a callable function
        if not callable(listener):
            raise ValueError("Listener must be a callable function.")

        # Register the listener for the specified event
        self.__listeners[event] = listener

    def pauseEverythingAt(
        self,
        at: datetime
    ) -> None:
        """
        Schedule the scheduler to pause all operations at a specific datetime.

        This method allows you to schedule a job that will pause the AsyncIOScheduler
        at the specified datetime. The job is added to the scheduler with a 'date'
        trigger, ensuring it executes exactly at the given time.

        Parameters
        ----------
        at : datetime
            The datetime at which the scheduler should be paused. Must be a valid
            datetime object.

        Returns
        -------
        None
            This method does not return any value. It schedules a job to pause the
            scheduler at the specified datetime.

        Raises
        ------
        ValueError
            If the 'at' parameter is not a valid datetime object.
        """

        # Validate that the 'at' parameter is a datetime object
        if not isinstance(at, datetime):
            raise ValueError("The 'at' parameter must be a datetime object.")

        # Add a job to the scheduler to pause it at the specified datetime
        self.__scheduler.add_job(
            func=self.__scheduler.pause,                    # Function to pause the scheduler
            trigger='date',                                 # Trigger type is 'date' for one-time execution
            run_date=at,                                    # The datetime at which the job will run
            id=f"pause_scheduler_at_{at.isoformat()}",      # Unique job ID based on the datetime
            name=f"Pause Scheduler at {at.isoformat()}",    # Descriptive name for the job
            replace_existing=True                           # Replace any existing job with the same ID
        )

    def resumeEverythingAt(
        self,
        at: datetime
    ) -> None:
        """
        Schedule the scheduler to resume all operations at a specific datetime.

        This method allows you to schedule a job that will resume the AsyncIOScheduler
        at the specified datetime. The job is added to the scheduler with a 'date'
        trigger, ensuring it executes exactly at the given time.

        Parameters
        ----------
        at : datetime
            The datetime at which the scheduler should be resumed. Must be a valid
            datetime object.

        Returns
        -------
        None
            This method does not return any value. It schedules a job to resume the
            scheduler at the specified datetime.

        Raises
        ------
        ValueError
            If the 'at' parameter is not a valid datetime object.
        """

        # Validate that the 'at' parameter is a datetime object
        if not isinstance(at, datetime):
            raise ValueError("The 'at' parameter must be a datetime object.")

        # Add a job to the scheduler to resume it at the specified datetime
        self.__scheduler.add_job(
            func=self.__scheduler.resume,                   # Function to resume the scheduler
            trigger='date',                                 # Trigger type is 'date' for one-time execution
            run_date=at,                                    # The datetime at which the job will run
            id=f"resume_scheduler_at_{at.isoformat()}",     # Unique job ID based on the datetime
            name=f"Resume Scheduler at {at.isoformat()}",   # Descriptive name for the job
            replace_existing=True                           # Replace any existing job with the same ID
        )

    def shutdownEverythingAt(
        self,
        at: datetime
    ) -> None:
        """
        Schedule the scheduler to shut down all operations at a specific datetime.

        This method allows you to schedule a job that will shut down the AsyncIOScheduler
        at the specified datetime. The job is added to the scheduler with a 'date'
        trigger, ensuring it executes exactly at the given time.

        Parameters
        ----------
        at : datetime
            The datetime at which the scheduler should be shut down. Must be a valid
            datetime object.

        Returns
        -------
        None
            This method does not return any value. It schedules a job to shut down the
            scheduler at the specified datetime.

        Raises
        ------
        ValueError
            If the 'at' parameter is not a valid datetime object.
        """

        # Validate that the 'at' parameter is a datetime object
        if not isinstance(at, datetime):
            raise ValueError("The 'at' parameter must be a datetime object.")

        # Add a job to the scheduler to shut it down at the specified datetime
        self.__scheduler.add_job(
            func=self.shutdown,                 # Function to shut down the scheduler
            trigger='date',                                 # Trigger type is 'date' for one-time execution
            run_date=at,                                    # The datetime at which the job will run
            id=f"shutdown_scheduler_at_{at.isoformat()}",   # Unique job ID based on the datetime
            name=f"Shutdown Scheduler at {at.isoformat()}", # Descriptive name for the job
            replace_existing=True                           # Replace any existing job with the same ID
        )

    async def start(self) -> None:
        """
        Start the AsyncIO scheduler instance and keep it running.

        This method initiates the AsyncIOScheduler which integrates with asyncio event loops
        for asynchronous job execution. It ensures the scheduler starts properly within
        an asyncio context and maintains the event loop active to process scheduled jobs.

        Returns
        -------
        None
            This method does not return any value. It starts the AsyncIO scheduler and keeps it running.
        """

        # Start the AsyncIOScheduler to handle asynchronous jobs.
        try:

            # Ensure all events are loaded into the internal jobs list
            self.__loadEvents()

            # Subscribe to scheduler events for monitoring and handling
            self.__suscribeListeners()

            # Ensure we're in an asyncio context
            asyncio.get_running_loop()

            # Start the scheduler
            if not self.__scheduler.running:
                self.__scheduler.start()

            # Keep the event loop alive to process scheduled jobs
            try:

                # Run indefinitely until interrupted
                while self.__scheduler.running and self.__scheduler.get_jobs():
                    await asyncio.sleep(1)

            except (KeyboardInterrupt, asyncio.CancelledError):

                # Handle graceful shutdown on keyboard interrupt or cancellation
                await self.shutdown()

        except Exception as e:

            # Handle exceptions that may occur during scheduler startup
            raise CLIOrionisRuntimeError(f"Failed to start the scheduler: {str(e)}")

    async def shutdown(self, wait=True) -> None:
        """
        Shut down the AsyncIO scheduler instance asynchronously.

        This method gracefully stops the AsyncIOScheduler that handles asynchronous job execution.
        Using async ensures proper cleanup in asyncio environments.

        Parameters
        ----------
        wait : bool, optional
            If True, the method will wait until all currently executing jobs are completed before shutting down the scheduler.
            If False, the scheduler will be shut down immediately without waiting for running jobs to finish. Default is True.

        Returns
        -------
        None
            This method does not return any value. It shuts down the AsyncIO scheduler.
        """

        # Validate that the wait parameter is a boolean.
        if not isinstance(wait, bool):
            raise ValueError("The 'wait' parameter must be a boolean value.")

        try:

            # Shut down the AsyncIOScheduler, waiting for jobs if specified.
            if self.__scheduler.running:

                # For AsyncIOScheduler, shutdown can be called normally
                # but we await any pending operations
                self.__scheduler.shutdown(wait=wait)

                # Give a small delay to ensure proper cleanup
                if wait:
                    await asyncio.sleep(0.1)

        except Exception:

            # AsyncIOScheduler may not be running or may have issues in shutdown
            pass

    async def remove(self, signature: str) -> bool:
        """
        Remove a scheduled job from the AsyncIO scheduler asynchronously.

        This method removes a job with the specified signature from both the internal
        jobs dictionary and the AsyncIOScheduler instance. Using async ensures proper
        cleanup in asyncio environments.

        Parameters
        ----------
        signature : str
            The signature of the command/job to remove from the scheduler.

        Returns
        -------
        bool
            Returns True if the job was successfully removed, False if the job was not found.

        Raises
        ------
        ValueError
            If the signature is not a non-empty string.
        """

        # Validate that the signature is a non-empty string
        if not isinstance(signature, str) or not signature.strip():
            raise ValueError("Signature must be a non-empty string.")

        try:

            # Remove from the scheduler
            self.__scheduler.remove_job(signature)

            # Remove from internal jobs dictionary
            if signature in self.__jobs:
                del self.__jobs[signature]

            # Give a small delay to ensure proper cleanup
            await asyncio.sleep(0.01)

            # Log the removal of the job
            self.__logger.info(f"Job '{signature}' has been removed from the scheduler.")

            # Return True to indicate successful removal
            return True

        except Exception:

            # Job not found or other error
            return False

    def events(self) -> list:
        """
        Retrieve all scheduled jobs currently managed by the Scheduler.

        This method loads and returns a list of dictionaries, each representing a scheduled job
        managed by this Scheduler instance. Each dictionary contains details such as the command
        signature, arguments, purpose, random delay, start and end dates, and additional job details.

        Returns
        -------
        list of dict
            A list where each element is a dictionary containing information about a scheduled job.
            Each dictionary includes the following keys:
                - 'signature': str, the command signature.
                - 'args': list, the arguments passed to the command.
                - 'purpose': str, the description or purpose of the job.
                - 'random_delay': any, the random delay associated with the job (if any).
                - 'start_date': str or None, the formatted start date and time of the job, or None if not set.
                - 'end_date': str or None, the formatted end date and time of the job, or None if not set.
                - 'details': any, additional details about the job.
        """

        # Ensure all events are loaded into the internal jobs list
        self.__loadEvents()

        # Initialize a list to hold details of each scheduled job
        events: list = []

        # Iterate over each job in the internal jobs list
        for job in self.__jobs:
            # Append a dictionary with relevant job details to the events list
            events.append({
                'signature': job['signature'],
                'args': job['args'],
                'purpose': job['purpose'],
                'random_delay': job['random_delay'],
                'start_date': job['start_date'].strftime('%Y-%m-%d %H:%M:%S') if job['start_date'] else None,
                'end_date': job['end_date'].strftime('%Y-%m-%d %H:%M:%S') if job['end_date'] else None,
                'details': job['details']
            })

        # Return the list of scheduled job details
        return events