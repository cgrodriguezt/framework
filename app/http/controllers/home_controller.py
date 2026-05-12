from orionis.http.bases.controller import BaseController
from orionis.http.request import Request
from rich.console import Console
from orionis.http.response import HTMLResponse

class HomeController(BaseController):

    def index(self, request: Request, console : Console) -> HTMLResponse:

        console.print(request.param())

        return HTMLResponse(
            content="<h1>Welcome to Orionis Framework!</h1><p>Hello, Raulin!</p>",
            status_code=200,
        )
