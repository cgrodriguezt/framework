from orionis.console.base.command import BaseCommand
from orionis.console.contracts.schedule import ISchedule
from orionis.console.exceptions import CLIOrionisRuntimeError

class InspireCommand(BaseCommand):

    # Disable timestamps in console output by default
    timestamps = False

    # Command name, by convention in lowercase and starting with app.
    signature: str = "schedule:pause"

    # Description of the command.
    description: str = "Command responsible for pausing scheduled tasks."

    async def handle(self, schedule: ISchedule) -> None:
        """
        Pauses all scheduled tasks if they are currently active.

        This method checks whether the provided schedule is currently active (not paused).
        If the schedule is active, it attempts to pause all scheduled tasks. If an error
        occurs during the pausing process, a CLIOrionisRuntimeError is raised with a
        descriptive message.

        Parameters
        ----------
        schedule : ISchedule
            The schedule instance whose tasks are to be paused.

        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        CLIOrionisRuntimeError
            If an error occurs while attempting to pause the scheduled tasks.
        """

        try:

            # Check if the schedule is not already paused
            if not schedule.isPaused():

                # Pause the schedule if it is currently active
                schedule.pause()

        except Exception as e:

            # Raise a custom runtime error if pausing fails
            raise CLIOrionisRuntimeError(
                f"An error occurred while attempting to pause scheduled tasks: {str(e)}"
            )
