from abc import ABC, abstractmethod
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.scheduler_error import SchedulerError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted

class IBaseScheduler(ABC):

    @abstractmethod
    async def tasks(self, schedule: ISchedule) -> None:
        """
        Define and register scheduled tasks for the application.

        Parameters
        ----------
        schedule : ISchedule
            Schedule object for registering tasks.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    async def onStarted(self, event: SchedulerStarted, schedule: ISchedule) -> None:
        """
        Handle the event when the scheduler starts.

        Parameters
        ----------
        event : SchedulerStarted
            Event with scheduler start details.
        schedule : ISchedule
            Schedule instance for the started scheduler.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    async def onPaused(self, event: SchedulerPaused, schedule: ISchedule) -> None:
        """
        Handle the event when the scheduler is paused.

        Parameters
        ----------
        event : SchedulerPaused
            Event with scheduler pause details.
        schedule : ISchedule
            Schedule instance for the paused scheduler.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    async def onResumed(self, event: SchedulerResumed, schedule: ISchedule) -> None:
        """
        Handle the event when the scheduler is resumed.

        Parameters
        ----------
        event : SchedulerResumed
            Event with scheduler resumption details.
        schedule : ISchedule
            Schedule instance for the resumed scheduler.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    async def onFinalized(self, event: SchedulerShutdown, schedule: ISchedule) -> None:
        """
        Handle the event when the scheduler is finalized.

        Parameters
        ----------
        event : SchedulerShutdown
            Event with scheduler shutdown details.
        schedule : ISchedule
            Schedule instance for the finalized scheduler.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    async def onError(self, event: SchedulerError, schedule: ISchedule) -> None:
        """
        Handle the event when a job encounters an error.

        Parameters
        ----------
        event : SchedulerError
            Event with job error details.
        schedule : ISchedule
            Schedule instance for the job.

        Returns
        -------
        None
            This method does not return any value.
        """
