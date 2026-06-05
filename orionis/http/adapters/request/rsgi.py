from typing import Any, TYPE_CHECKING
from orionis.http.adapters.request.contracts.transport import TransportAdapter
from orionis.http.payload.estructures.headers import Headers

if TYPE_CHECKING:
    from granian.rsgi import Scope

class RSGITransportAdapter(TransportAdapter):

    # ruff: noqa: ANN401

    def __init__(self, scope: Scope) -> None:
        """Initialize the adapter with a Granian RSGI scope.

        Parameters
        ----------
        scope : Scope
            The Granian RSGI scope object.

        Returns
        -------
        None
            No value is returned.
        """
        # Memory cache for storing computed values like headers, client IP, etc.
        self.__memory_cache: dict[str, object] = {}
        # Store the RSGI scope and initialize the memory cache
        self.__scope: Scope = scope
        # Mutable overrides — never touches the original scope object
        self.__overrides: dict[str, Any] = {}
        # Pre-build headers for efficient access
        self.__buildHeadersRSGI()

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
        self.__memory_cache.pop(key, None)

    def __buildHeadersRSGI(self) -> Headers:
        """Build and return RSGI headers as a Headers object.

        Returns
        -------
        Headers
            The headers parsed from the RSGI scope, as string pairs.
        """
        if "headers" in self:
            return self["headers"]

        raw: list[tuple[str, str]] = []
        for key in self.__scope.headers:
            values = self.__scope.headers.get_all(key)
            raw.extend((str(key).lower(), value) for value in values)

        self["headers"] = Headers(raw)
        self.setState("headers", value=self["headers"])

        return self["headers"]

    def client(self) -> str | None:
        """Return the remote client address parsed from the RSGI scope.

        Returns
        -------
        str | None
            The client IP address as a string, or None if not available.
        """
        if "client" in self:
            return self["client"]

        raw = self.__scope.client
        if not raw:
            return None

        # Handle IPv6 with port (e.g. "[2001:db8::1]:8080") or
        # standard IPv4 with port (e.g. "192.168.1.1:8080")
        if raw.count(":") > 1:
            ip, port = raw.rsplit(":", 1)
        else:
            ip, port = raw.split(":", 1)

        self["client"] = ip
        self.setState("client", ip)
        self.setState("port", value=int(port))

        return ip

    def setClient(self, ip: str) -> None:
        """Set the remote client address in the RSGI scope dict.

        Parameters
        ----------
        ip : str
            The client IP address to assign.

        Returns
        -------
        None
            No value is returned.
        """
        self.__overrides["client"] = ip
        self["client"] = ip

    def scheme(self) -> str | None:
        """Return the URL scheme from the RSGI scope.

        Returns
        -------
        str | None
            The scheme string, or None if not set.
        """
        return self.__overrides.get("scheme", self.__scope.scheme)

    def setScheme(self, value: str) -> None:
        """Set the URL scheme in the RSGI scope.

        Parameters
        ----------
        value : str
            The scheme to apply (e.g. ``'http'``, ``'https'``).

        Returns
        -------
        None
            No value is returned.
        """
        self.__overrides["scheme"] = value

    def method(self) -> str | None:
        """Return the HTTP method from the RSGI scope.

        Returns
        -------
        str | None
            The HTTP method string, or None if not set.
        """
        return self.__overrides.get("method", self.__scope.method)

    def setMethod(self, method: str) -> None:
        """Set the HTTP method in the RSGI scope.

        Parameters
        ----------
        method : str
            The HTTP method to set (e.g. ``'GET'``, ``'POST'``).

        Returns
        -------
        None
            No value is returned.
        """
        self.__overrides["method"] = method

    def path(self) -> str | None:
        """Return the request path from the RSGI scope.

        Returns
        -------
        str | None
            The URL path string, or None if not set.
        """
        return self.__scope.path

    def headers(self) -> Headers:
        """Return the request headers as a Headers object.

        Returns
        -------
        Headers
            The headers parsed from the RSGI scope, as string pairs.
        """
        return self.__buildHeadersRSGI()

    def setState(self, key: str, value: Any) -> None:
        """Store a value as an attribute on the RSGI scope.

        Parameters
        ----------
        key : str
            The attribute name to set.
        value : Any
            The value to store.

        Returns
        -------
        None
            No value is returned.
        """
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

        result = (
            "application/json" in accept
            or "+json" in accept
        )

        self["wants_json"] = result
        self.setState("wants_json", value=result)
        return result

    def getScope(self) -> dict:
        """Return a dict representation of the RSGI scope.

        Returns
        -------
        dict
            A dict with all Granian Scope fields plus any values set
            via setState/setClient/setScheme.  The original scope object
            is never mutated.
        """
        base: dict[str, Any] = {
            "proto"        : self.__scope.proto,
            "http_version" : self.__scope.http_version,
            "rsgi_version" : self.__scope.rsgi_version,
            "server"       : self.__scope.server,
            "client"       : self.__scope.client,
            "scheme"       : self.__scope.scheme,
            "method"       : self.__scope.method,
            "path"         : self.__scope.path,
            "query_string" : self.__scope.query_string,
            "authority"    : self.__scope.authority,
            "headers"      : self.__scope.headers,
        }
        if self.__overrides:
            base.update(self.__overrides)
        return base
