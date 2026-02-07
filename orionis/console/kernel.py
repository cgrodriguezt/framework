from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar
from orionis.console.contracts.kernel import IKernelCLI
from orionis.console.contracts.reactor import IReactor

if TYPE_CHECKING:
    from orionis.foundation.contracts.application import IApplication

class KernelCLI(IKernelCLI):

    IGNORE_FLAGS: ClassVar[list[str]] = [
        "reactor", "-c", "-m", "-", "-i", "-q", "-B", "-O", "-OO", "-v",
        "-vv", "-d", "-x", "-E", "-s", "-S", "-u", "-I", "-W",
    ]

    async def boot(
        self,
        application: IApplication,
    ) -> None:
        """
        Initialize the kernel CLI and register commands with the reactor.

        Parameters
        ----------
        application : IApplication
            The application instance used to create the reactor.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Create and assign the reactor instance using the application factory.
        self.__reactor: IReactor = await application.make(IReactor)

    async def handle(self, args: list[str] | None = None) -> int:
        """
        Process and dispatch command line arguments to the appropriate handler.

        Parameters
        ----------
        args : list of str, optional
            List of command line arguments.

        Returns
        -------
        int
            The exit code from the command execution.
        """
        # Validate that args is a list or None
        if args is not None and not isinstance(args, list):
            error_msg = "Arguments must be provided as a list."
            raise TypeError(error_msg)

        # If no arguments are provided, show help
        if not args or len(args) == 0:
            return await self.__reactor.call("help")

        # Remove any interpreter flags from the beginning of args
        if args:
            i = 0
            while i < len(args) and args[i] in self.IGNORE_FLAGS:
                i += 1
                args = args[i:]

        # If no command is provided after removing script name, show help
        if len(args) == 0:
            return await self.__reactor.call("help")

        # If only the command is provided, call it without additional arguments
        if len(args) == 1:
            return await self.__reactor.call(args[0])

        # If command and arguments are provided, call the command with its arguments
        return await self.__reactor.call(args[0], args[1:])
