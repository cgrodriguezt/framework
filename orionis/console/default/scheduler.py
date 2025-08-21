from orionis.console.base.scheduler import BaseScheduler
from orionis.console.contracts.schedule import ISchedule

class Scheduler(BaseScheduler):

    def tasks(self, schedule: ISchedule):
        """
        Defines and registers scheduled tasks for the application.

        Parameters
        ----------
        schedule : ISchedule
            The schedule object used to define and register scheduled commands.

        Returns
        -------
        None
            This method does not return any value. It is intended to be overridden
            by subclasses to specify scheduled tasks.

        Notes
        -----
        Subclasses should implement this method to add specific tasks to the scheduler
        using the provided `schedule` object. This method enforces that each subclass
        defines its own scheduled tasks.
        """
        pass