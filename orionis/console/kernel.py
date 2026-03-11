from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar
from orionis.console.contracts.kernel import IKernelCLI
from orionis.console.core.contracts.reactor import IReactor

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
            return await self.__reactor.call("list")

        # Remove any interpreter flags from the beginning of args
        for arg in args[:]:
            if arg in self.IGNORE_FLAGS:
                args.remove(arg)
                continue
            break

        # If no command is provided after removing script name, show help
        if len(args) == 0 or args[0] in ("help", "--help", "-h"):
            return await self.__reactor.call("list")

        # Return the result of calling the command with the remaining arguments
        return await self.__reactor.call(args[0], args[1:])
