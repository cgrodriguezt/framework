from orionis.console.base.command import BaseCommand
from orionis.console.contracts.schedule import ISchedule
from orionis.console.exceptions import CLIOrionisRuntimeError

class InspireCommand(BaseCommand):

    # Disable timestamps in console output by default
    timestamps = False

    # Command name, by convention in lowercase and starting with app.
    signature: str = "schedule:shutdown"

    # Description of the command.
    description: str = "Stops the scheduler and halts all scheduled tasks."

    async def handle(self, schedule: ISchedule) -> None:
        """
        Gracefully shuts down the scheduler if it is currently running.

        This method checks whether the provided scheduler instance is running.
        If the scheduler is active, it attempts to shut it down asynchronously.
        If an error occurs during the shutdown process, a custom runtime error
        is raised to provide more context.

        Parameters
        ----------
        schedule : ISchedule
            The scheduler instance to be shut down.

        Returns
        -------
        None
            This method does not return any value. It performs the shutdown
            operation as a side effect.

        Raises
        ------
        CLIOrionisRuntimeError
            If an error occurs while attempting to shut down the scheduler.
        """

        try:

            # Check if the scheduler is currently running
            if schedule.isRunning():

                # Attempt to shut down the scheduler asynchronously
                await schedule.shutdown()

        except Exception as e:

            # Raise a custom runtime error if shutdown fails
            raise CLIOrionisRuntimeError(f"Failed to shut down scheduled tasks: {str(e)}")