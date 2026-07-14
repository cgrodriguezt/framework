from __future__ import annotations
from typing import Any, TYPE_CHECKING
from orionis.container.facades.meta import FacadeMeta

if TYPE_CHECKING:
    from orionis.foundation.contracts.application import IApplication

class Facade(metaclass=FacadeMeta):

    # ruff: noqa: PLC0415

    # Cached application instance shared across all facade subclasses
    _application: IApplication | None = None
    _pinned_instance: Any = None

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the container accessor key for this facade.

        Returns
        -------
        str
            Return the service key used to resolve the container binding.

        Raises
        ------
        NotImplementedError
            Raise when the subclass does not implement this method.
        """
        # Enforce subclass implementation for the accessor key.
        error_msg = f"Class {cls.__name__} must define getFacadeAccessor()"
        raise NotImplementedError(error_msg)

    @classmethod
    async def resolve(cls, *args: object, **kwargs: object) -> object:
        """
        Resolve the service instance bound to this facade.

        Parameters
        ----------
        *args : object
            Forward positional arguments to the container make call.
        **kwargs : object
            Forward keyword arguments to the container make call.

        Returns
        -------
        object
            Return the resolved service instance from the application.

        Raises
        ------
        RuntimeError
            Raise when the application has not been booted.
        """
        # Lazily initialize the shared application instance.
        if cls._application is None:
            from orionis.foundation.application import Application
            cls._application = Application()

        # Guard against resolution before application boot.
        if not cls._application.isBooted:
            error_msg = "Application not booted. Boot your app first."
            raise RuntimeError(error_msg)

        # Delegate service construction to the application container.
        return await cls._application.make(
            cls.getFacadeAccessor(),
            *args,
            **kwargs,
        )

    @classmethod
    async def pin(cls) -> None:
        """
        Pin the resolved instance on this facade class.

        Returns
        -------
        None
            Return ``None`` after storing the currently resolved instance.
        """
        # Cache the currently resolved instance for direct reuse.
        cls._pinned_instance = await cls.resolve()

    @classmethod
    def unpin(cls) -> None:
        """
        Clear the pinned instance from this facade class.

        Returns
        -------
        None
            Return ``None`` after clearing the cached pinned instance.
        """
        # Remove the cached pinned instance to restore normal resolution.
        cls._pinned_instance = None
