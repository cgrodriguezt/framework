from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.console.contracts.base_scheduler import IBaseScheduler

if TYPE_CHECKING:
    from orionis.console.contracts.schedule import ISchedule
    from orionis.console.entities.scheduler_error import SchedulerError
    from orionis.console.entities.scheduler_paused import SchedulerPaused
    from orionis.console.entities.scheduler_resumed import SchedulerResumed
    from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
    from orionis.console.entities.scheduler_started import SchedulerStarted

class BaseScheduler(IBaseScheduler):

    async def tasks(self, schedule: ISchedule) -> None:
        """
        Register scheduled tasks for the application.

        This method sets up tasks that the scheduler will execute using the provided
        `schedule` object. Subclasses should override this method to define specific
        tasks and their scheduling properties.

        Parameters
        ----------
        schedule : ISchedule
            The schedule object used to register scheduled commands.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Subclasses must implement this method to specify their task scheduling logic.
        """
        error_msg = (
            "Subclasses must implement the 'tasks' method to register scheduled tasks."
        )
        raise NotImplementedError(error_msg)

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
