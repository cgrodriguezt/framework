from orionis.console.base.scheduler_event_listener import BaseScheduleEventListener
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.event_job import EventJob

class InspireListener(BaseScheduleEventListener):

    async def before(self, event: EventJob, schedule: ISchedule):
        """
        Called before processing a job submission event.

        Parameters
        ----------
        event : EventJob
            The job submission event containing details about the job.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
            This method does not return any value.
        """
        # await super().before(event, schedule)
        print("InspireListener before job...")

    async def after(self, event: EventJob, schedule: ISchedule):
        """
        Called after processing a job execution event.

        Parameters
        ----------
        event : EventJob
            The job execution event containing details about the executed job.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
            This method does not return any value.
        """
        # await super().after(event, schedule)
        print("InspireListener after job...")

    async def onFailure(self, event: EventJob, schedule: ISchedule):
        """
        Called when a job execution fails.

        Parameters
        ----------
        event : EventJob
            The event containing details about the job execution failure.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
            This method does not return any value.
        """
        # await super().onFailure(event, schedule)
        print("InspireListener job failure...")

    async def onMissed(self, event: EventJob, schedule: ISchedule):
        """
        Called when a job execution is missed.

        Parameters
        ----------
        event : EventJob
            The event containing details about the missed job execution.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
            This method does not return any value.
        """
        # await super().onMissed(event, schedule)
        print("InspireListener job missed...")

    async def onMaxInstances(self, event: EventJob, schedule: ISchedule):
        """
        Called when a job exceeds the maximum allowed instances.

        Parameters
        ----------
        event : EventJob
            The event containing details about the max instances violation.
        schedule : ISchedule
            The associated schedule instance managing the job.

        Returns
        -------
        None
            This method does not return any value.
        """
        await super().onMaxInstances(event, schedule)

    async def onPaused(self, event: EventJob, schedule: ISchedule):
        """
        Called when the scheduler is paused.

        Parameters
        ----------
        event : EventJob
            The event containing details about the scheduler pause.
        schedule : ISchedule
            The associated schedule instance managing the jobs.

        Returns
        -------
        None
            This method does not return any value.
        """
        await super().onPaused(event, schedule)

    async def onResumed(self, event: EventJob, schedule: ISchedule):
        """
        Called when the scheduler is resumed.

        Parameters
        ----------
        event : EventJob
            The event containing details about the scheduler resume.
        schedule : ISchedule
            The associated schedule instance managing the jobs.

        Returns
        -------
        None
            This method does not return any value.
        """
        await super().onResumed(event, schedule)

    async def onRemoved(self, event: EventJob, schedule: ISchedule):
        """
        Called when a job is removed from the scheduler.

        Parameters
        ----------
        event : EventJob
            The event containing details about the job removal.
        schedule : ISchedule
            The associated schedule instance managing the jobs.

        Returns
        -------
        None
            This method does not return any value.
        """
        await super().onRemoved(event, schedule)
