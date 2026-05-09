from granian.rsgi import Scope, HTTPProtocol
from orionis.console.output.http_request import HTTPRequestPrinter
from orionis.failure.enums.kernel_type import KernelContext
from orionis.foundation.contracts.application import IApplication
from orionis.http.adapters.request.rsgi import RSGITransportAdapter
from orionis.http.adapters.request.contracts.transport import TransportAdapter
from orionis.http.adapters.response.asgi import ASGIResponseAdapter
from orionis.http.adapters.response.rsgi import RSGIResponseAdapter
from orionis.http.payload.body import BodyStream
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.default.responses import DefaultResponses
from orionis.http.enums.interfaces import Interface
from orionis.http.middleware.cors import CORSMiddleware
from orionis.http.middleware.proxies import ProxiesMiddleware
from orionis.http.middleware.request import RequestMiddleware
from orionis.http.middleware.security import SecurityMiddleware
from orionis.http.middleware.rate_limit import RateLimitMiddleware
from orionis.http.request import Request
from orionis.http.response import Response
from orionis.http.routes.engine import RoutingEngine

class KernelHTTP(IKernelHTTP):

    def __init__(
        self,
        app: IApplication,
        default_responses: DefaultResponses,
        asgi_adapter: ASGIResponseAdapter,
        rsgi_adapter: RSGIResponseAdapter,
        route_engine: RoutingEngine,
        http_request_printer: HTTPRequestPrinter,
    ) -> None:

        # Guardar instancia de la app para generar un scope en cada request
        self.__app = app

        # Global middlewares
        # Middleware de Proxies para detectar la IP real del cliente y
        # otras preferencias relacionadas con proxies inversos.
        self.__proxies = ProxiesMiddleware(
            config=app.config("http.proxies"),
        )

        # Middleware de Seguridad para validar headers comunes relacionados con
        # seguridad, como el tamaño máximo de headers, inyección de CRLF,
        # allowlist de Host, etc.
        self.__security = SecurityMiddleware(
            config=app.config("http.security"),
            default_responses=default_responses,
        )

        # Middleware de CORS para manejar la negociación de CORS y enviar los headers
        # correspondientes según la configuración de la app.
        self.__cors = CORSMiddleware(
            config=app.config("http.cors"),
        )

        # Middleware de Rate Limiting para limitar la cantidad de requests por IP
        # cliente en un periodo de tiempo determinado, utilizando un
        # algoritmo de sliding window.
        self.__rate_limit = RateLimitMiddleware(
            config=app.config("http.rate_limit"),
            default_responses=default_responses,
        )

        self.__request = RequestMiddleware(
            config=app.config("http.request"),
            default_responses=default_responses,
        )
        self.__max_content_length = self.__request.getMaxContentLength()

        # Descubrir rutas y guardarlas en memoria para resolverlas en cada request
        self.__route_engine = route_engine
        self.__route_engine.discover()

        # Guardar adaptadores para enviar respuestas en cada protocolo
        self.__rsgi_adapter = rsgi_adapter
        self.__asgi_adapter = asgi_adapter

        # Guardar recursos por defecto para manejar excepciones y otras
        # situaciones comunes
        self.__defaults = default_responses

        # Guardar instancia del impresor de requests para mostrar información de
        # cada request en consola solo si la app está en modo debug
        self.__request_printer = http_request_printer
        self.__request_printer.setEnabled(enabled=app.isDebug())

    async def __rsgiResponse(
        self,
        adapter: RSGITransportAdapter,
        response: Response,
        protocol: HTTPProtocol,
    ) -> None:
        """
        Send RSGI HTTP response through transport adapter.

        Apply CORS post-processing headers, log request details, and send
        the response back to the client via RSGI protocol adapter.

        Parameters
        ----------
        adapter : RSGITransportAdapter
            RSGI transport adapter with HTTP scope and client connection.
        response : Response
            HTTP response object to send to client.
        protocol : HTTPProtocol
            RSGI HTTP protocol version indicator.

        Returns
        -------
        None
        """
        # Apply CORS post-processing to add necessary headers based
        # on the request and response.
        self.__cors.after(adapter, response)

        # Log request and response details to console if debug mode is enabled.
        self.__request_printer.printRequest(adapter, response)

        # Send the response back to the client using the RSGI protocol adapter.
        return await self.__rsgi_adapter.send(adapter, response, protocol)

    async def __asgiResponse(
        self,
        adapter: TransportAdapter,
        response: Response,
        receive: object,
        send: object,
    ) -> None:
        """
        Send ASGI HTTP response through transport adapter.

        Apply CORS post-processing headers, log request details, and send
        the response back to the client via ASGI protocol adapter.

        Parameters
        ----------
        adapter : TransportAdapter
            Transport adapter encapsulating the HTTP request.
        response : Response
            HTTP response object to send to client.
        receive : object
            ASGI receive callable for reading request body.
        send : object
            ASGI send callable for sending response.

        Returns
        -------
        None
        """
        # Apply CORS post-processing headers based on request and response.
        self.__cors.after(adapter, response)

        # Log request and response details if debug mode is enabled.
        self.__request_printer.printRequest(adapter, response)

        # Send the response back to the client via ASGI protocol adapter.
        return await self.__asgi_adapter.send(
            adapter, response, receive, send,
        )

    async def __before(
        self,
        adapter: TransportAdapter,
    ) -> Response | None:
        """
        Execute global middleware chain on incoming request.

        Process request through middleware pipeline: proxies detection,
        security validation, CORS negotiation, rate limiting, and request
        normalization.

        Parameters
        ----------
        adapter : TransportAdapter
            Transport adapter encapsulating the HTTP request.

        Returns
        -------
        Response | None
            HTTP response if middleware rejects request, None if
            request passes all middleware checks.
        """
        # Detect real client IP and proxy-related preferences.
        adapter = self.__proxies.handle(adapter)

        # Validate header size, CRLF injection, and Host allowlist.
        response = self.__security.handle(adapter)
        if response is not None:
            return response

        # Handle CORS preflight and headers.
        response = self.__cors.before(adapter)
        if response is not None:
            return response

        # Apply rate limiting with sliding-window algorithm per client IP.
        response = await self.__rate_limit.handle(adapter)
        if response is not None:
            return response

        # Validate content-type allowlist, content-length limit, and optionally
        # override the HTTP method via request header.
        response = self.__request.handle(adapter)
        if response is not None:
            return response

        # If we reach this point, the request has passed all global middleware checks
        # and is ready to be processed by the route handler.
        return None

    async def handleRSGI(
        self,
        scope: Scope,
        protocol: HTTPProtocol,
    ) -> object | None:

        # Crear un scope de la app para cada request, que se encargará de manejar el
        # ciclo de vida de la request y compartir información entre middlewares
        # y handlers durante el manejo de la request
        async with self.__app.beginScope() as request_context:

            # Definir el tipo de Kernel del Scope.
            request_context.set("kernel", KernelContext.HTTP)

            # Iniciar el contador de tiempo para calcular la duración de la request
            # y mostrarla en consola junto con el método, ruta y código de respuesta
            self.__request_printer.startTimer()

            # Crear el transport adapter de RSGI
            adapter = RSGITransportAdapter(scope)

            # Middleware Global de Proxies para detectar la IP real del cliente
            # y otras preferencias relacionadas con proxies inversos.
            response = await self.__before(adapter)
            if response is not None:
                return await self.__rsgiResponse(adapter, response, protocol)

            # Crear el objeto Request a partir del scope
            request = Request(
                interface=Interface.RSGI,
                adapter=adapter,
                body_stream=BodyStream(
                    interface=Interface.RSGI,
                    receive_or_protocol=protocol,
                    max_body_size=self.__max_content_length,
                ),
            )

            # Registrar la request en el contenedor para que siempre se resuelva
            # la misma instancia durante el ciclo de vida de la request, y
            # esté disponible en cualquier parte de la app a través del contenedor.
            self.__app.instance(None, request)

            return await self.__rsgiResponse(
                adapter = adapter,
                response = Response(
                    status_code=200,
                    content="Hello, Orionis HTTP Kernel with RSGI!",
                ),
                protocol = protocol,
            )


        return None











        # try:
        #     request = Request(Interface.RSGI.value, scope, protocol)
        #     ready, handle, params = self.__route_engine.resolve(
        #         path=request.path,
        #         method=request.method,
        #         expects_json=request.expectsJson(),
        #     )

        #     self.__request_printer.printRequest(
        #         method=request.method,
        #         path=request.path,
        #         start_time=start_time,
        #         code=handle.getStatusCode(),
        #     )

        # except Exception as e:
        #     handle = self.__defaults.exceptionPage(
        #         exception=e,
        #         request_method=scope.method,
        #         request_path=scope.path,
        #     )
        # await self.__rsgi_adapter.send(handle, protocol, scope)

    async def handleASGI(
        self,
        scope: object,
        receive: object,
        send: object,
    ) -> object:
        try:
            request = Request(Interface.ASGI.value, scope, receive)
            ready, handle, params = self.__route_engine.resolve(
                path=request.path,
                method=request.method,
                expects_json=request.expectsJson(),
            )
        except Exception as e:
            handle = self.__defaults.exceptionPage(
                exception=e,
                request_method=scope["method"],
                request_path=scope["path"],
            )
        await self.__asgi_adapter.send(handle, scope, receive, send)
