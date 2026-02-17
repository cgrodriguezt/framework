import json
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

    async def handleRSGI(
        self,
        scope: Scope,
        protocol: object,
    ) -> object:
        request = Request("rsgi", scope, protocol)
        xml = await request.xml()
        print(xml.tag)
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
        print(await request.xml())
        response = HTMLResponse("Hello, World!", status_code=200)
        adapter = ASGIResponseAdapter()
        await adapter.send(response, scope, receive, send)