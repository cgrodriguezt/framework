from app.http.controllers.base_controller import BaseController
from app.http.schemas.store_user import StoreUserSchema
from orionis.http.request import Request
from orionis.http.response import JSONResponse
from orionis.services.file.storage import Storage

class UserController(BaseController):

    # ruff: noqa: D102

    async def index(self, slug: str, identifier: int, storage: Storage) -> JSONResponse:
        storage.put(
            nombre=f"{slug}_{identifier}.txt",
            contenido=f"Contenido del archivo para {slug} con id {identifier}",
        )
        return JSONResponse(
            content={
                "slug": slug,
                "identifier": identifier,
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
