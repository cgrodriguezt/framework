from abc import ABC, abstractmethod

class IBackgroundTask(ABC):

    @abstractmethod
    async def run(self) -> None:
        """
        Run the background task.

        Returns
        -------
        None
            This method does not return a value.
        """
        await self()
