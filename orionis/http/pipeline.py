from orionis.http.bases.middleware import BaseMiddleware
from orionis.http.contracts.request import IRequest

class Pipeline:

    def __init__(
        self,
        app_middlewares: list[type[BaseMiddleware]]
    ):
        self.app_middlewares = app_middlewares

    async def handle(
        self,
        *,
        default:bool = False,
        request:IRequest,
        route:dict
    ) -> object:

        stack = []

        # 1️⃣ Global middlewares
        stack.extend(self.app_middlewares)

        # 2️⃣ Route middlewares
        stack.extend(route.middlewares)

        # 3️⃣ Controller como último elemento
        async def controller_executor(req):
            return await route.action(req)

        async def execute(index, req):
            if index >= len(stack):
                return await controller_executor(req)

            middleware = stack[index]

            async def call_next(r):
                return await execute(index + 1, r)

            return await middleware.handle(req, call_next)

        return await execute(0, request)