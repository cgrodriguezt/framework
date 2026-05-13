import importlib
from typing import TYPE_CHECKING
from orionis.console.output.http_request import HTTPRequestPrinter
from orionis.failure.contracts.catch import ICatch
from orionis.failure.enums.kernel_type import KernelContext
from orionis.foundation.contracts.application import IApplication
from orionis.http.adapters.request.asgi import ASGITransportAdapter
from orionis.http.adapters.request.rsgi import RSGITransportAdapter
from orionis.http.adapters.response.asgi import ASGIResponseAdapter
from orionis.http.adapters.response.rsgi import RSGIResponseAdapter
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.default.responses import DefaultResponses
from orionis.http.enums.interfaces import Interface
from orionis.http.payload.body import BodyStream
from orionis.http.request import Request
from orionis.http.routes.enums.route_types import RouteType
from orionis.http.middleware.shared.cors import CORSMiddleware
from orionis.http.middleware.shared.proxies import ProxiesMiddleware
from orionis.http.middleware.shared.rate_limit import RateLimitMiddleware
from orionis.http.middleware.shared.request import RequestMiddleware
from orionis.http.middleware.shared.security import SecurityMiddleware
from orionis.http.response import JSONResponse, Response
from orionis.http.routes.contracts.route_not_found import RouteNotFound
from orionis.http.routes.loader import RouteLoader
from orionis.http.routes.route_resolver import RouteResolver

if TYPE_CHECKING:
    from granian.rsgi import HTTPProtocol, Scope
    from orionis.http.adapters.request.contracts.transport import TransportAdapter
    from orionis.http.default.contracts.responses import IDefaultResponses
    from orionis.http.routes.contracts.loader import IRouteLoader
    from orionis.http.routes.contracts.resolved_route import ResolvedRoute

class KernelHTTP(IKernelHTTP):

    # ruff: noqa:TC001 - For Dependency injection

    def __init__(
        self,
        app: IApplication,
        catch: ICatch,
    ) -> None:
        """
        Initialize the HTTP kernel with application configuration.

        Set up the route resolver, middleware stack, response adapters,
        and request printer based on the application configuration.

        Parameters
        ----------
        app : IApplication
            Application instance providing configuration and service
            container.

        Returns
        -------
        None
        """
        # Store the application instance for later access
        self.__app = app

        # Flag to prevent multiple kernel boot attempts
        self.__boot: bool = False

        # Initialize the catch handler for exception handling in HTTP context
        self.__catch: ICatch = catch

    async def boot(self) -> None:
        """
        Boot the HTTP kernel by initializing core components.

        Resolve routes, initialize middleware stack, configure response
        adapters, and set up request printer for each protocol.

        Returns
        -------
        None
        """
        # Prevent multiple booting of the kernel which could lead to redundant
        # initialization and potential resource leaks.
        if self.__boot:
            return

        # Resolve routes with the route loader from the application
        self.__routeResolve(
            route_loader=await self.__app.build(RouteLoader),
        )

        # Build the default responses handler
        self.__default_responses: IDefaultResponses = await self.__app.build(
            DefaultResponses,
        )

        # Initialize the default middleware stack
        self.__defaultMiddleware(
            http_config=self.__app.config("http"),
            default_responses=self.__default_responses,
        )

        # Initialize response adapters for each protocol
        self.__rsgi_adapter = await self.__app.build(RSGIResponseAdapter)
        self.__asgi_adapter = await self.__app.build(ASGIResponseAdapter)

        # Initialize the request printer for console logging
        self.__request_printer = await self.__app.build(HTTPRequestPrinter)
        self.__request_printer.setEnabled(enabled=self.__app.isDebug())

        # Mark the kernel as booted to prevent re-initialization
        self.__boot = True

    def __routeResolve(
        self,
        route_loader: IRouteLoader,
    ) -> None:
        """
        Initialize route resolver with loaded routes.

        Build a route resolver instance configured with routes loaded
        from the provided route loader and cache settings.

        Parameters
        ----------
        route_loader : IRouteLoader
            Route loader instance to discover and load routes.

        Returns
        -------
        None
        """
        # Initialize route resolver with loaded routes and fallback handler
        self.__routes = RouteResolver(
            routes=route_loader.load(),
            fallback=route_loader.fallback,
            hot_cache_size=512,
        )

    def __defaultMiddleware(
        self,
        http_config: dict,
        default_responses: IDefaultResponses,
    ) -> None:
        """
        Initialize default HTTP middleware stack.

        Configure and instantiate the default middleware chain including
        proxies, security, CORS, rate limiting, and request validation
        middleware.

        Parameters
        ----------
        http_config : dict
            HTTP configuration dictionary with middleware settings.
        default_responses : IDefaultResponses
            Default response handler for middleware rejections.

        Returns
        -------
        None
        """
        # Proxies middleware detects real client IP and proxy-related preferences
        self.__proxies = ProxiesMiddleware(
            config=http_config.get("proxies"),
        )

        # Security middleware validates common header-related security concerns
        # including max header size, CRLF injection, and Host allowlist.
        self.__security = SecurityMiddleware(
            config=http_config.get("security"),
            default_responses=default_responses,
        )

        # CORS middleware handles CORS negotiation and sends appropriate
        # response headers based on app configuration.
        self.__cors = CORSMiddleware(
            config=http_config.get("cors"),
        )

        # Rate limit middleware restricts request count per client IP
        # within a time period using a sliding window algorithm.
        self.__rate_limit = RateLimitMiddleware(
            config=http_config.get("rate_limit"),
            default_responses=default_responses,
        )

        # Request middleware validates content type and maximum body size.
        self.__request = RequestMiddleware(
            config=http_config.get("request"),
            default_responses=default_responses,
        )

        # Cache max content length for BodyStream to avoid repeated
        # RequestMiddleware instantiation during request handling.
        self.__max_content_length = (
            self.__request.getMaxContentLength()
        )

    async def __rsgiResponse(
        self,
        adapter: RSGITransportAdapter,
        response: Response,
        protocol: HTTPProtocol,
    ) -> None:
        """
        Send an RSGI HTTP response through the transport adapter.

        Apply CORS post-processing headers, log request details, and send
        the response back to the client via the RSGI protocol adapter.

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
        # Apply CORS post-processing headers.
        self.__cors.after(adapter, response)

        # Log request and response details if debug mode is enabled.
        self.__request_printer.printRequest(adapter, response)

        # Send the response via RSGI protocol adapter.
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

    async def __globalMiddleware(
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
            HTTP response if middleware rejects request, None if request
            passes all middleware checks.
        """
        # Detect real client IP and proxy-related preferences.
        adapter = self.__proxies.handle(adapter)

        # Validate header size, CRLF injection, and Host allowlist.
        response = self.__security.handle(adapter)
        if response is not None:
            return response

        # Handle CORS preflight requests and validation headers.
        response = self.__cors.before(adapter)
        if response is not None:
            return response

        # Apply rate limiting with sliding-window algorithm per client.
        response = await self.__rate_limit.handle(adapter)
        if response is not None:
            return response

        # Validate content-type allowlist and content-length limit.
        response = self.__request.handle(adapter)
        if response is not None:
            return response

        # Request passed all global middleware checks.
        return None

    async def __callHandler(
        self,
        resolved_route: ResolvedRoute,
    ) -> Response:
        """
        Invoke the resolved route handler and return its response.

        Dispatch the request to the appropriate controller method,
        invokable class, or plain function based on the route type.

        Parameters
        ----------
        resolved_route : ResolvedRoute
            The resolved route descriptor with handler metadata and
            type-converted path parameters.

        Returns
        -------
        Response
            The response object returned by the route handler.

        Raises
        ------
        TypeError
            If the route handler does not return a Response object.
        """
        route = resolved_route.route
        action = route.action
        module = importlib.import_module(action["module"])

        # Plain function handler: import and invoke directly.
        if route.type == RouteType.FUNCTION:
            fn = getattr(module, action["function"])
            response = await self.__app.invoke(
                fn,
                **resolved_route.params,
            )

        # Class and method handler: build class instance and call method.
        else:
            cls = getattr(module, action["class"])
            instance = await self.__app.build(cls)
            response = await self.__app.call(
                instance,
                action["method"],
                **resolved_route.params,
            )

        # Dict to JSONResponse handler: return JSON response with dict as body.
        if isinstance(response, dict):
            response = JSONResponse(
                status_code=200,
                content=response,
            )

        # Validate that the handler returned a Response object.
        if not isinstance(response, Response):
            error_msg = "Route handler must return a Response object"
            raise TypeError(error_msg)

        # Return the valid response from the route handler.
        return response

    async def __callFallback(
        self,
        fallback: tuple[type | object, str],
    ) -> Response:
        """
        Invoke the fallback handler and return its response.

        Call the fallback handler (either a class method or callable
        function) and validate the response.

        Parameters
        ----------
        fallback : tuple[type | object, str]
            A tuple containing the handler (class or callable) and
            method name or function reference.

        Returns
        -------
        Response
            The response object returned by the fallback handler.

        Raises
        ------
        TypeError
            If the fallback handler does not return a Response object.
        """
        # Extract handler and method/function from the fallback tuple.
        _class, _method_or_func = fallback

        # Initialize the response variable.
        response = None

        # Invoke the fallback handler based on its type.
        if isinstance(_class, type) and isinstance(_method_or_func, str):
            instance = await self.__app.build(_class)
            response = await self.__app.call(instance, _method_or_func)
        elif callable(_method_or_func):
            response = await self.__app.invoke(_method_or_func)

        # Validate that the fallback handler returned a Response object.
        if not isinstance(response, Response):
            error_msg = "Fallback handler must return a Response object"
            raise TypeError(error_msg)

        # Return the valid response from the fallback handler.
        return response

    async def handleRSGI(
        self,
        scope: Scope,
        protocol: HTTPProtocol,
    ) -> object | None:
        """
        Handle an incoming RSGI HTTP request end-to-end.

        Open a per-request scope, run global middleware, resolve the
        route, build the request object, invoke the handler, and send
        the response.

        Parameters
        ----------
        scope : Scope
            Granian RSGI scope object with connection metadata.
        protocol : HTTPProtocol
            RSGI HTTP protocol object used to send the response.

        Returns
        -------
        object | None
            The result of sending the RSGI response, or None on error.
        """
        # Create a scope for each request to manage lifecycle and share
        # information between middleware and handlers.
        async with self.__app.beginScope() as request_context:

            # Set the kernel type for this scope.
            request_context.set("kernel", KernelContext.HTTP)

            # Start timing the request for performance logging.
            self.__request_printer.startTimer()

            # Create the transport adapter for RSGI.
            adapter = RSGITransportAdapter(scope)

            # Initialize request (temporarily use the adapter)
            request = adapter

            try:

                # Run global middleware chain: proxies, security, CORS,
                # rate limiting, and request validation.
                response = await self.__globalMiddleware(adapter)
                if response and isinstance(response, Response):
                    return await self.__rsgiResponse(
                        adapter, response, protocol,
                    )

                # Handle OPTIONS requests for registered routes.
                if adapter.method().upper() == "OPTIONS":
                    allowed_methods = self.__routes.options(
                        adapter.path(),
                    )
                    response = Response(
                        status_code=200,
                        headers={"Allow": ", ".join(allowed_methods)},
                    )
                    return await self.__rsgiResponse(
                        adapter, response, protocol,
                    )

                # Resolve the route matching method and path.
                resolved_route = self.__routes.resolve(
                    method=adapter.method(),
                    path=adapter.path(),
                )

                # Build BodyStream and Request for the resolved route.
                body_stream = BodyStream(
                    interface=Interface.RSGI,
                    receive_or_protocol=protocol,
                    max_body_size=self.__max_content_length,
                )
                request = Request(
                    interface=Interface.RSGI,
                    adapter=adapter,
                    body_stream=body_stream,
                    params=resolved_route.params,
                )

                # Register the request in scope for dependency injection.
                request_context[Request] = request

                # Invoke the resolved route handler.
                response = await self.__callHandler(resolved_route)

            except Exception as e:  # noqa: BLE001

                # If exception is 404 and fallback route exists,
                # attempt to call the fallback handler.
                if isinstance(e, RouteNotFound):
                    fallback = self.__routes.fallback()
                    if fallback is not None and fallback != (None, None):
                        return await self.__callFallback(fallback)

                # Delegate exception handling to the catch service
                response = await self.__catch.exception(e, request)

            # Send the response back to the client via RSGI protocol adapter.
            return await self.__rsgiResponse(adapter, response, protocol)

    async def handleASGI(
        self,
        scope: dict,
        receive: object,
        send: object,
    ) -> None:
        """
        Handle an incoming ASGI HTTP request end-to-end.

        Open a per-request scope, run global middleware, resolve the
        route, build the request object, invoke the handler, and send
        the response.

        Parameters
        ----------
        scope : dict
            ASGI connection scope dict with request metadata.
        receive : object
            ASGI receive callable for reading request body and events.
        send : object
            ASGI send callable for sending response messages.

        Returns
        -------
        None
        """
        # Create a scope for each request to manage lifecycle and share
        # information between middleware and handlers.
        async with self.__app.beginScope() as request_context:

            # Set the kernel type for this scope.
            request_context.set("kernel", KernelContext.HTTP)

            # Start timing the request for performance logging.
            self.__request_printer.startTimer()

            # Create the transport adapter for ASGI.
            adapter = ASGITransportAdapter(scope)

            # Initialize request (temporarily use the adapter)
            request = adapter

            try:

                # Run global middleware chain: proxies, security, CORS,
                # rate limiting, and request validation.
                response = await self.__globalMiddleware(adapter)
                if response and isinstance(response, Response):
                    return await self.__asgiResponse(
                        adapter, response, receive, send,
                    )

                # Handle OPTIONS requests for registered routes.
                if adapter.method().upper() == "OPTIONS":
                    allowed_methods = self.__routes.options(
                        adapter.path(),
                    )
                    response = Response(
                        status_code=200,
                        headers={"Allow": ", ".join(allowed_methods)},
                    )
                    return await self.__asgiResponse(
                        adapter, response, receive, send,
                    )

                # Resolve the route matching method and path.
                resolved_route = self.__routes.resolve(
                    method=adapter.method(),
                    path=adapter.path(),
                )

                # Build BodyStream and Request for the resolved route.
                body_stream = BodyStream(
                    interface=Interface.ASGI,
                    receive_or_protocol=receive,
                    max_body_size=self.__max_content_length,
                )
                request = Request(
                    interface=Interface.ASGI,
                    adapter=adapter,
                    body_stream=body_stream,
                    params=resolved_route.params,
                )

                # Register the request in scope for dependency injection.
                request_context[Request] = request

                # Invoke the resolved route handler.
                response = await self.__callHandler(resolved_route)

            except Exception as e: # noqa: BLE001

                # If exception is 404 and fallback route exists,
                # attempt to call the fallback handler.
                if isinstance(e, RouteNotFound):
                    fallback = self.__routes.fallback()
                    if fallback is not None and fallback != (None, None):
                        return await self.__callFallback(fallback)

                # Delegate exception handling to the catch service
                response = await self.__catch.exception(e, request)

            # Send the response back to the client via ASGI protocol adapter.
            return await self.__asgiResponse(adapter, response, receive, send)
