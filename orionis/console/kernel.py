from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.console.contracts.kernel import IKernelCLI

if TYPE_CHECKING:
    from orionis.console.contracts.reactor import IReactor

class KernelCLI(IKernelCLI):

    def __init__(
        self,
        reactor: IReactor,
    ) -> None:
        """
        Initialize KernelCLI with application, reactor, and catch dependencies.

        Parameters
        ----------
        reactor : IReactor
            The reactor for command dispatching.
        catch : ICatch
            The exception handler.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Store the reactor instance for command dispatching
        self.__reactor = reactor

    def handle(self, args: list[str] | None = None) -> None:
        """
        Process and dispatch command line arguments to the appropriate handler.

        Parameters
        ----------
        args : list of str, optional
            List of command line arguments.

        Returns
        -------
        None
            Returns None. May raise exceptions if input is invalid.
        """
        # Validate that args is a list or None
        if args is not None and not isinstance(args, list):
            error_msg = "Arguments must be provided as a list."
            raise TypeError(error_msg)

        # If no arguments are provided, show help
        if not args or len(args) == 0:
            return self.__reactor.call("help")

        # Remove the first argument (script name) if present
        if len(args) > 0:
            args = args[1:]

        # If no command is provided after removing script name, show help
        if len(args) == 0:
            return self.__reactor.call("help")

        # If only the command is provided, call it without additional arguments
        if len(args) == 1:
            return self.__reactor.call(args[0])

        # If command and arguments are provided, call the command with its arguments
        return self.__reactor.call(args[0], args[1:])
