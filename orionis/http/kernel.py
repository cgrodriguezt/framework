from granian.rsgi import Scope
from orionis.foundation.contracts.application import IApplication
from orionis.http.adapters.asgi import ASGIResponseAdapter
from orionis.http.adapters.rsgi import RSGIResponseAdapter
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.default.resources import DefaultResources
from orionis.http.request import Request
from orionis.http.response import HTMLResponse
from orionis.http.routes.engine import RoutingEngine

class KernelHTTP(IKernelHTTP):

    def __init__(
        self,
        app: IApplication,
        defaults: DefaultResources,
        route_engine: RoutingEngine,
    ) -> None:
        self.__app: IApplication = app
        self.__route_engine = route_engine
        self.__route_engine.discover()
        self.__rsgi_adapter = RSGIResponseAdapter()
        self.__defaults = defaults

    async def handleRSGI(
        self,
        scope: Scope,
        protocol: object,
    ) -> object:
        try:
            request = Request("rsgi", scope, protocol)
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
                status_code=500,
            )
        await self.__rsgi_adapter.send(handle, protocol, scope)

    async def handleASGI(
        self,
        scope: object,
        receive: object,
        send: object,
    ) -> object:
        # request = Request("asgi", scope, receive)
        # form_data = await request.form()
        # print(form_data.fields)
        # print(form_data.files)
        response = HTMLResponse("Hello, World!", status_code=200)
        adapter = ASGIResponseAdapter()
        await adapter.send(response, scope, receive, send)
