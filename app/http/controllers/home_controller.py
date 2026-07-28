from orionis.http import HTMLResponse
from orionis.http.base import BaseController
from orionis.support.facades import View

class HomeController(BaseController):

    async def index(self) -> HTMLResponse:
        """
        Return the welcome page response.

        Returns
        -------
        HTMLResponse
            Rendered response for the welcome page.
        """
        return await View.make("welcome")
