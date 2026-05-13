from typing import Any, TYPE_CHECKING
from orionis.http.adapters.request.contracts.transport import TransportAdapter
from orionis.http.payload.estructures.headers import Headers

if TYPE_CHECKING:
    from collections.abc import Iterable

class ASGITransportAdapter(TransportAdapter):

    # ruff: noqa: ANN401

    def __init__(self, scope: dict) -> None:
        """Initialize the adapter with an ASGI scope dict.

        Parameters
        ----------
        scope : dict
            The ASGI scope dictionary.

        Returns
        -------
        None
            No value is returned.
        """
        # Memory cache for storing computed values like headers, client IP, etc.
        self.__memory_cache: dict[str, object] = {}
        # Mutable overrides — never touches the original scope object
        self.__overrides: dict[str, Any] = {}
        # Store the ASGI scope and initialize the memory cache
        self.__scope: dict = scope
        # Cache header list to avoid repeated dict lookups per request
        self.__headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
        # Pre-build headers for efficient access
        self.__buildHeadersASGI()

    def __getitem__(self, key: str) -> object | None:
        """Retrieve a cached value by key.

        Parameters
        ----------
        key : str
            The key to look up in the cache.

        Returns
        -------
        object | None
            The cached value if found, otherwise None.
        """
        return self.__memory_cache.get(key, None)

    def __setitem__(self, key: str, value: object) -> None:
        """Store a value in the cache with the specified key.

        Parameters
        ----------
        key : str
            The key under which to store the value.
        value : object
            The value to store in the cache.

        Returns
        -------
        None
            No value is returned.
        """
        # Map the key to the given value in the memory cache
        self.__memory_cache[key] = value

    def __contains__(self, key: str) -> bool:
        """Check if the cache contains the specified key.

        Parameters
        ----------
        key : str
            The key to check for existence in the cache.

        Returns
        -------
        bool
            True if the key exists in the cache, False otherwise.
        """
        return key in self.__memory_cache

    def __delitem__(self, key: str) -> None:
        """Remove an item from the memory cache by key.

        Parameters
        ----------
        key : str
            The key to remove from the cache.

        Returns
        -------
        None
            No value is returned.
        """
        # Silently remove the key if present
        self.__memory_cache.pop(key, None)

    def __buildHeadersASGI(self) -> Headers:
        """Build and return ASGI headers as a Headers object.

        Returns
        -------
        Headers
            The headers parsed from the ASGI scope, decoded to strings.
        """
        # If headers are already cached, return them directly
        if "headers" in self:
            return self["headers"]

        # Decode header keys and values from bytes to strings
        raw: Iterable[tuple[bytes, bytes]] = self.__headers
        decoded: list[tuple[str, str]] = [
            (k.decode("latin-1"), v.decode("latin-1"))
            for k, v in raw
        ]

        # Cache the Headers object for future lookups
        self["headers"] = Headers(decoded)
        self.setState("headers", self["headers"])

        # Return the cached Headers object
        return self["headers"]

    def client(self) -> str | None:
        """Return the remote client IP parsed from the ASGI scope dict.

        Returns
        -------
        str | None
            The client IP address as a string, or None if not available.
        """
        if "client" in self:
            return self["client"]

        raw = self.__overrides.get("client") or self.__scope.get("client")
        if not raw:
            return None

        # ASGI exposes client as a (host, port) tuple
        # __overrides may store a plain string after setClient() was called
        if isinstance(raw, str):
            return raw
        ip, port = raw[0], raw[1]

        self["client"] = ip
        self.setState("client", ip)
        self.setState("port", int(port))

        return ip

    def setClient(self, ip: str) -> None:
        """Set the remote client address in the ASGI scope dict.

        Parameters
        ----------
        ip : str
            The client IP address to assign.

        Returns
        -------
        None
            No value is returned.
        """
        # Store override without touching the original scope dict
        self.__overrides["client"] = ip
        # Keep the memory cache in sync so subsequent client() calls
        # return the updated address rather than the stale cached value.
        self["client"] = ip

    def scheme(self) -> str | None:
        """Return the URL scheme from the ASGI scope dict.

        Returns
        -------
        str | None
            The scheme string, or None if not present.
        """
        return self.__overrides.get("scheme", self.__scope.get("scheme"))

    def setScheme(self, value: str) -> None:
        """Set the URL scheme in the ASGI scope dict.

        Parameters
        ----------
        value : str
            The scheme to apply (e.g. ``'http'``, ``'https'``).

        Returns
        -------
        None
            No value is returned.
        """
        # Store override without touching the original scope dict
        self.__overrides["scheme"] = value

    def method(self) -> str | None:
        """Return the HTTP method from the ASGI scope dict.

        Returns
        -------
        str | None
            The HTTP method string, or None if not present.
        """
        return self.__scope.get("method")

    def path(self) -> str | None:
        """Return the request path from the ASGI scope dict.

        Returns
        -------
        str | None
            The URL path string, or None if not present.
        """
        return self.__scope.get("path")

    def setMethod(self, method: str) -> None:
        """Set the HTTP method in the ASGI scope dict.

        Parameters
        ----------
        method : str
            The HTTP method to set (e.g. ``'GET'``, ``'POST'``).

        Returns
        -------
        None
            No value is returned.
        """
        # Store override without touching the original scope dict
        self.__overrides["method"] = method

    def headers(self) -> Headers:
        """Return the request headers as a Headers object.

        Returns
        -------
        Headers
            The headers parsed from the ASGI scope, decoded to strings.
        """
        return self.__buildHeadersASGI()

    def setState(self, key: str, value: Any) -> None:
        """Store a value in the ASGI scope dict under the given key.

        Parameters
        ----------
        key : str
            The dict key to set.
        value : Any
            The value to store.

        Returns
        -------
        None
            No value is returned.
        """
        # Store override without touching the original scope dict
        self.__overrides[key] = value

    def wantsJson(self) -> bool:
        """Determine if the client prefers JSON based on the Accept header.

        Returns
        -------
        bool
            True if the Accept header indicates JSON is preferred,
            False otherwise.
        """
        if "wants_json" in self:
            return self["wants_json"]

        accept = self.headers().get("accept")
        if not accept:
            self["wants_json"] = False
            self.setState("wants_json", value=False)
            return False

        accept = accept.lower()

        # Match standard JSON MIME type or any JSON-based content subtype
        result = (
            "application/json" in accept
            or "+json" in accept
        )

        self["wants_json"] = result
        self.setState("wants_json", value=result)
        return result

    def getScope(self) -> dict:
        """Return the underlying protocol scope object.

        Returns the scope as adjusted by the use of other methods
        in this adapter. Reflects any modifications made through
        setClient, setScheme, setState, etc.

        Returns
        -------
        object
            The adjusted ASGI scope dict.
        """
        # Return a merged view; original scope is never mutated
        if not self.__overrides:
            return self.__scope
        return {**self.__scope, **self.__overrides}
