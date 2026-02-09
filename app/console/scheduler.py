from orionis.console.base.scheduler import BaseScheduler
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.scheduler_event import SchedulerEvent
from app.console.listeners.inspire_task_listener import InspireTaskListener

class Scheduler(BaseScheduler):

    # --------------------------------------------------------------------------
    # The 'tasks' method is required and is used to register scheduled tasks
    # that the scheduler will execute. You can define your tasks using the
    # 'schedule' object passed as an argument. This method is where you set up
    # the tasks you want to run in your application.
    #
    # The 'onStarted', 'onPaused', 'onResumed', and 'onShutdown' methods are
    # optional and can be implemented to handle specific scheduler lifecycle
    # events. These methods can be synchronous or asynchronous depending on
    # your logic. If you do not have await operations, you can define them as
    # synchronous. The Orionis event dispatcher will handle both cases.
    # --------------------------------------------------------------------------

    def __init__(
        self,
        inspire_listener: InspireTaskListener,
    ) -> None:
        """
        Initialize the Scheduler with required dependencies.

        Parameters
        ----------
        inspire_listener : InspireTaskListener
            Listener instance for handling inspire tasks.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        # Store the inspire task listener for later use in scheduled tasks
        self.inspire_listener = inspire_listener

    def tasks(
        self,
        schedule: ISchedule,
    ) -> None:
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
        # Register a test command that runs every ten seconds
        schedule.command("app:test", ["--name=Raul"])\
            .purpose("Test Route Command")\
            .maxInstances(1)\
            .everyTenSeconds()

        # Register the inspire command to run every fifteen seconds with a listener
        schedule.command("app:inspire")\
            .purpose("Test Inspire Command")\
            .maxInstances(1)\
            .registerListener(self.inspire_listener)\
            .everySeconds(15)

    async def onStarted(self, event: SchedulerEvent) -> None:
        """
        Handle the scheduler start event.

        Parameters
        ----------
        event : SchedulerEvent
            The event object representing the scheduler start.

        Returns
        -------
        None
            This method does not return any value.
        """
        await super().onStarted(event)

    async def onPaused(self, event: SchedulerEvent) -> None:
        """
        Handle the scheduler pause event.

        Parameters
        ----------
        event : SchedulerEvent
            The event object representing the scheduler pause.

        Returns
        -------
        None
            This method does not return any value.
        """
        await super().onPaused(event)

    async def onResumed(self, event: SchedulerEvent) -> None:
        """
        Handle the scheduler resumption event.

        Parameters
        ----------
        event : SchedulerEvent
            The event object representing the scheduler resumption.

        Returns
        -------
        None
            This method does not return any value.
        """
        await super().onResumed(event)

    async def onShutdown(self, event: SchedulerEvent) -> None:
        """
        Handle the scheduler finalization event.

        Parameters
        ----------
        event : SchedulerEvent
            The event object representing the scheduler shutdown.

        Returns
        -------
        None
            This method does not return any value.
        """
        await super().onShutdown(event)
