from granian.rsgi import Scope

class RSGIHandler:

    async def __call__(self, scope: Scope, proto):
        assert scope.proto == "http"
        proto.response_str(
            status=200,
            headers=[
                ("content-type", "text/plain"),
            ],
            body="Hello, world!",
        )

RSGIGateway = RSGIHandler()
