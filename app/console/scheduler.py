from __future__ import annotations
from typing import TYPE_CHECKING
from app.console.listeners.inspire_listener import InspireListener
from orionis.console.base.scheduler import BaseScheduler

if TYPE_CHECKING:
    from orionis.console.contracts.schedule import ISchedule
    from orionis.console.entities.scheduler_error import SchedulerError
    from orionis.console.entities.scheduler_paused import SchedulerPaused
    from orionis.console.entities.scheduler_resumed import SchedulerResumed
    from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
    from orionis.console.entities.scheduler_started import SchedulerStarted

class Scheduler(BaseScheduler):

    async def tasks(self, schedule: ISchedule) -> None:
        """
        Register scheduled tasks for the application.

        Set up tasks that the scheduler will execute using the provided schedule
        object.

        Parameters
        ----------
        schedule : ISchedule
            The schedule object used to register scheduled commands.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Register a test command that runs every fifteen seconds
        schedule.command("app:test", ["--name=Raul"])\
            .purpose("Test Route Command")\
            .maxInstances(1)\
            .everyFifteenSeconds()

        # Register the inspire command to run every 20 seconds
        schedule.command("app:inspire")\
            .purpose("Test Inspire Command")\
            .maxInstances(1)\
            .subscribeListener(InspireListener)\
            .everySeconds(20)

    async def onStarted(self, event: SchedulerStarted, schedule: ISchedule) -> None:
        """
        Handle the scheduler start event.

        This method is called when the scheduler starts its operation. It processes
        the `SchedulerStarted` event and can be used for initialization or logging.

        Parameters
        ----------
        event : SchedulerStarted
            Details about the scheduler start event.
        schedule : ISchedule
            The schedule instance associated with the started scheduler.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Calls the parent class's `onStarted` method for base start handling.
        """
        # Call the parent class's onStarted method.
        await super().onStarted(event, schedule)

    async def onPaused(self, event: SchedulerPaused, schedule: ISchedule) -> None:
        """
        Handle the scheduler pause event.

        This method is called when the scheduler is paused. It processes the
        `SchedulerPaused` event and can be used for logging or custom actions.

        Parameters
        ----------
        event : SchedulerPaused
            Details about the scheduler pause event.
        schedule : ISchedule
            The schedule instance associated with the paused scheduler.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Calls the parent class's `onPaused` method for base pause handling.
        """
        # Call the parent class's onPaused method.
        await super().onPaused(event, schedule)

    async def onResumed(self, event: SchedulerResumed, schedule: ISchedule) -> None:
        """
        Handle the scheduler resumption event.

        Called when the scheduler resumes after being paused. Processes the
        `SchedulerResumed` event for logging or custom actions.

        Parameters
        ----------
        event : SchedulerResumed
            Details about the scheduler resumption.
        schedule : ISchedule
            The schedule instance associated with the resumed scheduler.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Calls the parent class's `onResumed` method for base resumption handling.
        """
        # Call the parent class's onResumed method.
        await super().onResumed(event, schedule)

    async def onFinalized(self, event: SchedulerShutdown, schedule: ISchedule) -> None:
        """
        Handle the scheduler finalization event.

        This method is called after the scheduler has completed its shutdown.
        It processes the `SchedulerShutdown` event and performs cleanup or logging.

        Parameters
        ----------
        event : SchedulerShutdown
            Details about the scheduler shutdown.
        schedule : ISchedule
            The schedule instance associated with the finalized scheduler.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Calls the parent class's `onFinalized` method for base finalization.
        """
        # Call the parent class's onFinalized method.
        await super().onFinalized(event, schedule)

    async def onError(self, event: SchedulerError, schedule: ISchedule) -> None:
        """
        Handle errors that occur during job execution.

        This method is called when a job fails due to an exception. It processes the
        `SchedulerError` event and can be used for logging or notification.

        Parameters
        ----------
        event : SchedulerError
            Contains details about the job error, such as job ID and exception info.
        schedule : ISchedule
            The schedule instance related to the job.

        Returns
        -------
        None
            No value is returned.

        Notes
        -----
        Calls the parent class's `onError` method for base error handling.
        """
        # Call the parent class's onError method.
        await super().onError(event, schedule)
