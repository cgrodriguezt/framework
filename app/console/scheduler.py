from datetime import datetime, timedelta
from app.console.listeners.inspire_listener import InspireListener
from orionis.console.base.scheduler import BaseScheduler
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.scheduler_error import SchedulerError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted

class Scheduler(BaseScheduler):

    async def tasks(self, schedule: ISchedule):
        """
        Defines and registers scheduled tasks for the application.

        This asynchronous method is responsible for configuring and registering the scheduled
        commands that the application will execute. It utilizes the provided `schedule` object
        to define commands, set their execution intervals, configure concurrency, and attach
        listeners for event handling. This setup enables automated and recurring task execution
        within the application's scheduling framework.

        Parameters
        ----------
        schedule : ISchedule
            The schedule object used to define and register scheduled commands.

        Returns
        -------
        None
            This method does not return any value. It registers tasks to be executed
            by the scheduler.

        Notes
        -----
        - Schedules the "app:test" command to run every fifteen seconds with a random delay,
          a maximum of three concurrent instances, and a specific parameter.
        - Schedules the "app:inspire" command to run every ten seconds with a random delay,
          a maximum of three concurrent instances, and attaches the `InspireListener` to handle
          related events.
        - Schedules the "schedule:pause" and "schedule:resume" commands to run daily at
          specified times to control the scheduler state.
        - Schedules the "schedule:shutdown" command to run once at a specific datetime to
          stop the scheduler.
        """

        # Register the "app:test" command to run every fifteen seconds.
        # - Adds a random delay of up to 5 seconds before execution.
        # - Limits to 3 concurrent instances.
        # - Passes the "--name=Raul" parameter to the command.
        schedule.command("app:test", ["--name=Raul"])\
                .purpose("Test Route Command")\
                .maxInstances(1)\
                .everyFifteenSeconds()

        # Register the "app:inspire" command to run every ten seconds.
        # - Adds a random delay of up to 5 seconds before execution.
        # - Limits to 3 concurrent instances.
        # - Attaches the InspireListener to handle command events.
        schedule.command("app:inspire")\
            .purpose("Test Inspire Command")\
            .maxInstances(1)\
            .subscribeListener(InspireListener)\
            .everySeconds(20)

        # Register the "schedule:pause" command to run daily at 22:00.
        # This command pauses all scheduled tasks at the specified time.
        schedule.command("schedule:pause")\
            .purpose("Pauses all scheduled tasks")\
            .onceAt(datetime.now() + timedelta(seconds=40))

        # Register the "schedule:resume" command to run daily at 08:00.
        # This command resumes all scheduled tasks at the specified time.
        schedule.command("schedule:resume")\
            .purpose("Resumes all scheduled tasks")\
            .onceAt(datetime.now() + timedelta(seconds=80))

        # Register the "schedule:shutdown" command to run once at a specific datetime.
        # This command stops the scheduler at the given date and time.
        schedule.command("schedule:shutdown")\
            .purpose("Stops the scheduler")\
            .onceAt(datetime.now() + timedelta(seconds=120))

    async def onStarted(self, event: SchedulerStarted, schedule: ISchedule):
        """
        Handles the event triggered when the scheduler has started successfully.

        This asynchronous method is called when the scheduler begins its operation.
        It processes the `SchedulerStarted` event, allowing for any necessary initialization,
        logging, or custom actions to be performed at the start of the scheduler.

        Parameters
        ----------
        event : SchedulerStarted
            The event object containing details about the scheduler start event, such as
            the timestamp and any relevant metadata.
        schedule : ISchedule
            The schedule instance associated with the started scheduler, which can be used
            to interact with or modify scheduled tasks.

        Returns
        -------
        None
            This method does not return any value. It is intended for handling the
            scheduler start event and performing related actions, such as initialization
            or logging.

        Notes
        -----
        This method calls the parent class's `onStarted` method to ensure that any base
        functionality is executed, maintaining the default behavior while enabling
        additional custom actions during the scheduler's startup process.
        """

        # Call the parent class's onStarted method to retain base functionality
        await super().onStarted(event, schedule)

    async def onPaused(self, event: SchedulerPaused, schedule: ISchedule):
        """
        Handles the event triggered when the scheduler is paused.

        This asynchronous method is called whenever the scheduler pauses its operation.
        It processes the `SchedulerPaused` event, allowing for custom actions such as
        logging, resource management, or notification when the scheduler enters a paused state.
        The method ensures that any base class logic is executed by invoking the parent
        implementation.

        Parameters
        ----------
        event : SchedulerPaused
            The event object containing details about the scheduler pause event, such as
            the timestamp and relevant metadata.
        schedule : ISchedule
            The schedule instance associated with the paused scheduler, which can be used
            to inspect or modify scheduled tasks during the pause.

        Returns
        -------
        None
            This method does not return any value. It is intended for handling the
            scheduler pause event and performing related actions, such as logging or
            resource management.

        Notes
        -----
        This method calls the parent class's `onPaused` method to ensure that any base
        functionality is executed, maintaining the default behavior while enabling
        additional custom actions during the scheduler's pause process.
        """

        # Call the parent class's onPaused method to retain base functionality
        await super().onPaused(event, schedule)

    async def onResumed(self, event: SchedulerResumed, schedule: ISchedule):
        """
        Handles the event triggered when the scheduler is resumed.

        This asynchronous method is called when the scheduler resumes its operation after being paused.
        It processes the `SchedulerResumed` event, allowing for custom actions such as logging,
        resource reallocation, or notification when the scheduler transitions from a paused to an active state.
        The method ensures that any base class logic is executed by invoking the parent implementation.

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
            This method does not return any value. It is intended for handling the
            scheduler resumption event and performing related actions, such as logging or
            resource management.

        Notes
        -----
        This method calls the parent class's `onResumed` method to ensure that any base
        functionality is executed, maintaining the default behavior while enabling
        additional custom actions during the scheduler's resumption process.
        """

        # Call the parent class's onResumed method to retain base functionality
        await super().onResumed(event, schedule)

    async def onFinalized(self, event: SchedulerShutdown, schedule: ISchedule):
        """
        Handles the event triggered when the scheduler has completed its shutdown process.

        This asynchronous method is called after the scheduler has been finalized and all scheduled
        tasks have been stopped. It processes the `SchedulerShutdown` event, allowing for any necessary
        cleanup operations, resource deallocation, or logging activities related to the scheduler's
        termination. By invoking this method, you can ensure that any custom actions required at the
        end of the scheduler's lifecycle are performed appropriately.

        Parameters
        ----------
        event : SchedulerShutdown
            The event object containing details about the scheduler shutdown, such as the timestamp
            and any relevant metadata associated with the shutdown process.
        schedule : ISchedule
            The schedule instance associated with the finalized scheduler, which can be used to
            inspect or interact with the scheduler's tasks during the shutdown phase.

        Returns
        -------
        None
            This method does not return any value. It is intended solely for handling the scheduler
            shutdown event and executing any related finalization logic.

        Notes
        -----
        This method calls the parent class's `onFinalized` method to ensure that any base
        functionality is executed, maintaining the default shutdown behavior while enabling
        additional custom actions during the scheduler's finalization process.
        """

        # Call the parent class's onFinalized method to retain base shutdown functionality
        await super().onFinalized(event, schedule)

    async def onError(self, event: SchedulerError, schedule: ISchedule):
        """
        Handles errors that occur during the execution of scheduled jobs.

        This asynchronous method is triggered whenever a scheduled job encounters an exception
        during its execution. It processes the `SchedulerError` event, which contains details
        about the error, such as the exception message, stack trace, and any relevant metadata.
        This method can be used to implement custom error handling logic, such as logging error
        details, sending notifications, or performing cleanup operations. The base class's
        `onError` method is called to ensure that any default error handling behavior is preserved.

        Parameters
        ----------
        event : SchedulerError
            The event object containing information about the job error, including the exception
            details and associated metadata.
        schedule : ISchedule
            The schedule instance associated with the job, which can be used to interact with or
            modify scheduled tasks.

        Returns
        -------
        None
            This method does not return any value. It is intended for handling job error events
            and executing related actions such as logging or notification.

        Notes
        -----
        - Calls the parent class's `onError` method to maintain default error handling behavior.
        - Can be extended to include custom error handling logic as needed.
        """

        # Call the parent class's onError method to retain base error handling functionality
        await super().onError(event, schedule)