from orionis.http.bases.controller import BaseController
from orionis.http.response import HTMLResponse

class HomeController(BaseController):

    def index(self):

        return HTMLResponse(
            content="<h1>Welcome to Orionis Framework!</h1><p>This is the home page.</p>",
            status_code=200
        )