from abc import ABC, abstractmethod

class IServiceProvider(ABC):

    @abstractmethod
    async def register(self) -> None:
        """
        Register services and components into the application container.

        This asynchronous method should be implemented by subclasses to bind services,
        configurations, or other components to the application container. It is called
        during the application's service registration phase.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        NotImplementedError
            If the method is not overridden in a subclass.
        """

    @abstractmethod
    async def boot(self) -> None:
        """
        Perform post-registration initialization tasks.

        This asynchronous method is called after all services have been registered.
        Subclasses may override this method to initialize services or perform operations
        required at application boot time.

        Returns
        -------
        None
            This method does not return a value.
        """
