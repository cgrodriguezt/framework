from orionis.http.base import BaseController
from app.http.schemas.store_user import StoreUserSchema
from orionis.http import Request
from orionis.http import JSONResponse
from orionis.support.facades.session import Session

class UserController(BaseController):

    # ruff: noqa: D102

    async def index(self, slug: str, identifier: int, request: Request) -> JSONResponse:
        Session.put("user", {
            "name": "wilmer",
            "email": "wilmer@example.com",
        })
        return JSONResponse(
            content={
                "slug": slug,
                "identifier": identifier,
                "user": Session.get("user"),
            },
            status_code=200,
        )

    async def store(self, request: Request, data: StoreUserSchema) -> JSONResponse:
        """
        Handle the store request.

        Args:
            request: The HTTP request object.
            data: The validated request data.

        Returns
        -------
        JSONResponse
            A JSON response with the request data.
        """
        return JSONResponse(
            content=data,
            status_code=200,
        )

    async def query(self, request: Request) -> JSONResponse:
        """
        Handle the query request.

        Args:
            request: The HTTP request object.

        Returns
        -------
        JSONResponse
            A JSON response with the query parameters.
        """
        return JSONResponse(
            content=await request.data(),
            status_code=200,
        )
