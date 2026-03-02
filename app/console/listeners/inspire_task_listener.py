from orionis.console.base.listener import BaseTaskListener
from orionis.console.entities.task_event import TaskEvent
from orionis.services.log.contracts.log_service import ILogger

class InspireTaskListener(BaseTaskListener):

    # --------------------------------------------------------------------------
    # Methods can be synchronous or asynchronous depending on the logic
    # you need to apply. If you do not have any await operations,
    # define them as synchronous. The Orionis event dispatcher will
    # handle both cases.
    # --------------------------------------------------------------------------

    def __init__(self, log: ILogger) -> None:
        """
        Initialize the InspireTaskListener instance.

        Parameters
        ----------
        log : ILogger
            Logger service for logging task events.
            (Injected by the framework)

        Returns
        -------
        None
            This constructor does not return a value.
        """
        self._log = log

    async def onTaskAdded(self, event: TaskEvent) -> None:
        """
        Handle the event when a task is added.

        Parameters
        ----------
        event : TaskEvent
            The event object containing information about the added task.

        Returns
        -------
        None
            This method does not return a value.

        """
        await super().onTaskAdded(event)
        self._log.info("Task added")

    async def onTaskRemoved(self, event: TaskEvent) -> None:
        """
        Handle the event when a task is removed.

        Parameters
        ----------
        event : TaskEvent
            The event object containing information about the removed task.

        Returns
        -------
        None
            This method does not return a value.

        """
        await super().onTaskRemoved(event)
        self._log.info("Task removed")

    async def onTaskExecuted(self, event: TaskEvent) -> None:
        """
        Handle the event when a task is executed.

        Parameters
        ----------
        event : TaskEvent
            The event object containing information about the executed task.

        Returns
        -------
        None
            This method does not return a value.

        """
        await super().onTaskExecuted(event)
        self._log.info("Task executed")

    async def onTaskError(self, event: TaskEvent) -> None:
        """
        Handle the event when a task encounters an error.

        Parameters
        ----------
        event : TaskEvent
            The event object containing information about the task error.

        Returns
        -------
        None
            This method does not return a value.

        """
        await super().onTaskError(event)
        self._log.error("Task error")

    async def onTaskMissed(self, event: TaskEvent) -> None:
        """
        Handle the event when a task is missed.

        Parameters
        ----------
        event : TaskEvent
            The event object containing information about the missed task.

        Returns
        -------
        None
            This method does not return a value.

        """
        await super().onTaskMissed(event)
        self._log.warning("Task missed")

    async def onTaskSubmitted(self, event: TaskEvent) -> None:
        """
        Handle the event when a task is submitted.

        Parameters
        ----------
        event : TaskEvent
            The event object containing information about the submitted task.

        Returns
        -------
        None
            This method does not return a value.

        """
        await super().onTaskSubmitted(event)
        self._log.info("Task submitted")

    async def onTaskMaxInstances(self, event: TaskEvent) -> None:
        """
        Handle the event when a task reaches its maximum allowed instances.

        Parameters
        ----------
        event : TaskEvent
            The event object containing information about the max instances event.

        Returns
        -------
        None
            This method does not return a value.

        """
        await super().onTaskMaxInstances(event)
        self._log.warning("Task max instances reached")
