import json
import platform
from pathlib import Path
from typing import TYPE_CHECKING
from orionis.foundation.contracts.application import IApplication
from orionis.http.default.contracts.responses import IDefaultResponses
from orionis.http.enums.status import HTTPStatus
from orionis.http.request import Request
from orionis.http.response import FileResponse, HTMLResponse, JSONResponse, Response
from orionis.metadata.framework import VERSION
from orionis.services.file.directory import Directory
from orionis.support.formatter.exceptions.parser import ExceptionParser

if TYPE_CHECKING:
    from orionis.services.file.contracts.directory import IDirectory

class DefaultResponses(IDefaultResponses):

    # ruff: noqa: TC001

    _FAVICON_CACHE_CONTROL_AGE: str = "public, max-age=31536000, immutable"
    _ROBOTS_TXT_CACHE_CONTROL_AGE: str = "public, max-age=3600"
    _SITEMAP_XML_CACHE_CONTROL_AGE: str = "public, max-age=600"
    _GENERAL_CACHE_CONTROL: str = "no-cache, no-store, must-revalidate"

    def __init__(
        self,
        app: IApplication,
        directory: Directory,
    ) -> None:
        """
        Initialize instance with application and directory dependencies.

        Parameters
        ----------
        app : IApplication
            The application instance providing configuration and services.
        directory : IDirectory
            The directory service for accessing storage paths.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        # Store application and directory dependencies
        self.__app: IApplication = app
        self.__directory: IDirectory = directory

        # Cache frequently accessed configuration values
        self.__app_name = self.__app.config("app.name")
        self.__app_locale = self.__app.config("app.locale")

        # Initialize memory cache for storing static asset responses
        self.__memory_cache: dict = {}

    def __getitem__(self, key: str) -> object | None:
        """
        Retrieve a cached value by key.

        Parameters
        ----------
        key : str
            The key to look up in the cache.

        Returns
        -------
        object or None
            The cached value if found, otherwise None.
        """
        # Return the value from the memory cache for the given key
        return self.__memory_cache.get(key, None)

    def __setitem__(self, key: str, value: object) -> None:
        """
        Store a value in the cache with the specified key.

        Parameters
        ----------
        key : str
            The key under which to store the value.
        value : object
            The value to store in the cache.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set the value in the memory cache for the given key
        self.__memory_cache[key] = value

    def __contains__(self, key: str) -> bool:
        """
        Check if the cache contains the specified key.

        Parameters
        ----------
        key : str
            The key to check for existence in the cache.

        Returns
        -------
        bool
            True if the key exists in the cache, False otherwise.
        """
        # Return True if the key is present in the memory cache
        return key in self.__memory_cache

    def __delitem__(self, key: str) -> None:
        """
        Remove an item from the memory cache by key.

        Parameters
        ----------
        key : str
            The key to remove from the cache.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Remove the key from the cache if present
        self.__memory_cache.pop(key, None)

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
        # Check if favicon is already cached
        if "favicon" in self:
            return self["favicon"]

        # Get the public storage directory path
        public_storage: Path = self.__directory.storagePublic()

        # Map of possible favicon file names to their content types
        favicon_map: dict[str, str] = {
            "favicon.ico": "image/x-icon",
            "favicon.png": "image/png",
            "favicon.svg": "image/svg+xml",
        }

        # Search for favicon in public storage
        for file_name, content_type in favicon_map.items():
            favicon_path: Path = public_storage / file_name

            if favicon_path.exists():
                self["favicon"] = FileResponse(
                    path=favicon_path,
                    headers={
                        "content-type": content_type,
                        "cache-control": self._FAVICON_CACHE_CONTROL_AGE,
                    },
                )
                return self["favicon"]

        # Use internal framework fallback favicon if not found in public storage
        fallback_path: Path = (
            Path(__file__).parent / "assets" / "favicon.ico"
        )

        # Check if the fallback favicon exists and return it if found
        if fallback_path.exists():
            self["favicon"] = FileResponse(
                path=fallback_path,
                headers={
                    "content-type": "image/x-icon",
                    "cache-control": self._FAVICON_CACHE_CONTROL_AGE,
                },
            )
            return self["favicon"]

        # Return 404 response if no favicon is found
        return self.error(
            status_code=HTTPStatus.NOT_FOUND,
            content="Favicon Not Found",
            expects_json=False,
            headers={
                "cache-control": self._GENERAL_CACHE_CONTROL,
            },
        )

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
        # Return cached robots.txt if available
        if "robots_txt" in self:
            return self["robots_txt"]

        # Get the public storage directory path
        public_storage: Path = self.__directory.storagePublic()

        # Check for robots.txt in public storage
        robots_path: Path = public_storage / "robots.txt"

        if robots_path.exists():
            self["robots_txt"] = FileResponse(
                path=robots_path,
                headers={
                    "content-type": "text/plain",
                    "cache-control": self._ROBOTS_TXT_CACHE_CONTROL_AGE,
                },
            )
            return self["robots_txt"]

        # Check for fallback robots.txt in internal assets
        fallback_path: Path = (
            Path(__file__).parent / "assets" / "robots.txt"
        )

        if fallback_path.exists():
            self["robots_txt"] = FileResponse(
                path=fallback_path,
                headers={
                    "content-type": "text/plain",
                    "cache-control": self._ROBOTS_TXT_CACHE_CONTROL_AGE,
                },
            )
            return self["robots_txt"]

        # Return 404 response if robots.txt is not found
        return self.error(
            status_code=HTTPStatus.NOT_FOUND,
            content="Robots.txt Not Found",
            expects_json=False,
            headers={
                "cache-control": self._GENERAL_CACHE_CONTROL,
            },
        )

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
        # Return cached sitemap.xml if available
        if "sitemap_xml" in self:
            return self["sitemap_xml"]

        # Get the public storage directory path
        public_storage: Path = self.__directory.storagePublic()

        # Check for sitemap.xml in public storage
        sitemap_path: Path = public_storage / "sitemap.xml"

        if sitemap_path.exists():
            self["sitemap_xml"] = FileResponse(
                path=sitemap_path,
                headers={
                    "content-type": "application/xml",
                    "cache-control": self._SITEMAP_XML_CACHE_CONTROL_AGE,
                },
            )
            return self["sitemap_xml"]

        # Return 404 response if sitemap.xml is not found
        return self.errorPage(
            status_code=HTTPStatus.NOT_FOUND,
            description="Sitemap Not Found",
            expects_json=False,
            headers={
                "cache-control": self._GENERAL_CACHE_CONTROL,
            },
        )

    def health(self, request: Request) -> HTMLResponse | JSONResponse:
        """
        Render the application health state as an HTML or JSON response.

        Parameters
        ----------
        request : Request
            The HTTP request object.

        Returns
        -------
        HTMLResponse or JSONResponse
            HTMLResponse with the state page content or JSONResponse with the
            application status. Status is 200 if healthy, 503 if under
            maintenance.
        """
        # Retrieve maintenance mode settings from environment and config
        config_maintenance: bool = self.__app.config("app.maintenance")

        # Determine application state based on maintenance configuration
        app_state: int = (
            HTTPStatus.SERVICE_UNAVAILABLE
            if config_maintenance else HTTPStatus.OK
        )

        # Return JSON response if requested
        if request.wantsJson():
            # Check if cached JSON response exists
            if f"http_{app_state}:json" not in self:
                status: str = (
                    "Application in Maintenance"
                    if app_state == HTTPStatus.SERVICE_UNAVAILABLE
                    else "Online Application"
                )
                # Cache the JSON response for future calls
                self[f"http_{app_state}:json"] = JSONResponse(
                    content={"message": status},
                    status_code=app_state,
                    headers={"cache-control": self._GENERAL_CACHE_CONTROL},
                )
            return self[f"http_{app_state}:json"]

        # Cache the state page content for each state
        if f"state_page_{app_state}:html" not in self:

            # Select template page based on application state
            template_page: str = (
                "down" if app_state == HTTPStatus.SERVICE_UNAVAILABLE else "up"
            )
            state_page_path: Path = (
                Path(__file__).parent / "pages" / f"{template_page}.html"
            )
            with state_page_path.open() as f:
                content: str = f.read()
            html: str = (
                content.replace("{{app_name}}", self.__app_name) # NOSONAR
                       .replace("{{locale}}", self.__app_locale) # NOSONAR
            )
            self[f"state_page_{app_state}:html"] = HTMLResponse(
                content=html,
                status_code=app_state,
                headers={"cache-control": self._GENERAL_CACHE_CONTROL},
            )

        # Return the cached HTML response for the current application state
        return self[f"state_page_{app_state}:html"]

    def error(
        self,
        status_code: int | HTTPStatus,
        content: str | dict,
        *,
        expects_json: bool,
        headers: dict[str, str] | None = None,
    ) -> HTMLResponse | JSONResponse:
        """
        Return an error page or JSON response for the specified status code.

        Parameters
        ----------
        status_code : int | HTTPStatus
            HTTP status code to display on the error page.
        content : str | dict
            Content of the error to display.
        expects_json : bool
            If True, returns a JSON response; otherwise, returns HTML.
        headers : dict[str, str] | None, optional
            Additional headers to include in the response.

        Returns
        -------
        HTMLResponse or JSONResponse
            HTMLResponse with rendered error page, or JSONResponse if
            expects_json is True.
        """
        # Convert HTTPStatus to integer if necessary
        if isinstance(status_code, HTTPStatus):
            status_code = status_code.value

        # Ensure cache-control header is always present
        if headers is not None and "cache-control" not in headers:
            headers.update({"cache-control": self._GENERAL_CACHE_CONTROL})
        else:
            headers = {"cache-control": self._GENERAL_CACHE_CONTROL}

        # Return JSON response if requested by client
        if expects_json:

            data = {}
            if isinstance(content, dict):
                data.update(content)
            else:
                data["message"] = content

            return JSONResponse(
                content=data,
                status_code=status_code,
                headers=headers,
            )

        # Cache the error page template for performance
        if "error_page_template" not in self:
            error_page_path = Path(__file__).parent / "pages" / "error.html"
            with error_page_path.open() as f:
                self["error_page_template"] = f.read()

        # Render the error page with provided status code and description
        template: str = self["error_page_template"]
        message: str = HTTPStatus(status_code).name.replace("_", " ").title()

        # Determine the description to display based on content type
        if isinstance(content, dict):
            description = content.get("message", json.dumps(content))
        elif isinstance(content, str):
            description = content

        html: str = (
            template.replace("{{0}}", str(status_code)[0])
                    .replace("{{1}}", str(status_code)[1])
                    .replace("{{2}}", str(status_code)[2])
                    .replace("{{error}}", str(status_code))
                    .replace("{{message}}", message)
                    .replace("{{description}}", description)
                    .replace("{{app_name}}", self.__app_name)
                    .replace("{{locale}}", self.__app_locale)
        )

        # Return the rendered error page as an HTMLResponse
        # with the specified status code and headers
        return HTMLResponse(
            content=html,
            status_code=status_code,
            headers=headers,
        )

    def exception(
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
        # Cache the exception page template if not already cached
        if "exception_page_template" not in self:
            exception_page_path: Path = (
                Path(__file__).parent / "pages" / "exception.html"
            )
            with exception_page_path.open() as f:
                template = f.read()
            debug_status: str = (
                "Enabled" if self.__app.config("app.debug") else "Disabled"
            )
            # Fill in static framework and environment details
            template = (
                template.replace("{{framework_version}}", f"v{VERSION}")
                .replace("{{python_version}}", platform.python_version())
                .replace("{{environment}}", self.__app.config("app.env"))
                .replace("{{debug_mode}}", debug_status)
                .replace("{{timezone}}", self.__app.config("app.timezone"))
                .replace("{{interface}}", self.__app.config("app.interface").upper())
                .replace("{{locale}}", self.__app_locale)
                .replace("{{app_name}}", self.__app_name)
            )
            self["exception_page_template"] = template

        # Parse the exception to extract error type and stack trace information
        traceback = ExceptionParser(exception).toDict()

        # Render the exception page with request and error details
        template: str = self["exception_page_template"]
        html: str = (
            template.replace("{{path}}", request_path)
                    .replace("{{request_method}}", request_method)
                    .replace("{{error_context}}", traceback["error_type"])
                    .replace('"{{traceback}}"', json.dumps(traceback))
                    .replace("{{exception}}", traceback["error_type"])
        )

        # Return the rendered exception page with the specified status code
        return HTMLResponse(
            content=html,
            status_code=status_code,
            headers={"cache-control": self._GENERAL_CACHE_CONTROL},
        )
