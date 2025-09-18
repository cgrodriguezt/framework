from orionis.console.base.command import BaseCommand
from orionis.console.contracts.schedule import ISchedule
from orionis.console.exceptions import CLIOrionisRuntimeError

class InspireCommand(BaseCommand):

    # Disable timestamps in console output by default
    timestamps = False

    # Command name, by convention in lowercase and starting with app.
    signature: str = "schedule:resume"

    # Description of the command.
    description: str = "Command responsible for resuming scheduled tasks."

    async def handle(self, schedule: ISchedule) -> None:
        """
        Resumes all scheduled tasks if they are currently paused.

        This method checks whether the provided schedule instance is in a paused state.
        If the schedule is paused, it attempts to resume all scheduled tasks associated
        with the schedule. If an error occurs during the resumption process, a
        CLIOrionisRuntimeError is raised with a descriptive error message.

        Parameters
        ----------
        schedule : ISchedule
            The schedule instance whose tasks are to be resumed.

        Returns
        -------
        None
            This method does not return any value. Its sole purpose is to resume
            scheduled tasks if they are paused.

        Raises
        ------
        CLIOrionisRuntimeError
            If an error occurs while attempting to resume the scheduled tasks.
        """

        try:

            # Check if the schedule is currently paused
            if schedule.isPaused():

                # Resume the schedule if it is paused
                schedule.resume()

        except Exception as e:

            # Raise a custom runtime error if resuming fails
            raise CLIOrionisRuntimeError(f"Failed to resume scheduled tasks. Details: {e}")
