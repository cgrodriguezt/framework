from granian.rsgi import Scope
from orionis.foundation.contracts.application import IApplication
from orionis.http.adapters.asgi import ASGIResponseAdapter
from orionis.http.adapters.rsgi import RSGIResponseAdapter
from orionis.http.contracts.kernel import IKernelHTTP
from orionis.http.request import Request
from orionis.http.response import HTMLResponse

class KernelHTTP(IKernelHTTP):

    def __init__(
        self,
        app: IApplication,
    ) -> None:
        self.__app: IApplication = app

    def handleRequest(method: str, path: str):
        """
        Recibe method (GET, POST, etc.) y path (/usuarios/123)
        y devuelve el handler + parametros parseados
        """
        for route_path, methods in compiled_routes.items():
            if method not in methods:
                continue
            route_info = methods[method]

            match = route_info["regex"].match(path)
            if match:
                # Parseamos los parámetros usando los convertidores
                params = {
                    name: route_info["converters"][name](value)
                    for name, value in match.groupdict().items()
                }
                controller_class = route_info["controller"]
                handler_name = route_info["handler"]

                # Instanciamos el controller
                controller = controller_class()
                handler = getattr(controller, handler_name)

                # Llamamos al handler con los parámetros
                return handler(**params)

        # Si no coincide ninguna ruta
        raise Exception("404 Not Found")

    async def handleRSGI(
        self,
        scope: Scope,
        protocol: object,
    ) -> object:
        request = Request("rsgi", scope, protocol)
        form_data = await request.form()
        print(form_data.fields)
        print(form_data.files)
        response = HTMLResponse("Hello, World!", status_code=200)
        adapter = RSGIResponseAdapter()
        await adapter.send(response, protocol, scope)

    async def handleASGI(
        self,
        scope: object,
        receive: object,
        send: object,
    ) -> object:
        request = Request("asgi", scope, receive)
        form_data = await request.form()
        print(form_data.fields)
        print(form_data.files)
        response = HTMLResponse("Hello, World!", status_code=200)
        adapter = ASGIResponseAdapter()
        await adapter.send(response, scope, receive, send)
