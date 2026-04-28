from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from granian.rsgi import Scope

class TransportAdapter:
    """
    Read/write abstraction over a protocol scope (ASGI or RSGI).

    Decouples middleware logic from the underlying transport protocol,
    allowing all middlewares to operate against a single unified
    interface regardless of whether the server speaks ASGI or RSGI.
    """

    # --- client ---

    def client(self) -> tuple[str, int] | None:
        """Return the remote client address as a (host, port) tuple.

        Returns
        -------
        tuple[str, int] | None
            The client IP and port, or None if unavailable.
        """
        raise NotImplementedError

    def setClient(self, ip: str, port: int) -> None:
        """Set the remote client address on the underlying scope.

        Parameters
        ----------
        ip : str
            The client IP address.
        port : int
            The client port number.

        Returns
        -------
        None
        """
        raise NotImplementedError

    # --- scheme ---

    def scheme(self) -> str | None:
        """Return the URL scheme of the current request.

        Returns
        -------
        str | None
            The scheme (e.g. ``'http'``, ``'https'``), or None.
        """
        raise NotImplementedError

    def setScheme(self, value: str) -> None:
        """Set the URL scheme on the underlying scope.

        Parameters
        ----------
        value : str
            The scheme to apply (e.g. ``'http'``, ``'https'``).

        Returns
        -------
        None
        """
        raise NotImplementedError

    # --- request metadata ---

    def method(self) -> str | None:
        """Return the HTTP method of the current request.

        Returns
        -------
        str | None
            The HTTP method (e.g. ``'GET'``, ``'POST'``), or None.
        """
        raise NotImplementedError

    def path(self) -> str | None:
        """Return the URL path of the current request.

        Returns
        -------
        str | None
            The request path, or None if unavailable.
        """
        raise NotImplementedError

    # --- headers ---

    def getHeader(self, name: str) -> str | None:
        """Return the first value of a request header by name.

        Parameters
        ----------
        name : str
            The header name (case-insensitive).

        Returns
        -------
        str | None
            The first header value, or None if the header is absent.
        """
        raise NotImplementedError

    def getAllHeaders(self, name: str) -> list[str]:
        """Return all values of a request header by name.

        Parameters
        ----------
        name : str
            The header name (case-insensitive).

        Returns
        -------
        list[str]
            All values for the given header, or an empty list if absent.
        """
        raise NotImplementedError

    # --- state ---

    def setState(self, key: str, value: Any) -> None:
        """Store an arbitrary value in the scope under the given key.

        Parameters
        ----------
        key : str
            The attribute or dict key to set.
        value : Any
            The value to store.

        Returns
        -------
        None
        """
        raise NotImplementedError

    def wantsJson(self) -> bool:
        """Determine if the client prefers a JSON response based on the Accept header.

        Returns
        -------
        bool
            True if the Accept header indicates JSON is preferred, otherwise False.
        """
        raise NotImplementedError

class RSGITransportAdapter(TransportAdapter):
    """TransportAdapter implementation for Granian RSGI scopes."""

    def __init__(self, scope: Scope) -> None:
        """Initialize the adapter with a Granian RSGI scope.

        Parameters
        ----------
        scope : Scope
            The Granian RSGI scope object.

        Returns
        -------
        None
        """
        self._scope = scope

    def client(self) -> tuple[str, int] | None:
        """Return the remote client address parsed from the RSGI scope.

        Returns
        -------
        tuple[str, int] | None
            The client IP and port, or None if the client is not set.
        """
        raw = self._scope.client
        if not raw:
            return None
        # RSGI encodes client as "ip:port"; rpartition handles IPv6
        ip, _, port = raw.rpartition(":")
        return ip, int(port)

    def setClient(self, ip: str, port: int) -> None:
        """Set the remote client address on the RSGI scope.

        Parameters
        ----------
        ip : str
            The client IP address.
        port : int
            The client port number.

        Returns
        -------
        None
        """
        self._scope.client = f"{ip}:{port}"

    def scheme(self) -> str | None:
        """Return the URL scheme from the RSGI scope.

        Returns
        -------
        str | None
            The scheme string, or None if not set.
        """
        return self._scope.scheme

    def setScheme(self, value: str) -> None:
        """Set the URL scheme on the RSGI scope.

        Parameters
        ----------
        value : str
            The scheme to apply (e.g. ``'http'``, ``'https'``).

        Returns
        -------
        None
        """
        self._scope.scheme = value

    def method(self) -> str | None:
        """Return the HTTP method from the RSGI scope.

        Returns
        -------
        str | None
            The HTTP method string, or None if not set.
        """
        return self._scope.method

    def path(self) -> str | None:
        """Return the request path from the RSGI scope.

        Returns
        -------
        str | None
            The URL path string, or None if not set.
        """
        return self._scope.path

    def getHeader(self, name: str) -> str | None:
        """Return the first value of a request header from the RSGI scope.

        Parameters
        ----------
        name : str
            The header name (case-insensitive).

        Returns
        -------
        str | None
            The first header value, or None if the header is absent.
        """
        # Normalize to lowercase per HTTP header conventions
        values = self._scope.headers.get_all(name.lower())
        return values[0] if values else None

    def getAllHeaders(self, name: str) -> list[str]:
        """Return all values of a request header from the RSGI scope.

        Parameters
        ----------
        name : str
            The header name (case-insensitive).

        Returns
        -------
        list[str]
            All header values for the given name, or an empty list.
        """
        return self._scope.headers.get_all(name.lower()) or []

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
        """
        setattr(self._scope, key, value)

    def wantsJson(self) -> bool:
        """
        Determine if the client prefers a JSON response based on the Accept
        header.

        Returns
        -------
        bool
            True if the Accept header indicates JSON is preferred, otherwise
            False.
        """
        # Check the Accept header for JSON MIME types
        accept = self.getHeader("Accept")

        # If no Accept header is present, assume JSON is not expected
        if not accept:
            return False

        # Check for specific JSON MIME types in the Accept header
        if "application/json" in accept or "application/*+json" in accept:
            return True

        # If the Accept header is present but does not indicate JSON, return False
        return False

class ASGITransportAdapter(TransportAdapter):
    """TransportAdapter implementation for ASGI scopes (dict-based)."""

    def __init__(self, scope: dict) -> None:
        """Initialize the adapter with an ASGI scope dict.

        Parameters
        ----------
        scope : dict
            The ASGI scope dictionary.

        Returns
        -------
        None
        """
        self._scope = scope
        # Cache header list to avoid repeated dict lookups per request
        self._headers: list[tuple[bytes, bytes]] = scope.get("headers", [])

    def client(self) -> tuple[str, int] | None:
        """Return the remote client address from the ASGI scope dict.

        Returns
        -------
        tuple[str, int] | None
            The client IP and port, or None if absent.
        """
        raw = self._scope.get("client")
        if not raw:
            return None
        return raw[0], raw[1]

    def setClient(self, ip: str, port: int) -> None:
        """Set the remote client address in the ASGI scope dict.

        Parameters
        ----------
        ip : str
            The client IP address.
        port : int
            The client port number.

        Returns
        -------
        None
        """
        self._scope["client"] = (ip, port)

    def scheme(self) -> str | None:
        """Return the URL scheme from the ASGI scope dict.

        Returns
        -------
        str | None
            The scheme string, or None if not present.
        """
        return self._scope.get("scheme")

    def setScheme(self, value: str) -> None:
        """Set the URL scheme in the ASGI scope dict.

        Parameters
        ----------
        value : str
            The scheme to apply (e.g. ``'http'``, ``'https'``).

        Returns
        -------
        None
        """
        self._scope["scheme"] = value

    def method(self) -> str | None:
        """Return the HTTP method from the ASGI scope dict.

        Returns
        -------
        str | None
            The HTTP method string, or None if not present.
        """
        return self._scope.get("method")

    def path(self) -> str | None:
        """Return the request path from the ASGI scope dict.

        Returns
        -------
        str | None
            The URL path string, or None if not present.
        """
        return self._scope.get("path")

    def getHeader(self, name: str) -> str | None:
        """Return the first value of a request header from the ASGI scope.

        Parameters
        ----------
        name : str
            The header name (case-insensitive).

        Returns
        -------
        str | None
            The first matching header value decoded as latin-1, or None.
        """
        # Encode once for efficient byte-level comparison with raw headers
        target = name.lower().encode("latin-1")
        for k, v in self._headers:
            if k.lower() == target:
                return v.decode("latin-1")
        return None

    def getAllHeaders(self, name: str) -> list[str]:
        """Return all values of a request header from the ASGI scope.

        Parameters
        ----------
        name : str
            The header name (case-insensitive).

        Returns
        -------
        list[str]
            All matching header values decoded as latin-1.
        """
        target = name.lower().encode("latin-1")
        return [
            v.decode("latin-1")
            for k, v in self._headers
            if k.lower() == target
        ]

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
        """
        self._scope[key] = value

    def wantsJson(self) -> bool:
        """
        Determine if the client prefers a JSON response based on the Accept
        header.

        Returns
        -------
        bool
            True if the Accept header indicates JSON is preferred, otherwise
            False.
        """
        accept = self.getHeader("Accept")
        if not accept:
            return False
        return "application/json" in accept or "application/*+json" in accept