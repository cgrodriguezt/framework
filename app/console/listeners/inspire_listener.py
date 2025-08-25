from orionis.console.base.scheduler_event_listener import BaseScheduleEventListener
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.job_error import JobError
from orionis.console.entities.job_executed import JobExecuted
from orionis.console.entities.job_max_instances import JobMaxInstances
from orionis.console.entities.job_missed import JobMissed
from orionis.console.entities.job_pause import JobPause
from orionis.console.entities.job_removed import JobRemoved
from orionis.console.entities.job_resume import JobResume
from orionis.console.entities.job_submitted import JobSubmitted

class InspireListener(BaseScheduleEventListener):

    async def before(self, event: JobSubmitted, schedule: ISchedule):
        """
        Called before processing a job submission event.

        Parameters
        ----------
        event : JobSubmitted
            The job submission event.
        schedule : ISchedule
            The associated schedule.
        """
        print("InspireListener: Before job submission.")
        pass

    async def after(self, event: JobExecuted, schedule: ISchedule):
        """
        Called after processing a job execution event.

        Parameters
        ----------
        event : JobExecuted
            The job execution event.
        schedule : ISchedule
            The associated schedule.
        """
        print("InspireListener: After job execution.")
        pass

    async def onSuccess(self, event: JobExecuted, schedule: ISchedule):
        """
        Called when a job is successfully executed.

        Parameters
        ----------
        event : JobExecuted
            The successful job execution event.
        schedule : ISchedule
            The associated schedule.
        """
        print("InspireListener: Job executed successfully.")
        pass

    async def onFailure(self, event: JobError, schedule: ISchedule):
        """
        Called when a job execution fails.

        Parameters
        ----------
        event : JobError
            The job error event.
        schedule : ISchedule
            The associated schedule.
        """
        print("InspireListener: Job execution failed.")
        pass

    async def onMissed(self, event: JobMissed, schedule: ISchedule):
        """
        Called when a job execution is missed.

        Parameters
        ----------
        event : JobMissed
            The missed job event.
        schedule : ISchedule
            The associated schedule.
        """
        print("InspireListener: Job execution missed.")
        pass

    async def onMaxInstances(self, event: JobMaxInstances, schedule: ISchedule):
        """
        Called when a job exceeds the maximum allowed instances.

        Parameters
        ----------
        event : JobMaxInstances
            The max instances event.
        schedule : ISchedule
            The associated schedule.
        """
        print("InspireListener: Job exceeded maximum instances.")
        pass

    async def onPaused(self, event: JobPause, schedule: ISchedule):
        """
        Called when the scheduler is paused.

        Parameters
        ----------
        event : JobPause
            The pause event.
        schedule : ISchedule
            The associated schedule.
        """
        print("InspireListener: Scheduler paused.")
        pass

    async def onResumed(self, event: JobResume, schedule: ISchedule):
        """
        Called when the scheduler is resumed.

        Parameters
        ----------
        event : JobResume
            The resume event.
        schedule : ISchedule
            The associated schedule.
        """
        print("InspireListener: Scheduler resumed.")
        pass

    async def onRemoved(self, event: JobRemoved, schedule: ISchedule):
        """
        Called when a job is removed from the scheduler.

        Parameters
        ----------
        event : JobRemoved
            The job removal event.
        schedule : ISchedule
            The associated schedule.
        """
        print("InspireListener: Job removed from scheduler.")
        pass
