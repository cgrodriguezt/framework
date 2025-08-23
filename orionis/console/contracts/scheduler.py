from abc import ABC, abstractmethod
from datetime import datetime
from orionis.console.contracts.schedule import ISchedule

class IBaseScheduler(ABC):

    # Pause Global Scheduler at a specific time
    PAUSE_AT: datetime = None

    # Resume Global Scheduler at a specific time
    RESUME_AT: datetime = None

    # Finalize Global Scheduler at a specific time
    FINALIZE_AT: datetime = None

    @abstractmethod
    def tasks(self, schedule: ISchedule):
        """
        Defines and registers scheduled tasks for the application.

        Parameters
        ----------
        schedule : ISchedule
            The schedule object used to define and register scheduled commands. 
            This object provides methods to add tasks to the scheduler.

        Returns
        -------
        None
            This method does not return any value. It is intended to be overridden
            by subclasses to specify scheduled tasks.

        Notes
        -----
        This method serves as a contract for subclasses to implement task registration
        logic. Subclasses should use the provided `schedule` object to define and
        register tasks that the scheduler will execute.
        """
        # Abstract method to be implemented by subclasses for task registration
        pass

    @abstractmethod
    def onStarted(self):
        """
        Called when the scheduler is started.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Subclasses should override this method to implement custom behavior that
        should occur when the scheduler starts running. This can include initializing
        resources or logging the start event.
        """
        # Abstract method to define behavior when the scheduler starts
        pass

    @abstractmethod
    def onPaused(self):
        """
        Called when the scheduler is paused.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Subclasses should override this method to define custom behavior that occurs
        when the scheduler enters a paused state. This can include saving the current
        state or logging the pause event.
        """
        # Abstract method to define behavior when the scheduler is paused
        pass

    @abstractmethod
    def onResumed(self):
        """
        Called when the scheduler is resumed from a paused state.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Subclasses should override this method to implement any actions that need to
        occur when the scheduler resumes operation. This can include restoring the
        state or logging the resume event.
        """
        # Abstract method to define behavior when the scheduler is resumed
        pass

    @abstractmethod
    def onFinalized(self):
        """
        Called when the scheduler has completed its execution and is being finalized.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Subclasses can override this method to perform any necessary cleanup or
        finalization tasks, such as releasing resources or logging the finalization
        event.
        """
        # Abstract method to define behavior when the scheduler is finalized
        pass

    @abstractmethod
    def onError(self, error: Exception):
        """
        Handles errors that occur within the scheduler.

        Parameters
        ----------
        error : Exception
            The exception instance representing the error that occurred.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Subclasses can override this method to implement custom error handling logic
        for the scheduler. This can include logging the error, notifying stakeholders,
        or attempting to recover from the error.
        """
        # Abstract method to define behavior for handling errors in the scheduler
        pass