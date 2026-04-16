from granian.rsgi import Scope
from orionis.console.output.http_request import HTTPRequestPrinter
from orionis.foundation.contracts.application import IApplication
from orionis.http.adapters.asgi import ASGIResponseAdapter
from orionis.http.adapters.rsgi import RSGIResponseAdapter
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.default.resources import DefaultResources
from orionis.failure.enums.kernel_type import KernelContext
from orionis.http.enums.interfaces import Interface
from orionis.http.request import Request
from orionis.http.routes.engine import RoutingEngine

class KernelHTTP(IKernelHTTP):

    def __init__(
        self,
        app: IApplication,
        defaults: DefaultResources,
        asgi_adapter: ASGIResponseAdapter,
        route_engine: RoutingEngine,
        rsgi_adapter: RSGIResponseAdapter,
        http_request_printer: HTTPRequestPrinter,
    ) -> None:

        # Guardar instancia de la app para generar un scope en cada request
        self.__app = app

        # Descubrir rutas y guardarlas en memoria para resolverlas en cada request
        self.__route_engine = route_engine
        self.__route_engine.discover()

        # Guardar adaptadores para enviar respuestas en cada protocolo
        self.__rsgi_adapter = rsgi_adapter
        self.__asgi_adapter = asgi_adapter

        # Guardar recursos por defecto para manejar excepciones y otras situaciones comunes
        self.__defaults = defaults

        # Guardar instancia del impresor de requests para mostrar información de cada request en consola solo si la app está en modo debug
        self.__http_request_printer = http_request_printer
        self.__http_request_printer.setEnabled(enabled=app.isDebug())

    async def handleRSGI(
        self,
        scope: Scope,
        protocol: object,
    ) -> object:

        import asyncio
        for i in range(60):
            print(f"⏱️  [{i+1}/60] handling RSGI request...")
            await asyncio.sleep(1)

        # async with self.__app.beginScope() as request_context:

        #     # Agregar información del kernel al scope de la app para que esté disponible en cualquier parte de la aplicación durante el manejo de la request
        #     request_context.set("kernel", KernelContext.HTTP)

        #     # Iniciar el marcador de tiempo para calcular la duración de la request y mostrarla en consola junto con el método, ruta y código de respuesta
        start_time = self.__http_request_printer.startTimer()

        #     request = Request(Interface.RSGI.value, scope, protocol)

        #     self.__app.instance()


        try:
            request = Request(Interface.RSGI.value, scope, protocol)
            ready, handle, params = self.__route_engine.resolve(
                path=request.path,
                method=request.method,
                expects_json=request.expectsJson(),
            )

            self.__http_request_printer.printRequest(
                method=request.method,
                path=request.path,
                start_time=start_time,
                code=handle.getStatusCode(),
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
        import asyncio
        for i in range(60):
            print(f"⏱️  [{i+1}/60] handling ASGI request...")
            await asyncio.sleep(1)

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