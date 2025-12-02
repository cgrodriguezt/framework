from orionis.console.contracts.schedule_event_listener import IScheduleEventListener
from orionis.console.entities.event_job import EventJob

class BaseScheduleEventListener(IScheduleEventListener):

    # ruff: noqa: ANN001
    async def before(self, event: EventJob, schedule) -> None:
        """
        Handle job submission event before processing.

        Parameters
        ----------
        event : EventJob
            The job submission event containing details about the job.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
        """

    # ruff: noqa: ANN001
    async def after(self, event: EventJob, schedule) -> None:
        """
        Handle job execution completion event.

        Parameters
        ----------
        event : EventJob
            The job execution event containing details about the job.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
        """

    # ruff: noqa: ANN001
    async def onFailure(self, event: EventJob, schedule) -> None:
        """
        Handle job execution failure.

        Parameters
        ----------
        event : EventJob
            The job error event containing details about the failure.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
        """

    # ruff: noqa: ANN001
    async def onMissed(self, event: EventJob, schedule) -> None:
        """
        Handle missed job execution event.

        Parameters
        ----------
        event : EventJob
            The missed job event containing details about the missed execution.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
        """

    # ruff: noqa: ANN001
    async def onMaxInstances(self, event: EventJob, schedule) -> None:
        """
        Handle event when a job exceeds the maximum allowed instances.

        Parameters
        ----------
        event : EventJob
            The max instances event containing details about the job.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
        """

    # ruff: noqa: ANN001
    async def onPaused(self, event: EventJob, schedule) -> None:
        """
        Handle scheduler pause event.

        Parameters
        ----------
        event : EventJob
            The pause event containing details about the scheduler state.
        schedule : ISchedule
            The associated schedule instance managing the jobs.

        Returns
        -------
        None
        """

    # ruff: noqa: ANN001
    async def onResumed(self, event: EventJob, schedule) -> None:
        """
        Handle scheduler resume event.

        Parameters
        ----------
        event : EventJob
            The resume event containing details about the scheduler state.
        schedule : ISchedule
            The associated schedule instance managing the jobs.

        Returns
        -------
        None
        """

    # ruff: noqa: ANN001
    async def onRemoved(self, event: EventJob, schedule) -> None:
        """
        Handle job removal from the scheduler.

        Parameters
        ----------
        event : EventJob
            The job removal event containing details about the removed job.
        schedule : ISchedule
            The associated schedule instance managing the jobs.

        Returns
        -------
        None
        """
