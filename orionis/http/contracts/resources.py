from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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
    def healthCheck(self) -> JSONResponse:
        """
        Return application health status as a JSON response.

        Parameters
        ----------
        None

        Returns
        -------
        JSONResponse
            JSON response indicating health status ("ok" or "maintenance").
        """

    @abstractmethod
    def statePage(self, milliseconds: int = 0) -> HTMLResponse:
        """
        Render the application state page as an HTML response.

        Parameters
        ----------
        milliseconds : int, optional
            Time in milliseconds to display on the page.

        Returns
        -------
        HTMLResponse
            HTML response with the state page content. Status is 200 if healthy,
            503 if under maintenance.
        """

    @abstractmethod
    def errorPage(self, status_code: int, description: str) -> HTMLResponse:
        """
        Render an error page for a given status code and description.

        Parameters
        ----------
        status_code : int
            HTTP status code to display on the error page.
        description : str
            Description of the error to display.

        Returns
        -------
        HTMLResponse
            HTML response containing the rendered error page.
        """

    @abstractmethod
    def exceptionPage(
        self,
        request_path: str,
        request_method: str,
        traceback: dict,
    ) -> HTMLResponse:
        """
        Render an exception page with request and traceback details.

        Parameters
        ----------
        request_path : str
            The path of the request that caused the exception.
        request_method : str
            The HTTP method of the request that caused the exception.
        traceback : dict
            Dictionary containing error type and stack trace information.

        Returns
        -------
        HTMLResponse
            An HTMLResponse containing the rendered exception page with status 500.
        """
