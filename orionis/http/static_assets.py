from pathlib import Path
from orionis.foundation.contracts.application import IApplication
from orionis.services.file.contracts.directory import IDirectory
from orionis.support.strings.stringable import Stringable

class StaticAssets:

    def __init__(
        self,
        app: IApplication,
        directory: IDirectory
    ) -> None:
        self.__app: IApplication = app
        self.__directory: IDirectory = directory
        self.__memory_cache: dict = {}
        self.__interface = Stringable(app.config("app.interface")).upper()

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

    def faviconBytes(self) -> tuple[bytes | None, str | None]:
        """
        Retrieve the favicon file contents as bytes if available.

        Parameters
        ----------
        self : StaticAssets
            Instance of the StaticAssets class.

        Returns
        -------
        tuple of bytes or None, and str or None
            Tuple containing the favicon file contents as bytes and the content
            type if found, otherwise (None, None).
        """
        # Get the public storage directory
        public_storage: Path = self.__directory.storagePublic()

        favicon_map: dict[str, str] = {
            "favicon.png": "image/png",
            "favicon.svg": "image/svg+xml",
            "favicon.ico": "image/x-icon",
        }

        # Search for favicon in the public storage directory
        for file_name, content_type in favicon_map.items():
            favicon_path: Path = public_storage / file_name
            if favicon_path.exists():
                with open(favicon_path, "rb") as f:
                    return f.read(), content_type

        # Fallback to default favicon if not found in public storage
        favicon_path: Path = (
            Path(__file__).parent.parent / "metadata" / "favicon_light.svg"
        )
        if favicon_path.exists():
            with open(favicon_path, "rb") as f:
                return f.read(), "image/svg+xml"

        return None, None

    def favicon(self) -> tuple:
        """
        Retrieve favicon contents and headers if available.

        Parameters
        ----------
        self : StaticAssets
            Instance of the StaticAssets class.

        Returns
        -------
        tuple of bytes or None, and list of tuple of bytes or None
            Tuple containing the favicon file contents and headers if found,
            otherwise (None, None).
        """
        # Return cached favicon if present
        if "favicon" in self:
            return self["favicon"]

        # Obtener los bytes y el tipo de contenido del favicon
        favicon_bytes, content_type = self.faviconBytes()





        # Get the public storage directory
        public_storage = self.__directory.storagePublic()

        # Prepare variables for favicon content and headers
        bytes_content: bytes | None = None
        headers: list[tuple[bytes, bytes]] = []
        headers.extend(self.__default_headers)
        headers.append(("cache-control", "public, max-age=31536000"))

        favicon_map = {
            "favicon.png": "image/png",
            "favicon.svg": "image/svg+xml",
            "favicon.ico": "image/x-icon",
        }

        for file_name, content_type in favicon_map.items():
            favicon_path = public_storage / file_name
            if favicon_path.exists():
                with open(favicon_path, "rb") as f:
                    bytes_content = f.read()
                    headers.append(("content-type", content_type))
                    break

        if bytes_content is None:
            favicon_path = Path(__file__).parent.parent / "metadata" / "favicon_light.svg"
            if favicon_path.exists():
                with open(favicon_path, "rb") as f:
                    bytes_content = f.read()
                    headers.append(("content-type", "image/svg+xml"))

        if bytes_content is not None:
            self["favicon"] = bytes_content, headers
            return bytes_content, headers

        self.__default_headers: list[tuple[bytes, bytes]] = [
            ("server", f"Orionis {self.__interface}"),
        ]


    def wellKnown(self) -> tuple:
        """
        Return the well-known response headers and body.

        Parameters
        ----------
        self : StaticAssets
            Instance of the StaticAssets class.

        Returns
        -------
        tuple of bytes and list of tuple of bytes
            Tuple containing the response body as bytes and a list of HTTP
            headers.
        """
        # Return cached well-known response if present
        if "well_known" in self:
            return self["well_known"]

        # Prepare headers for the well-known response
        headers = [
            ("content-type", "application/json"),
            ("cache-control", "public, max-age=86400"),
        ]
        headers.extend(self.__default_headers)

        # Prepare empty response body
        response = {}

        # Cache the response and headers
        self["well_known"] = response, headers
        return response, headers

    def healthPage(self) -> tuple:
        """
        Return the HTTP response for the health page.

        Parameters
        ----------
        self : StaticAssets
            Instance of StaticAssets.

        Returns
        -------
        tuple of bytes and list of tuple of str
            Tuple containing the response body as bytes and a list of HTTP
            headers.
        """
        # Determine the file name based on maintenance mode
        file_name = "up.html"

        # Return cached health page if present
        if "health_page" in self:
            return self["health_page"]

        # Load the HTML content for the health page from the filesystem
        page_path: Path = Path(__file__).parent / "default" / "pages" / file_name
        with page_path.open("rb") as f:
            body: bytes = f.read()

        headers: list[tuple[str, str]] = [
            ("content-type", "text/html; charset=utf-8"),
            ("cache-control", "no-cache"),
        ]
        headers.extend(self.__default_headers)

        # Cache the health page response
        self["health_page"] = body, headers
        return body, headers

    def robotsTxt(self) -> tuple:
        """
        Return the HTTP response for the robots.txt file.

        Parameters
        ----------
        self : StaticAssets
            Instance of StaticAssets.

        Returns
        -------
        tuple of bytes and list of tuple of str
            Tuple containing the robots.txt file content as bytes and a list of
            HTTP headers.
        """
        # Return cached robots.txt if present
        if "robots_txt" in self:
            return self["robots_txt"]

        # Try to load custom robots.txt from the public storage directory
        public_storage: Path = self.__directory.storagePublic()
        robots_path: Path = public_storage / "robots.txt"
        if robots_path.exists():
            with robots_path.open("rb") as f:
                body: bytes = f.read()
        else:
            # Load default robots.txt from the filesystem if custom not found
            default_robots_path: Path = (
                Path(__file__).parent / "default" / "assets" / "robots.txt"
            )
            with default_robots_path.open("rb") as f:
                body: bytes = f.read()

        headers: list[tuple[str, str]] = [
            ("content-type", "text/plain; charset=utf-8"),
            ("cache-control", "public, max-age=86400"),
        ]
        headers.extend(self.__default_headers)
        # Cache the robots.txt response for future requests
        self["robots_txt"] = body, headers
        return body, headers