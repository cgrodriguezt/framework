from abc import ABC, abstractmethod
from orionis.console.entities.task_event import TaskEvent

class IBaseTaskListener(ABC):

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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
