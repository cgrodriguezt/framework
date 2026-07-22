from orionis.http.base import BaseController
from app.http.schemas.store_user import StoreUserSchema
from orionis.http import Request
from orionis.http import JSONResponse, HTMLResponse
from orionis.support.facades.view import View

class UserController(BaseController):

    # ruff: noqa: D102

    async def index(self, slug: str, identifier: int, request: Request) -> HTMLResponse:
        return await View.make(
            "welcome",
            title="Welcome",
            app_name="Orionis Framework",
            version="1.0.0",
            today="2026-07-22",
            markdown_text="""
            # Orionis

            This page was rendered using **Jinja2**.
            """,
            user={
                "name": "Raúl",
            },
            users=[
                {
                    "name": "Raúl",
                    "email": "raul@example.com",
                },
                {
                    "name": "John",
                    "email": "john@example.com",
                },
                {
                    "name": "Jane",
                    "email": "jane@example.com",
                },
            ],
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
