from orionis.console.exceptions import CLIOrionisValueError
from orionis.failure.contracts.catch import ICatch
from orionis.foundation.contracts.application import IApplication
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.core.asgi import ASGIGateway
from orionis.http.core.rsgi import RSGIGateway

class KernelHTTP(IKernelHTTP):

    def __init__(
        self,
        app: IApplication,
    ) -> None:
        """
        Initializes the KernelCLI instance with the provided application container.

        Parameters
        ----------
        app : IApplication
            The application container instance that provides access to services and dependencies.

        Returns
        -------
        None
            This constructor does not return a value. It initializes internal dependencies required for CLI operations.

        Raises
        ------
        CLIOrionisValueError
            If the provided `app` argument is not an instance of `IApplication`.
        """
        # Validate that the app is an instance of IApplication
        if not isinstance(app, IApplication):
            raise CLIOrionisValueError(
                f"Failed to initialize TestKernel: expected IApplication, got {type(app).__module__}.{type(app).__name__}.",
            )

        # Retrieve and initialize the catch instance from the application container.
        self.__catch: ICatch = app.make(ICatch)

    async def handle(self, *args) -> None:
        if args and isinstance(args[0], dict):
            scope = args[0]
            method = scope.get("method")
            path = scope.get("path")
            print(f"[{method}] - {path}")
            await ASGIGateway(*args)
        else:
            method = args[0].method
            path = args[0].path
            print(f"[{method}] - {path}")
            await RSGIGateway(*args)
