from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.failure.enums.kernel_type import KernelType

class ICatch(ABC):

    @abstractmethod
    def exception(
        self,
        kernel: KernelType,
        request: type[Any],
        exception: BaseException | Exception,
    ) -> None:
        """
        Handle and report exceptions during CLI execution.

        Parameters
        ----------
        kernel : KernelType
            The kernel instance associated with the CLI, or None if not available.
        request : type[Any]
            The request or arguments associated with the CLI command.
        exception : BaseException | Exception
            The exception instance to be handled.

        Returns
        -------
        None
            This method performs side effects such as logging and output.
        """
