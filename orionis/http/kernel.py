import asyncio
from granian.rsgi import Scope
from orionis.console.output.http_request import HTTPRequestPrinter
from orionis.foundation.contracts.application import IApplication
from orionis.http.adapters.asgi import ASGIResponseAdapter
from orionis.http.adapters.rsgi import RSGIResponseAdapter
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.response import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from orionis.http.static_assets import StaticAssets
from orionis.support.formatter.serializer import Parser

class KernelHTTP(IKernelHTTP):

    # ruff: noqa: BLE001

    def __init__(
        self,
        app: IApplication,
        assets: StaticAssets,
        # console: HTTPRequestPrinter,
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
        # self.__console: HTTPRequestPrinter = console
        # self.__print_request = app.isDebug() and not app.isProduction()
        # self.__loop = asyncio.get_event_loop()
        # self.__cached = False
        # self.__favicon: tuple | None = None

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
        # if self.__print_request:
        #     start_time = self.__loop.time()

        # # Logic to handle the RSGI request.
        # try:
        # response = HTMLResponse("Hello, World!", status_code=200)
        # response = JSONResponse({"message": "Hello, World!"}, status_code=200)
        # response = PlainTextResponse("Hello, World!", status_code=200)
        # response = RedirectResponse("/new-url", status_code=302)
        # response = FileResponse(
        #     "storage/app/public/robots.txt",
        #     status_code=200,
        #     media_type="text/plain",
        #     headers={"Content-Disposition": "attachment; filename=robots.txt"}
        # )
        # try:
        #     0 / 0
        # except Exception as e:
        #     exp = Parser.exception(e)
        #     print(exp.toDict())
        response = HTMLResponse("Hello, World!", status_code=200)
        if scope.path == "/favicon.ico":
            response = self.__assets.favicon()
        if scope.path == "/up":
            response = self.__assets.statePage()
        if scope.path == "/500":
            response = self.__assets.errorPage(status_code=500, description="Internal Server Error")
        if scope.path == "/404":
            response = self.__assets.errorPage(status_code=404, description="Page Not Found")
        if scope.path == "/403":
            response = self.__assets.errorPage(status_code=403, description="Forbidden")
        if scope.path == "/health-check":
            response = self.__assets.healthCheck()
        adapter = RSGIResponseAdapter()
        await adapter.send(response, protocol, scope)
        #     success = True
        # except Exception:
        #     # If an exception occurs, mark the request as unsuccessful.
        #     result = None
        #     success = False

        # # Print the request details to the console if in debug mode.
        # if self.__print_request:
        #     duration = self.__loop.time() - start_time
        #     self.__console.printRequest(
        #         scope.method,
        #         scope.path,
        #         duration,
        #         success=success,
        #         code=200,
        #     )

        # # Return the result of the RSGI gateway processing.
        # return result

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
        response = HTMLResponse("Hello, World!", status_code=200)
        adapter = ASGIResponseAdapter()
        await adapter.send(response, scope, receive, send)