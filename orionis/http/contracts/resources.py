from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from orionis.http.enums.status import HTTPStatus

if TYPE_CHECKING:
    from orionis.http.response import FileResponse, HTMLResponse, JSONResponse, Response

class IDefaultResources(ABC):

    @abstractmethod
    def favicon(self) -> FileResponse | Response:
        """
        Return the favicon file response or a 404 response if not found.

        Searches for a favicon in the public storage directory using common
        favicon file names and content types. If not found, attempts to use
        the framework's internal fallback favicon. Caches the result for
        subsequent calls.

        Returns
        -------
        FileResponse or Response
            A FileResponse containing the favicon if found, otherwise a
            Response with status 404.
        """

    @abstractmethod
    def robotsTxt(self) -> FileResponse | Response:
        """
        Return the robots.txt file or a 404 response if not found.

        Search for a robots.txt file in the public storage directory. If not
        found, check for a fallback file. Cache the result for future calls.

        Returns
        -------
        FileResponse or Response
            FileResponse with robots.txt if found, otherwise Response with 404.
        """

    @abstractmethod
    def sitemapXml(self) -> FileResponse | Response:
        """
        Return the sitemap.xml file or a 404 response if found, else 404.

        Search for a sitemap.xml file in the public storage directory. If not found,
        check for a fallback file. Cache the result for future calls.

        Returns
        -------
        FileResponse or Response
            FileResponse with sitemap.xml if found, otherwise Response with status 404.
        """

    @abstractmethod
    def health(self, expects_json: bool) -> HTMLResponse | JSONResponse:
        """
        Render the application health state as an HTML or JSON response.

        Parameters
        ----------
        expects_json : bool
            Whether to return a JSON response (True) or HTML (False).

        Returns
        -------
        HTMLResponse or JSONResponse
            HTMLResponse with the state page content or JSONResponse with the
            application status. Status is 200 if healthy, 503 if under
            maintenance.
        """

    @abstractmethod
    def errorPage(
        self,
        status_code: int,
        description: str,
        expects_json: bool,
        headers: dict[str, str] | None = None,
    ) -> HTMLResponse | JSONResponse:
        """
        Render an error page for the specified status code and description.

        Parameters
        ----------
        status_code : int
            HTTP status code to display on the error page.
        description : str
            Description of the error to display.
        expects_json : bool
            If True, returns a JSON response; otherwise, returns HTML.
        headers : dict[str, str] | None, optional
            Additional headers to include in the response.

        Returns
        -------
        HTMLResponse or JSONResponse
            HTMLResponse with rendered error page, or JSONResponse if expects_json.
        """

    @abstractmethod
    def exceptionPage(
        self,
        request_path: str,
        request_method: str,
        exception: BaseException,
        status_code: int | HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
    ) -> HTMLResponse:
        """
        Render an exception page with request and traceback details.

        Parameters
        ----------
        request_path : str
            Path of the request that caused the exception.
        request_method : str
            HTTP method of the request that caused the exception.
        exception : BaseException
            Exception instance to be rendered.
        status_code : int | HTTPStatus, optional
            HTTP status code for the response. Defaults to 500.

        Returns
        -------
        HTMLResponse
            Rendered exception page as an HTMLResponse with the given status code.
        """

    @abstractmethod
    def emptyResponse(self, headers: dict[str, str] | None = None) -> Response:
        """
        Return an empty response with status 204 No Content.

        Parameters
        ----------
        headers : dict[str, str] | None, optional
            Additional headers to include in the response.

        Returns
        -------
        Response
            A Response object with status 204 and provided headers.
        """
