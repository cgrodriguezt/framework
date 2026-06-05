from app.http.controllers.base_controller import BaseController
from orionis.http.request import Request
from orionis.http.response import JSONResponse

class HomeController(BaseController):

    async def index(self, slug: str, identifier: int, request: Request) -> JSONResponse:
        """
        Handle the home page request.

        Args:
            slug: The slug parameter from the URL.
            identifier: The identifier parameter from the URL.
            request: The HTTP request object.

        Returns
        -------
        JSONResponse
            A JSON response with the request data.
        """
        return JSONResponse(
            content={
                "slug": slug,
                "identifier": identifier,
                "interface": request.interface,
                "unique_id": request.state.unique_id,
            },
            status_code=200,
        )

    async def store(self, request: Request) -> JSONResponse:
        """
        Handle the store request.

        Args:
            request: The HTTP request object.

        Returns
        -------
        JSONResponse
            A JSON response with the request data.
        """
        data = await request.data()

        return JSONResponse(
            content=data,
            status_code=200,
        )
