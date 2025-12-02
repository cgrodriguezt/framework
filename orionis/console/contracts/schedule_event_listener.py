from abc import ABC, abstractmethod
from orionis.console.entities.event_job import EventJob

class IScheduleEventListener(ABC):

    # ruff: noqa: ANN001
    @abstractmethod
    async def before(self, event: EventJob, schedule) -> None:
        """
        Invoke before processing a job submission event.

        Parameters
        ----------
        event : EventJob
            Job submission event with job details.
        schedule : ISchedule
            Schedule instance managing the job.

        Returns
        -------
        None
            This method does not return a value.
        """

    # ruff: noqa: ANN001
    @abstractmethod
    async def after(self, event: EventJob, schedule) -> None:
        """
        Invoke after processing a job execution event.

        Parameters
        ----------
        event : EventJob
            Job execution event with job details.
        schedule : ISchedule
            Schedule instance managing the job.

        Returns
        -------
        None
            This method does not return a value.
        """

    # ruff: noqa: ANN001
    @abstractmethod
    async def onFailure(self, event: EventJob, schedule) -> None:
        """
        Handle job execution failure.

        Parameters
        ----------
        event : EventJob
            Job error event with failure details.
        schedule : ISchedule
            Schedule instance managing the job.

        Returns
        -------
        None
            This method does not return a value.
        """

    # ruff: noqa: ANN001
    @abstractmethod
    async def onMissed(self, event: EventJob, schedule) -> None:
        """
        Handle missed job execution.

        Parameters
        ----------
        event : EventJob
            Missed job event with missed execution details.
        schedule : ISchedule
            Schedule instance managing the job.

        Returns
        -------
        None
            This method does not return a value.
        """

    # ruff: noqa: ANN001
    @abstractmethod
    async def onMaxInstances(self, event: EventJob, schedule) -> None:
        """
        Handle job exceeding maximum allowed instances.

        Parameters
        ----------
        event : EventJob
            Max instances event with job details.
        schedule : ISchedule
            Schedule instance managing the job.

        Returns
        -------
        None
            This method does not return a value.
        """

    # ruff: noqa: ANN001
    @abstractmethod
    async def onPaused(self, event: EventJob, schedule) -> None:
        """
        Handle scheduler pause event.

        Parameters
        ----------
        event : EventJob
            Pause event with scheduler state details.
        schedule : ISchedule
            Schedule instance managing the jobs.

        Returns
        -------
        None
            This method does not return a value.
        """

    # ruff: noqa: ANN001
    @abstractmethod
    async def onResumed(self, event: EventJob, schedule) -> None:
        """
        Handle scheduler resume event.

        Parameters
        ----------
        event : EventJob
            Resume event with scheduler state details.
        schedule : ISchedule
            Schedule instance managing the jobs.

        Returns
        -------
        None
            This method does not return a value.
        """

    # ruff: noqa: ANN001
    @abstractmethod
    async def onRemoved(self, event: EventJob, schedule) -> None:
        """
        Handle job removal from scheduler.

        Parameters
        ----------
        event : EventJob
            Job removal event with removed job details.
        schedule : ISchedule
            Schedule instance managing the jobs.

        Returns
        -------
        None
            This method does not return a value.
        """
