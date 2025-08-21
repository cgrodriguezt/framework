from datetime import datetime
from orionis.console.contracts.schedule import ISchedule

class BaseScheduler:

    # Pause Global Scheduler at a specific time
    PAUSE_AT: datetime = None

    # Resume Global Scheduler at a specific time
    RESUME_AT: datetime = None

    # Finalize Global Scheduler at a specific time
    FINALIZE_AT: datetime = None

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
        This method should be implemented in subclasses to add specific tasks
        to the scheduler using the provided `schedule` object.
        """
        # This method should be overridden in subclasses to define scheduled tasks.
        pass

    def onStarted(self):
        # Called when the scheduler is started.
        pass

    def onPaused(self):
        # Called when the scheduler is paused.
        pass

    def onResumed(self):
        # Called when the scheduler is resumed.
        pass

    def onFinalized(self):
        # Called when the scheduler is finalized.
        pass

    def onError(self, error: Exception):
        # Called when an error occurs in the scheduler.
        pass