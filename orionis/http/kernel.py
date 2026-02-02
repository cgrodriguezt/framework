import asyncio
from granian.rsgi import Scope
from orionis.console.output.http_request import HTTPRequestPrinter
from orionis.failure.contracts.catch import ICatch
from orionis.foundation.contracts.application import IApplication
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.core.asgi import ASGIGateway
from orionis.http.core.rsgi import RSGIGateway

class KernelHTTP(IKernelHTTP):

    # ruff: noqa: BLE001

    def __init__(
        self,
        app: IApplication,
        console: HTTPRequestPrinter,
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
        self.__catch: ICatch = app.make(ICatch)
        self.__console: HTTPRequestPrinter = console
        self.__debug = app.config("app.debug")

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
        if self.__debug:
            loop = asyncio.get_event_loop()
            start_time = loop.time()

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
        if self.__debug:
            duration = loop.time() - start_time
            self.__console.printRequest(
                scope.method,
                scope.path,
                duration,
                success=success,
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
        if self.__debug:
            loop = asyncio.get_event_loop()
            start_time = loop.time()

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
        if self.__debug:
            duration = loop.time() - start_time
            self.__console.printRequest(
                scope["method"],
                scope["path"],
                duration,
                success=success,
            )

        # Return the result of the ASGI gateway processing.
        return result
