import importlib
from typing import TYPE_CHECKING
import msgspec
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
from orionis.http.layer.shared.cors import CORSMiddleware
from orionis.http.layer.shared.proxies import ProxiesMiddleware
from orionis.http.layer.shared.rate_limit import RateLimitMiddleware
from orionis.http.layer.shared.request import RequestMiddleware
from orionis.http.layer.shared.security import SecurityMiddleware
from orionis.http.payload.body import BodyStream
from orionis.http.request import Request
from orionis.http.response import JSONResponse, Response
from orionis.http.routes.enums.route_types import RouteType
from orionis.http.routes.exceptions.route_not_found import RouteNotFound
from orionis.http.routes.loader import RouteLoader
from orionis.http.routes.route_resolver import RouteResolver
from orionis.schemas.exceptions.validation import ValidationException

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from granian.rsgi import HTTPProtocol, Scope
    from orionis.http.adapters.request.contracts.transport import TransportAdapter
    from orionis.http.default.contracts.responses import IDefaultResponses
    from orionis.http.routes.contracts.loader import IRouteLoader
    from orionis.http.routes.entities.resolved_route import ResolvedRoute

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
        self.__app = app
        self.__boot: bool = False
        self.__catch: ICatch = catch
        self.__module_cache: dict[str, object] = {}
        self.__function_cache: dict[tuple[str, str], object] = {}
        self.__class_cache: dict[tuple[str, str], type] = {}
        self.__middleware_cache: dict[tuple, tuple] = {}

    async def boot(self) -> None:
        """
        Boot the HTTP kernel by initializing core components.

        Resolve routes, initialize middleware stack, configure response
        adapters, and set up request printer for each protocol.

        Returns
        -------
        None
        """
        if self.__boot:
            return

        self.__routeResolve(
            route_loader=await self.__app.build(RouteLoader),
        )
        await self.__preloadMiddleware()
        self.__default_responses: IDefaultResponses = await self.__app.build(
            DefaultResponses,
        )
        self.__defaultMiddleware(
            http_config=self.__app.config("http"),
            default_responses=self.__default_responses,
        )
        self.__rsgi_adapter = await self.__app.build(RSGIResponseAdapter)
        self.__asgi_adapter = await self.__app.build(ASGIResponseAdapter)
        self.__request_printer = await self.__app.build(HTTPRequestPrinter)
        self.__request_printer.setEnabled(enabled=self.__app.isDebug())
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
        self.__proxies = ProxiesMiddleware(
            config=http_config.get("proxies"),
        )
        self.__security = SecurityMiddleware(
            config=http_config.get("security"),
            default_responses=default_responses,
        )
        self.__cors = CORSMiddleware(
            config=http_config.get("cors"),
        )
        self.__rate_limit = RateLimitMiddleware(
            config=http_config.get("rate_limit"),
            default_responses=default_responses,
        )
        self.__request = RequestMiddleware(
            config=http_config.get("request"),
            default_responses=default_responses,
        )
        self.__max_content_length = self.__request.getMaxContentLength()

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
        self.__cors.after(adapter, response)
        self.__request_printer.printRequest(adapter, response)
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
        self.__cors.after(adapter, response)
        self.__request_printer.printRequest(adapter, response)
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
        adapter = self.__proxies.handle(adapter)

        response = self.__security.handle(adapter)
        if response is not None:
            return response

        response = self.__cors.before(adapter)
        if response is not None:
            return response

        response = await self.__rate_limit.handle(adapter)
        if response is not None:
            return response

        response = self.__request.handle(adapter)
        if response is not None:
            return response

        return None

    async def __preloadMiddleware(self) -> None:
        """
        Pre-build middleware instances for all routes at boot time.

        Iterate every compiled route and eagerly resolve each middleware
        class through the container. Results are stored keyed by the
        immutable stack tuple so identical stacks share the same instances.

        Returns
        -------
        None
        """
        for route in self.__routes.allRoutes():
            stack = route.compiled_middlewares
            if stack and stack not in self.__middleware_cache:
                built = [await self.__app.build(mw_class) for mw_class in stack]
                self.__middleware_cache[stack] = tuple(built)

    async def __requestLayer(
        self,
        request: Request,
        resolved_route: ResolvedRoute,
    ) -> Response:
        """
        Execute the request middleware pipeline for the resolved route.

        Parameters
        ----------
        request : Request
            Incoming HTTP request.

        resolved_route : ResolvedRoute
            Route resolution result containing the matched route
            and resolved path parameters.

        Returns
        -------
        Response
            Final HTTP response.
        """
        stack = resolved_route.route.compiled_middlewares

        if not stack:
            return await self.__callHandler(resolved_route)

        instances = self.__middleware_cache.get(stack)
        if instances is None:
            built = [await self.__app.build(mw_class) for mw_class in stack]
            instances = tuple(built)
            self.__middleware_cache[stack] = instances

        async def final_handler() -> Response:
            return await self.__callHandler(resolved_route)

        # Inline recursive dispatch — avoids MiddlewarePipeline allocation.
        # Each layer enforces single-invocation of next() via `called` flag.
        async def dispatch(index: int) -> Response:
            if index >= len(instances):
                return await final_handler()

            called = False

            async def next_fn() -> Response:
                nonlocal called
                if called:
                    error_msg = (
                        "next() has already been called "
                        "in this middleware layer."
                    )
                    raise RuntimeError(error_msg)
                called = True
                return await dispatch(index + 1)

            return await instances[index].handle(request, next_fn)

        return await dispatch(0)

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
        module_name = action["module"]
        module = self.__module_cache.get(module_name)
        if module is None:
            module = importlib.import_module(module_name)
            self.__module_cache[module_name] = module

        if route.type == RouteType.FUNCTION:
            function_name = action["function"]
            function_key = (module_name, function_name)
            fn = self.__function_cache.get(function_key)
            if fn is None:
                fn = getattr(module, function_name)
                self.__function_cache[function_key] = fn
            response = await self.__app.invoke(
                fn,
                **resolved_route.params,
            )
        else:
            class_name = action["class"]
            class_key = (module_name, class_name)
            cls = self.__class_cache.get(class_key)
            if cls is None:
                cls = getattr(module, class_name)
                self.__class_cache[class_key] = cls
            instance = await self.__app.build(cls)
            response = await self.__app.call(
                instance,
                action["method"],
                **resolved_route.params,
            )

        if isinstance(response, (dict, msgspec.Struct)):
            response = JSONResponse(status_code=200, content=response)

        if isinstance(response, Response):
            return response

        error_msg = "Route handler must return a Response object"
        raise TypeError(error_msg)

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
        _class, _method_or_func = fallback
        response = None
        if isinstance(_class, type) and isinstance(_method_or_func, str):
            instance = await self.__app.build(_class)
            response = await self.__app.call(instance, _method_or_func)
        elif callable(_method_or_func):
            response = await self.__app.invoke(_method_or_func)

        if not isinstance(response, Response):
            error_msg = "Fallback handler must return a Response object"
            raise TypeError(error_msg)

        return response

    async def __dispatchRequest(
        self,
        interface: Interface,
        adapter: TransportAdapter,
        receive_or_protocol: object,
        send_fn: Callable[[Response], Awaitable[object | None]],
    ) -> object | None:
        """
        Execute the full HTTP request-response lifecycle.

        Shared implementation for RSGI and ASGI transports. Runs global
        middleware, resolves the route, builds the request, invokes the
        handler, and sends the response through ``send_fn``.

        Parameters
        ----------
        interface : Interface
            Transport protocol type (ASGI or RSGI).
        adapter : TransportAdapter
            Protocol-specific transport adapter for the current request.
        receive_or_protocol : object
            ASGI receive callable or RSGI ``HTTPProtocol`` instance used
            to construct the ``BodyStream``.
        send_fn : Callable[[Response], Awaitable[object | None]]
            Async callable ``(Response) -> object | None`` that sends the
            response back to the client via the correct protocol adapter.

        Returns
        -------
        object | None
            Result of sending the response, or ``None``.
        """
        async with self.__app.beginScope() as request_context:
            request_context.set("kernel", KernelContext.HTTP)
            self.__request_printer.startTimer()
            request = adapter
            try:
                response = await self.__globalMiddleware(adapter)
                if response and isinstance(response, Response):
                    return await send_fn(response)

                if adapter.method().upper() == "OPTIONS":
                    allowed_methods = self.__routes.options(adapter.path())
                    headers = {
                        "Allow": ", ".join(allowed_methods)
                    }
                    if "QUERY" in allowed_methods:
                        headers["Accept-Query"] = (
                            "application/json, application/x-www-form-urlencoded"
                        )
                    return await send_fn(
                        Response(
                            status_code=200,
                            headers=headers,
                        ),
                    )

                resolved_route = self.__routes.resolve(
                    method=adapter.method(),
                    path=adapter.path(),
                )
                body_stream = BodyStream(
                    interface=interface,
                    receive_or_protocol=receive_or_protocol,
                    max_body_size=self.__max_content_length,
                )
                request = Request(
                    interface=interface,
                    adapter=adapter,
                    body_stream=body_stream,
                    params=resolved_route.params,
                )
                request_context[Request] = request
                response = await self.__requestLayer(
                    request=request,
                    resolved_route=resolved_route,
                )

            except ValidationException as ve:
                response = self.__default_responses.error(
                    status_code=422,
                    content=ve.error(),
                    expects_json=request.wantsJson(),
                )

            except Exception as e:  # noqa: BLE001
                if isinstance(e, RouteNotFound):
                    fallback = self.__routes.fallback()
                    if fallback is not None and fallback != (None, None):
                        return await self.__callFallback(fallback)
                response = await self.__catch.exception(e, request)

            return await send_fn(response)

    async def handleRSGI(
        self,
        scope: Scope,
        protocol: HTTPProtocol,
    ) -> object | None:
        """
        Handle an incoming RSGI HTTP request end-to-end.

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
        adapter = RSGITransportAdapter(scope)
        return await self.__dispatchRequest(
            interface=Interface.RSGI,
            adapter=adapter,
            receive_or_protocol=protocol,
            send_fn=lambda resp: self.__rsgiResponse(adapter, resp, protocol),
        )

    async def handleASGI(
        self,
        scope: dict,
        receive: object,
        send: object,
    ) -> None:
        """
        Handle an incoming ASGI HTTP request end-to-end.

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
        adapter = ASGITransportAdapter(scope)
        return await self.__dispatchRequest(
            interface=Interface.ASGI,
            adapter=adapter,
            receive_or_protocol=receive,
            send_fn=lambda resp: self.__asgiResponse(adapter, resp, receive, send),
        )
