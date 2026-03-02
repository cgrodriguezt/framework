from __future__ import annotations
from typing import TypeVar, Any
from orionis import Application, IApplication

T = TypeVar("T")

class FacadeMeta(type):

    # ruff: noqa: ANN401

    def __getattr__(cls, name: str) -> Any:
        """
        Redirect attribute access to the underlying service.

        Parameters
        ----------
        name : str
            The attribute or method name to access on the service.

        Returns
        -------
        Any
            The attribute or method from the underlying service.

        Raises
        ------
        AttributeError
            If the underlying service does not have the requested attribute.
        """
        # Retrieve the cached service instance
        service = cls._getServiceInstance()
        if not hasattr(service, name):
            error_msg = (
                f"'{cls.__name__}' facade's service has no attribute '{name}'"
            )
            raise AttributeError(error_msg)
        return getattr(service, name)

class Facade(metaclass=FacadeMeta):

    # Instance of the application container
    _app: IApplication = Application()

    # Cached service instance
    _service_instance: Any | None = None

    @classmethod
    def _getServiceInstance(cls) -> Any:
        """
        Retrieve the initialized service instance for the facade.

        Returns
        -------
        Any
            The initialized service instance.

        Raises
        ------
        RuntimeError
            If the facade has not been initialized via `init()`.

        Notes
        -----
        This method is used internally to access the cached service instance.
        """
        # Ensure the service instance is initialized before returning it
        if cls._service_instance is None:
            error_msg = (
                f"Facade {cls.__name__} not initialized. "
                "Call `await Facade.init()` before using methods."
            )
            raise RuntimeError(error_msg)
        return cls._service_instance

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the service name in the container.

        This method must be overridden in each concrete Facade subclass to
        specify the service accessor name.

        Returns
        -------
        str
            The name of the service in the container.

        Raises
        ------
        NotImplementedError
            If the method is not overridden in the subclass.
        """
        error_msg = (
            f"Class {cls.__name__} must define the getFacadeAccessor method"
        )
        raise NotImplementedError(error_msg)

    @classmethod
    async def init(cls, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the underlying service asynchronously.

        This method initializes the underlying service for the facade. If the
        service is asynchronous, it awaits its boot process. It must be called
        once before using the facade.

        Parameters
        ----------
        *args : Any
            Positional arguments to pass to the service initializer.
        **kwargs : Any
            Keyword arguments to pass to the service initializer.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        RuntimeError
            If the application is not booted or service initialization fails.
        """
        # Ensure the application is booted before initializing the service
        if not cls._app.isBooted:
            error_msg = "Application not booted. Boot your app first."
            raise RuntimeError(error_msg)

        try:
            # Attempt to create and cache the service instance
            instance = await cls._app.make(
                cls.getFacadeAccessor(),
                *args,
                **kwargs,
            )
            cls._service_instance = instance
        except Exception as e:
            # Handle any exceptions during service initialization
            error_msg = (
                f"Error initializing Facade {cls.__name__}: {e!s}"
            )
            raise RuntimeError(error_msg) from e

    @classmethod
    def resolve(cls) -> Any:
        """
        Return the already initialized service instance.

        Returns
        -------
        Any
            The initialized service instance.

        Notes
        -----
        This synchronous method is useful for internal use if `init()` has
        already been called.
        """
        # Return the cached service instance if already initialized
        return cls._getServiceInstance()
