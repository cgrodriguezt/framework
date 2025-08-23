from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from orionis.console.base.command import BaseCommand
from orionis.console.contracts.schedule import ISchedule
from orionis.console.enums.listener import ListeningEvent
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.container.exceptions.exception import OrionisContainerException
from orionis.foundation.contracts.application import IApplication
from orionis.foundation.exceptions.runtime import OrionisRuntimeError

class ScheduleWorkCommand(BaseCommand):
    """
    Executes the scheduled tasks defined in the application's scheduler.

    This command dynamically loads the scheduler module specified in the application's configuration,
    retrieves the `Scheduler` class and its `tasks` method, registers the scheduled tasks with the
    ISchedule service, and starts the scheduler worker. It provides user feedback via the console and
    handles errors by raising CLIOrionisRuntimeError exceptions.

    Parameters
    ----------
    orionis : IApplication
        The application instance providing configuration and service resolution.
    console : Console
        The Rich console instance used for displaying output to the user.

    Returns
    -------
    bool
        Returns True if the scheduler worker starts successfully. If an error occurs during the process,
        a CLIOrionisRuntimeError is raised.

    Raises
    ------
    CLIOrionisRuntimeError
        If the scheduler module, class, or tasks method cannot be found, or if any unexpected error occurs.
    """

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "schedule:work"

    # Command description
    description: str = "Executes the scheduled tasks defined in the application."

    async def handle(self, app: IApplication, console: Console) -> bool:
        """
        Executes the scheduled tasks defined in the application's scheduler.

        This method retrieves the Scheduler instance from the application, registers scheduled tasks
        with the ISchedule service, and starts the scheduler worker asynchronously. It provides user
        feedback via the console and handles errors by raising CLIOrionisRuntimeError exceptions.

        Parameters
        ----------
        app : IApplication
            The application instance providing configuration and service resolution.
        console : Console
            The Rich console instance used for displaying output to the user.

        Returns
        -------
        bool
            True if the scheduler worker starts successfully.

        Raises
        ------
        CLIOrionisRuntimeError
            If the scheduler module, class, or tasks method cannot be found, or if any unexpected error occurs.
        """
        try:

            # Retrieve the Scheduler instance from the application
            scheduler = app.getScheduler()

            # Create an instance of the ISchedule service
            schedule_service: ISchedule = app.make(ISchedule)

            # Register scheduled tasks using the Scheduler's tasks method
            await scheduler.tasks(schedule_service)

            # Retrieve the list of scheduled jobs/events
            list_tasks = schedule_service.events()

            # Display a message if no scheduled jobs are found
            if not list_tasks:
                console.line()
                console.print(Panel("No scheduled jobs found.", border_style="green"))
                console.line()
                return True

            # If there are scheduled jobs and the scheduler has an onStarted method
            if hasattr(scheduler, "onStarted"):
                schedule_service._setListener(ListeningEvent.SCHEDULER_STARTED.value, scheduler.onStarted)

            # If the scheduler has an onPaused method
            if hasattr(scheduler, "onPaused"):
                schedule_service._setListener(ListeningEvent.SCHEDULER_PAUSED.value, scheduler.onPaused)

            # If the scheduler has an onResumed method
            if hasattr(scheduler, "onResumed"):
                schedule_service._setListener(ListeningEvent.SCHEDULER_RESUMED.value, scheduler.onResumed)

            # If the scheduler has an onFinalized method
            if hasattr(scheduler, "onFinalized"):
                schedule_service._setListener(ListeningEvent.SCHEDULER_SHUTDOWN.value, scheduler.onFinalized)

            # If the scheduler has an onError method
            if hasattr(scheduler, "onError"):
                schedule_service._setListener(ListeningEvent.SCHEDULER_ERROR.value, scheduler.onError)

            # Check if the scheduler has specific pause, resume, and finalize times
            if hasattr(scheduler, "PAUSE_AT") and isinstance(scheduler.PAUSE_AT, datetime):
                schedule_service.pauseEverythingAt(scheduler.PAUSE_AT)

            if hasattr(scheduler, "RESUME_AT") and isinstance(scheduler.RESUME_AT, datetime):
                schedule_service.resumeEverythingAt(scheduler.RESUME_AT)

            if hasattr(scheduler, "FINALIZE_AT") and isinstance(scheduler.FINALIZE_AT, datetime):
                schedule_service.shutdownEverythingAt(scheduler.FINALIZE_AT)

            # Start the scheduler worker asynchronously
            await schedule_service.start()

            # Flag to indicate the scheduler is running
            return True

        except Exception as e:

            # Raise any unexpected exceptions as CLIOrionisRuntimeError
            raise CLIOrionisRuntimeError(
                f"An unexpected error occurred while starting the scheduler worker: {e}"
            )
