import asyncio
from granian.rsgi import Scope
from orionis.console.output.http_request import HTTPRequestPrinter
from orionis.foundation.contracts.application import IApplication
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.core.asgi import ASGIGateway
from orionis.http.core.rsgi import RSGIGateway
from orionis.http.static_assets import StaticAssets

class KernelHTTP(IKernelHTTP):

    # ruff: noqa: BLE001

    def __init__(
        self,
        app: IApplication,
        console: HTTPRequestPrinter,
        assets: StaticAssets,
    ) -> None:
        """
        Initialize the KernelHTTP instance.

        Parameters
        ----------
        app : IApplication
            The application container instance providing services and dependencies.
        console : HTTPRequestPrinter
            The console printer for HTTP request output.

        Returns
        -------
        None
            This constructor initializes internal dependencies for HTTP operations.

        Raises
        ------
        ValueError
            If `app` is not an instance of `IApplication`.
        """
        # Initialize the catch instance and console printer.
        self.__app: IApplication = app
        self.__assets: StaticAssets = assets
        self.__console: HTTPRequestPrinter = console
        self.__print_request = app.isDebug() and not app.isProduction()
        self.__loop = asyncio.get_event_loop()
        self.__cached = False
        self.__favicon: tuple | None = None

    async def cacheStaticAssets(self) -> None:
        """
        Cache static assets for efficient reuse.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return a value.
        """
        # Avoid re-caching if already done.
        if self.__cached:
            return

        # Prepare the favicon response tuple for quick access.
        self.__favicon = self.__assets.favicon()
        self.__well_known = self.__assets.wellKnown()
        self.__up_page = self.__assets.healthPage()
        self.__cached = True

    async def handleRSGI(
        self,
        scope: Scope,
        protocol: object,
    ) -> object:
        """
        Handle an RSGI HTTP request and print request details.

        Parameters
        ----------
        scope : Scope
            The RSGI scope object containing request information.
        protocol : object
            The protocol instance for the RSGI server.

        Returns
        -------
        object
            The result of the RSGI gateway handling the request.
        """
        # Only measure time and print if in debug mode.
        if self.__print_request:
            start_time = self.__loop.time()

        if scope.path == '/favicon.ico':
            return protocol.response_bytes(200, *self.__favicon)
        if scope.path.startswith('/.well-known/'):
            return protocol.response_bytes(200, *self.__well_known)
        if scope.path == '/up':
            body, headers = self.__up_page
            body = body.replace(b'{{time}}', f"{(self.__loop.time() - start_time)* 1000:.0f}".encode())
            return protocol.response_bytes(200, headers, body)

        # Logic to handle the RSGI request.
        try:
            # Process the request using the RSGI gateway.
            result = await RSGIGateway(scope, protocol)
            success = True
        except Exception:
            # If an exception occurs, mark the request as unsuccessful.
            result = None
            success = False

        # Print the request details to the console if in debug mode.
        if self.__print_request:
            duration = self.__loop.time() - start_time
            self.__console.printRequest(
                scope.method,
                scope.path,
                duration,
                success=success,
                code=200,
            )

        # Return the result of the RSGI gateway processing.
        return result

    async def handleASGI(
        self,
        scope: object,
        receive: object,
        send: object,
    ) -> object:
        """
        Handle an ASGI HTTP request and print request details.

        Parameters
        ----------
        scope : object
            The ASGI scope dictionary containing request information.
        receive : object
            The receive callable for the ASGI server.
        send : object
            The send callable for the ASGI server.

        Returns
        -------
        object
            The result of the ASGI gateway handling the request.
        """
        # Only measure time and print if in debug mode.
        if self.__print_request:
            start_time = self.__loop.time()

        # Logic to handle the ASGI request.
        try:
            # Process the request using the ASGI gateway.
            result = await ASGIGateway(scope, receive, send)
            success = True
        except Exception:
            # If an exception occurs, mark the request as unsuccessful.
            result = None
            success = False

        # Print the request details to the console if in debug mode.
        if self.__print_request:
            duration = self.__loop.time() - start_time
            self.__console.printRequest(
                scope["method"],
                scope["path"],
                duration,
                success=success,
            )

        # Return the result of the ASGI gateway processing.
        return result
