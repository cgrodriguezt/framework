from __future__ import annotations
from abc import ABC, abstractmethod

class ICatch(ABC):

    @abstractmethod
    async def exception(
        self,
        exception: BaseException | Exception,
    ) -> None:
        """
        Handle an exception based on the current kernel context.

        Parameters
        ----------
        exception : BaseException | Exception
            The exception instance to handle.

        Returns
        -------
        None
            This method performs side effects and returns None.

        Notes
        -----
        Determines the context and delegates exception handling accordingly.
        """
