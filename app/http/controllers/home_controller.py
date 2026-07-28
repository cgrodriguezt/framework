from orionis.http import HTMLResponse
from orionis.http.base import BaseController
from orionis.support.facades.view import View
from orionis.support.facades.session import Session

class HomeController(BaseController):

    async def index(self) -> HTMLResponse:
        """
        Return the welcome page response.

        Returns
        -------
        HTMLResponse
            Rendered response for the welcome page.
        """
        Session.put("foo", "bar")
        return await View.make("welcome")
