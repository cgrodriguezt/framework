from rich.console import Console
from rich.panel import Panel
from orionis.console.base.command import BaseCommand
from orionis.console.contracts.schedule import ISchedule
from orionis.console.enums.listener import ListeningEvent
from orionis.console.exceptions import CLIOrionisException, CLIOrionisValueError
from orionis.foundation.contracts.application import IApplication
from orionis.services.introspection.instances.reflection import ReflectionInstance

class ScheduleWorkCommand(BaseCommand):

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "schedule:work"

    # Command description
    description: str = "Executes the scheduled tasks defined in the application."

    async def handle(self, app: IApplication, console: Console) -> None:
        """
        Run the application's scheduled tasks worker.

        Retrieve the Scheduler instance, register scheduled tasks, set event
        listeners if available, and start the scheduler worker asynchronously.
        Report errors as CLIOrionisRuntimeError.

        Parameters
        ----------
        app : IApplication
            Application instance for configuration and service resolution.
        console : Console
            Rich console instance for output.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        CLIOrionisRuntimeError
            If the scheduler or its methods are missing, or on unexpected error.
        """
        try:

            # Retrieve the Scheduler instance from the application
            scheduler = app.getScheduler()

            # Create a reflection instance for method inspection
            rf_scheduler = ReflectionInstance(scheduler)

            # Check if the Scheduler class defines the 'tasks' method
            if not rf_scheduler.hasMethod("tasks"):
                error_msg = (
                    "The 'tasks' method was not found in the Scheduler class. "
                    "Please ensure your Scheduler class defines a "
                    "'tasks(self, schedule: ISchedule)' method to register "
                    "scheduled tasks."
                )
                raise ValueError(error_msg)

            # Create an instance of the ISchedule service
            schedule_service: ISchedule = app.make(ISchedule)

            # Register scheduled tasks using the Scheduler's tasks method
            app.call(scheduler, "tasks", schedule_service)

            # Retrieve the list of scheduled jobs/events
            list_tasks = schedule_service.events()

            # Display a message if no scheduled jobs are found
            if not list_tasks:

                # Print a message indicating no scheduled jobs are found
                console.line()
                console.print(
                    Panel(
                        "No scheduled jobs found.",
                        border_style="green",
                    ),
                )
                console.line()
                return

            # Register event listeners if the scheduler defines them

            # Listener for scheduler started event
            if rf_scheduler.hasMethod("onStarted"):
                schedule_service.setListener(
                    ListeningEvent.SCHEDULER_STARTED,
                    scheduler.onStarted,
                )

            # Listener for scheduler paused event
            if rf_scheduler.hasMethod("onPaused"):
                schedule_service.setListener(
                    ListeningEvent.SCHEDULER_PAUSED,
                    scheduler.onPaused,
                )

            # Listener for scheduler resumed event
            if rf_scheduler.hasMethod("onResumed"):
                schedule_service.setListener(
                    ListeningEvent.SCHEDULER_RESUMED,
                    scheduler.onResumed,
                )

            # Listener for scheduler shutdown event
            if rf_scheduler.hasMethod("onFinalized"):
                schedule_service.setListener(
                    ListeningEvent.SCHEDULER_SHUTDOWN,
                    scheduler.onFinalized,
                )

            # Listener for scheduler error event
            if rf_scheduler.hasMethod("onError"):
                schedule_service.setListener(
                    ListeningEvent.SCHEDULER_ERROR,
                    scheduler.onError,
                )

            # Start the scheduler worker asynchronously
            await schedule_service.start()

        except ValueError as ve:

            # Raise ValueErrors as CLIOrionisException
            error_msg = (
                f"Error starting the scheduler worker: {ve}"
            )
            raise CLIOrionisValueError(error_msg) from ve

        except Exception as e:

            # Raise any unexpected exceptions as CLIOrionisRuntimeError
            error_msg = (
                f"An unexpected error occurred while starting the scheduler: {e}"
            )
            raise CLIOrionisException(error_msg) from e
