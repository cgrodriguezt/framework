import json
import platform
from pathlib import Path
from orionis.foundation.contracts.application import IApplication
from orionis.http.contracts.resources import IDefaultResources
from orionis.http.response import FileResponse, HTMLResponse, JSONResponse, Response
from orionis.http.enums.status import HTTPStatus
from orionis.metadata.framework import VERSION
from orionis.services.file.contracts.directory import IDirectory

class DefaultResources(IDefaultResources):

    _FAVICON_CACHE_CONTROL_AGE: str = "public, max-age=31536000, immutable"
    _ROBOTS_TXT_CACHE_CONTROL_AGE: str = "public, max-age=3600"
    _SITEMAP_XML_CACHE_CONTROL_AGE: str = "public, max-age=600"
    _GENERAL_CACHE_CONTROL: str = "no-cache, no-store, must-revalidate"

    def __init__(
        self,
        app: IApplication,
        directory: IDirectory,
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
            "favicon.png": "image/png",
            "favicon.svg": "image/svg+xml",
            "favicon.ico": "image/x-icon",
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
            Path(__file__).parent / "default" / "assets" / "favicon.ico"
        )

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
        self["favicon"] = Response(status=404)
        return self["favicon"]

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
            Path(__file__).parent / "default" / "assets" / "robots.txt"
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
        self["robots_txt"] = Response(status=404)
        return self["robots_txt"]

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
        self["sitemap_xml"] = Response(status=404)
        return self["sitemap_xml"]

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
        # Determine application state based on maintenance config
        app_state = (
            HTTPStatus.SERVICE_UNAVAILABLE
            if self.__app.config("app.maintenance") else HTTPStatus.OK
        )

        # Return maintenance status if app is in maintenance mode
        if app_state == HTTPStatus.SERVICE_UNAVAILABLE:
            return JSONResponse(
                content={"status": "maintenance"},
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                headers={"cache-control": self._GENERAL_CACHE_CONTROL},
            )
        # Return healthy status otherwise
        return JSONResponse(
            content={"status": "ok"},
            status_code=HTTPStatus.OK,
            headers={"cache-control": self._GENERAL_CACHE_CONTROL},
        )

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
        # Determine application state based on maintenance config
        app_state = (
            HTTPStatus.SERVICE_UNAVAILABLE
            if self.__app.config("app.maintenance") else HTTPStatus.OK
        )

        # Cache the state page content for each state
        if f"state_page_{app_state}" not in self:
            name_page = "down" if app_state == HTTPStatus.SERVICE_UNAVAILABLE else "up"
            state_page_path: Path = (
                Path(__file__).parent / "default" / "pages" / f"{name_page}.html"
            )
            with state_page_path.open() as f:
                content: str = f.read()
            self[f"state_page_{app_state}"] = content

        content: str = self[f"state_page_{app_state}"]
        html: str = (
            content.replace("{{time}}", str(milliseconds))
                   .replace("{{app_name}}", self.__app_name)
                   .replace("{{locale}}", self.__app_locale) # NOSONAR
        )

        return HTMLResponse(
            content=html,
            status_code=app_state,
            headers={"cache-control": self._GENERAL_CACHE_CONTROL},
        )

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
        # Cache the error page template if not already cached
        if "error_page_template" not in self:
            error_page_path: Path = (
                Path(__file__).parent / "default" / "pages" / "error.html"
            )
            with error_page_path.open() as f:
                self["error_page_template"] = f.read()

        # Render the error page with provided status code and description
        template: str = self["error_page_template"]
        html: str = (
            template.replace("{{0}}", str(status_code)[0])
                    .replace("{{1}}", str(status_code)[1])
                    .replace("{{2}}", str(status_code)[2])
                    .replace("{{error}}", str(status_code))
                    .replace("{{description}}", description)
                    .replace("{{app_name}}", self.__app_name)
                    .replace("{{locale}}", self.__app_locale)
        )

        return HTMLResponse(
            content=html,
            status_code=status_code,
            headers={"cache-control": self._GENERAL_CACHE_CONTROL},
        )

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
        # Cache the exception page template if not already cached
        if "exception_page_template" not in self:
            exception_page_path: Path = (
                Path(__file__).parent / "default" / "pages" / "exception.html"
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
                        .replace("{{interface}}", self.__app.config("app.interface"))
                        .replace("{{locale}}", self.__app_locale)
            )
            self["exception_page_template"] = template

        # Render the exception page with request and error details
        template: str = self["exception_page_template"]
        html: str = (
            template.replace("{{request_path}}", request_path)
                    .replace("{{request_method}}", request_method)
                    .replace("{{error_context}}", traceback["error_type"])
                    .replace('"{{traceback}}"', json.dumps(traceback["stack_trace"]))
        )

        return HTMLResponse(
            content=html,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            headers={"cache-control": self._GENERAL_CACHE_CONTROL},
        )
