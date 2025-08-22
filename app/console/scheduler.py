from datetime import datetime
from orionis.console.base.scheduler import BaseScheduler
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.listeners import *

class Scheduler(BaseScheduler):

    # Pause Global Scheduler at a specific time
    PAUSE_AT = datetime(2025, 8, 19, 22, 33, 0)

    # Resume Global Scheduler at a specific time
    RESUME_AT = datetime(2025, 8, 19, 22, 33, 0)

    # Finalize Global Scheduler at a specific time
    FINALIZE_AT = datetime(2025, 8, 20, 7, 32, 0)

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
                .everySeconds(10)
                # .maxInstances(3)\
                # .subscribeListener(CommandListener)\
                # .pauseAt(datetime(2025, 8, 19, 22, 33, 0))\
                # .resumeAt(datetime(2025, 8, 19, 22, 33, 0))\

    # def onStarted(self, commands:list):
    #     print("Scheduler started successfully.")

    # def onPaused(self, commands:list):
    #     print("Scheduler paused successfully.")

    # def onResumed(self, commands:list):
    #     print("Scheduler resumed successfully.")

    # def onFinalized(self, commands:list):
    #     print("Scheduler finalized successfully.")

    # def onError(self, error:Exception):
    #     print(f"Scheduler encountered an error: {error}")