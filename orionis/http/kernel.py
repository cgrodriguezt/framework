from granian.rsgi import Scope
from orionis.http.adapters.asgi import ASGIResponseAdapter
from orionis.http.adapters.rsgi import RSGIResponseAdapter
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.default.resources import DefaultResources
from orionis.http.enums.interfaces import Interface
from orionis.http.request import Request
from orionis.http.routes.engine import RoutingEngine

class KernelHTTP(IKernelHTTP):

    def __init__(
        self,
        defaults: DefaultResources,
        asgi_adapter: ASGIResponseAdapter,
        route_engine: RoutingEngine,
        rsgi_adapter: RSGIResponseAdapter,
    ) -> None:
        self.__route_engine = route_engine
        self.__route_engine.discover()
        self.__rsgi_adapter = rsgi_adapter
        self.__asgi_adapter = asgi_adapter
        self.__defaults = defaults

    async def handleRSGI(
        self,
        scope: Scope,
        protocol: object,
    ) -> object:
        try:
            request = Request(Interface.RSGI.value, scope, protocol)
            ready, handle, params = self.__route_engine.resolve(
                path=request.path,
                method=request.method,
                expects_json=request.expectsJson(),
            )
        except Exception as e:
            handle = self.__defaults.exceptionPage(
                exception=e,
                request_method=scope.method,
                request_path=scope.path,
            )
        await self.__rsgi_adapter.send(handle, protocol, scope)

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