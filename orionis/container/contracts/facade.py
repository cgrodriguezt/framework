from abc import ABC, abstractmethod
from typing import Any

class IFacade(ABC):

    # ruff: noqa: ANN401

    @classmethod
    @abstractmethod
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
