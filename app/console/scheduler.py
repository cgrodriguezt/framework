from datetime import datetime
from app.console.listeners.inspire_listener import InspireListener
from orionis.console.base.scheduler import BaseScheduler
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.job_error import JobError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted

class Scheduler(BaseScheduler):

    # Pause Global Scheduler at a specific time
    PAUSE_AT = datetime(2025, 8, 19, 22, 33, 0)

    # Resume Global Scheduler at a specific time
    RESUME_AT = datetime(2025, 8, 19, 22, 33, 0)

    # Finalize Global Scheduler at a specific time
    FINALIZE_AT = datetime(2025, 8, 20, 7, 32, 0)

    async def tasks(self, schedule: ISchedule):
        """
        Defines and registers scheduled tasks for the application.

        Parameters
        ----------
        schedule : ISchedule
            The schedule object used to define and register scheduled commands.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        This method schedules the "app:inspire" command with the following properties:
            - Purpose: "Inspire Command Test"
            - Executes once at 2025-08-19 13:59:00
            - Applies a random delay of up to 5 seconds before execution
        """

        # Schedule the "app:inspire" command with a specific purpose,
        # a random delay of up to 5 seconds, to run once at the specified datetime.
        schedule.command("app:inspire")\
                .purpose("Inspire Command Test")\
                .randomDelay(5)\
                .maxInstances(3)\
                .subscribeListener(InspireListener)\
                .everySeconds(10)

    async def onStarted(self, event:SchedulerStarted, schedule:ISchedule):
        print("Hello, the scheduler has started successfully.")

    async def onPaused(self, event:SchedulerPaused, schedule:ISchedule):
        print("Hello, the scheduler has been paused successfully.")

    async def onResumed(self, event:SchedulerResumed, schedule:ISchedule):
        print("Hello, the scheduler has been resumed successfully.")

    async def onFinalized(self, event:SchedulerShutdown, schedule:ISchedule):
        print("Hello, the scheduler has been finalized successfully.")

    async def onError(self, event:JobError, schedule:ISchedule):
        print(f"Hello, the job {event.job_id} has encountered an error: {event.exception}")