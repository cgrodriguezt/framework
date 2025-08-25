from datetime import datetime
from app.console.listeners.inspire_listener import InspireListener
from orionis.console.base.scheduler import BaseScheduler
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.scheduler_error import SchedulerError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted

class Scheduler(BaseScheduler):

    # Pause Global Scheduler dynamically one minute from now
    PAUSE_AT = datetime(2025, 8, 25, 14, 23, 0)

    # Resume Global Scheduler dynamically one minute after pause
    RESUME_AT = datetime(2025, 8, 25, 14, 24, 0)

    # Finalize Global Scheduler dynamically one minute after resume
    FINALIZE_AT = datetime(2025, 8, 25, 14, 25, 0)

    async def tasks(self, schedule: ISchedule):
        """
        Example of defining and registering scheduled tasks for the application.

        Parameters
        ----------
        schedule : ISchedule
            The schedule object used to define and register scheduled commands.

        Returns
        -------
        None
            This method does not return any value. It registers tasks to be executed by the scheduler.

        Notes
        -----
        This method schedules the "app:inspire" command with the following properties:
            - Purpose: "Inspire Command Test"
            - Executes every ten seconds
            - Applies a random delay of up to 5 seconds before execution
            - Allows a maximum of 3 concurrent instances of the command
            - Subscribes the `InspireListener` to handle events related to this command
        """

        # Schedule the "app:inspire" command to run every ten seconds
        schedule.command("app:inspire")\
                .purpose("Inspire Command Test")\
                .randomDelay(5)\
                .maxInstances(3)\
                .subscribeListener(InspireListener)\
                .everyTenSeconds()

    async def onStarted(self, event: SchedulerStarted, schedule: ISchedule):
        """
        Handles the event triggered when the scheduler has started successfully.

        This method is invoked when the scheduler begins its operation. It processes
        the `SchedulerStarted` event and performs any necessary initialization or logging
        tasks associated with the start of the scheduler.

        Parameters
        ----------
        event : SchedulerStarted
            The event object containing details about the scheduler start event.
        schedule : ISchedule
            The schedule instance associated with the started scheduler.

        Returns
        -------
        None
            This method does not return any value. It is used for handling the
            scheduler start event and performing related actions.

        Notes
        -----
        This method calls the parent class's `onStarted` method to ensure that
        any base functionality is executed.
        """
        await super().onStarted(event, schedule)

    async def onPaused(self, event: SchedulerPaused, schedule: ISchedule):
        """
        Handles the event triggered when the scheduler is paused.

        This method is invoked when the scheduler pauses its operation. It processes
        the `SchedulerPaused` event and performs any necessary actions or logging
        tasks associated with the pause of the scheduler.

        Parameters
        ----------
        event : SchedulerPaused
            The event object containing details about the scheduler pause event.
        schedule : ISchedule
            The schedule instance associated with the paused scheduler.

        Returns
        -------
        None
            This method does not return any value. It is used for handling the
            scheduler pause event and performing related actions.

        Notes
        -----
        This method calls the parent class's `onPaused` method to ensure that
        any base functionality is executed.
        """

        # Call the parent class's onPaused method to retain base functionality
        await super().onPaused(event, schedule)

    async def onResumed(self, event: SchedulerResumed, schedule: ISchedule):
        """
        Handles the event triggered when the scheduler is resumed.

        This method is invoked when the scheduler resumes its operation after being paused.
        It processes the `SchedulerResumed` event and performs any necessary actions or logging
        tasks associated with the resumption of the scheduler.

        Parameters
        ----------
        event : SchedulerResumed
            The event object containing details about the scheduler resumption, such as the
            timestamp of the resumption and any relevant metadata.
        schedule : ISchedule
            The schedule instance associated with the resumed scheduler, which can be used
            to interact with or modify the scheduler's tasks.

        Returns
        -------
        None
            This method does not return any value. It is used for handling the scheduler
            resumption event and performing related actions.

        Notes
        -----
        This method calls the parent class's `onResumed` method to ensure that any base
        functionality is executed. This allows the scheduler to maintain its default behavior
        while enabling additional custom actions during the resumption process.
        """

        # Call the parent class's onResumed method to retain base functionality
        await super().onResumed(event, schedule)

    async def onFinalized(self, event: SchedulerShutdown, schedule: ISchedule):
        """
        Handles the event triggered when the scheduler has been finalized.

        This method is invoked after the scheduler has completed its shutdown process.
        It processes the `SchedulerShutdown` event and performs any necessary cleanup
        or logging tasks associated with the finalization of the scheduler.

        Parameters
        ----------
        event : SchedulerShutdown
            The event object containing details about the scheduler shutdown, such as
            the timestamp of the shutdown and any relevant metadata.
        schedule : ISchedule
            The schedule instance associated with the finalized scheduler, which can be
            used to interact with or inspect the scheduler's tasks.

        Returns
        -------
        None
            This method does not return any value. It is used for handling the scheduler
            shutdown event and performing related actions.

        Notes
        -----
        This method calls the parent class's `onFinalized` method to ensure that any base
        functionality is executed. This allows the scheduler to maintain its default behavior
        while enabling additional custom actions during the finalization process.
        """

        # Call the parent class's onFinalized method to retain base functionality
        await super().onFinalized(event, schedule)

    async def onError(self, event: SchedulerError, schedule: ISchedule):
        """
        Handles the event triggered when a job encounters an error during execution.

        This method is invoked when a job fails due to an exception. It processes the `JobError`
        event and performs any necessary actions, such as logging the error details or notifying
        relevant systems about the failure.

        Parameters
        ----------
        event : SchedulerError
            The event object containing details about the job error, such as the exception
            message, stack trace, and any relevant metadata.
        schedule : ISchedule
            The schedule instance associated with the job, which can be used to interact with
            or modify the scheduler's tasks.

        Returns
        -------
        None
            This method does not return any value. It is used for handling the job error event
            and performing related actions, such as logging or cleanup.

        Notes
        -----
        This method calls the parent class's `onError` method to ensure that any base functionality
        is executed. This allows the scheduler to maintain its default behavior while enabling
        additional custom actions during error handling.
        """

        # Call the parent class's onError method to retain base functionality
        await super().onError(event, schedule)