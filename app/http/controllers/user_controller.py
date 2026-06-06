from app.http.controllers.base_controller import BaseController
from app.http.schemas.store_user_schema import StoreUserSchema
from orionis.http.request import Request
from orionis.http.response import JSONResponse

class UserController(BaseController):

    # ruff: noqa: D102

    async def index(self) -> JSONResponse:
        return JSONResponse(
            content={},
            status_code=200,
        )

    async def store(self, request: Request, data: StoreUserSchema) -> JSONResponse:
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
