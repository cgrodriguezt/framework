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

    def __init__(
        self,
        log: ILogger,
    ) -> None:
        """
        Initialize the InspireTaskListener instance.

        Parameters
        ----------
        log : ILogger
            Logger service for logging task events.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        self.log = log

    async def taskAdded(self, event: TaskEvent) -> None:
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
        await super().taskAdded(event)
        self.log.info("Task added")

    async def taskRemoved(self, event: TaskEvent) -> None:
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
        await super().taskAdded(event)
        self.log.info("Task removed")

    async def taskExecuted(self, event: TaskEvent) -> None:
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
        await super().taskAdded(event)
        self.log.info("Task executed")

    async def taskError(self, event: TaskEvent) -> None:
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
        await super().taskAdded(event)
        self.log.error("Task error")

    async def taskMissed(self, event: TaskEvent) -> None:
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
        await super().taskAdded(event)
        self.log.warning("Task missed")

    async def taskSubmitted(self, event: TaskEvent) -> None:
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
        await super().taskAdded(event)
        self.log.info("Task submitted")

    async def taskMaxInstances(self, event: TaskEvent) -> None:
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
        await super().taskAdded(event)
        self.log.warning("Task max instances reached")
