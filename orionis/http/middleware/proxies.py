from __future__ import annotations
from ipaddress import ip_address, ip_network, IPv4Network, IPv6Network
from typing import TYPE_CHECKING
from orionis.foundation.config.http.entitites.proxies import HTTPProxies
from orionis.http.adapters.request.asgi import ASGITransportAdapter
from orionis.http.adapters.request.rsgi import RSGITransportAdapter

if TYPE_CHECKING:
    from collections.abc import Iterable
    from granian.rsgi import Scope
    from orionis.http.adapters.request.transport import TransportAdapter

class ProxiesMiddleware:
    """
    Normalize client IP and scheme using trusted proxy headers.

    - Supports multiple proxies (X-Forwarded-For chain)
    - Supports multiple headers (get_all)
    - Prevents spoofing via trusted proxy validation
    """

    def __init__(
        self,
        config: dict,
    ) -> None:
        """
        Initialize the middleware with the given proxy configuration.

        Parameters
        ----------
        config : dict
            A dictionary whose keys must match ``HTTPProxies`` fields.

        Returns
        -------
        None
        """
        self.__config = HTTPProxies(**config)
        self.__trusted_proxies = self.__config.trusted_proxies
        # Resolve the active strategy from the selected strategy key
        self.__strategy = self.__config.proxy_strategies[
            self.__config.proxy_strategy
        ]
        self.__ip_header = self.__strategy.ip_header.lower()
        self.__proto_header = self.__strategy.proto_header.lower()
        # Pre-compile proxy CIDRs into network objects for fast membership tests
        self.__trusted_networks = self._compile(self.__trusted_proxies)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handleRSGI(self, scope: Scope) -> Scope:
        """
        Process an RSGI scope and normalize its client IP and scheme.

        Parameters
        ----------
        scope : Scope
            The RSGI connection scope to process.

        Returns
        -------
        Scope
            The same scope object with updated client and scheme fields.
        """
        adapter: TransportAdapter = RSGITransportAdapter(scope)
        self.__process(adapter)
        return scope

    def handleASGI(self, scope: dict) -> dict:
        """
        Process an ASGI scope and normalize its client IP and scheme.

        Parameters
        ----------
        scope : dict
            The ASGI connection scope to process.

        Returns
        -------
        dict
            The same scope dict with updated client and scheme fields.
        """
        adapter: TransportAdapter = ASGITransportAdapter(scope)
        self.__process(adapter)
        return scope

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    def __process(self, adapter: TransportAdapter) -> None:
        """
        Apply trusted-proxy normalization to the transport adapter.

        Parameters
        ----------
        adapter : TransportAdapter
            Abstraction over an RSGI or ASGI scope.

        Returns
        -------
        None
            Mutates ``adapter`` in place; no value is returned.
        """
        client = adapter.client()
        if not client:
            return

        client_ip, client_port = client

        # Skip requests that do not originate from a trusted proxy
        if not self.__isTrusted(client_ip):
            return

        real_ip, proxies, chain = self.__resolveForwardedChain(
            adapter, client_ip,
        )

        adapter.setClient(real_ip, client_port)

        scheme = self.__resolveScheme(adapter)
        if scheme:
            adapter.setScheme(scheme)

        # Expose resolved forwarding metadata for downstream middleware
        adapter.setState("forwarded", {
            "client": real_ip,
            "proxies": proxies,
            "chain": chain,
        })

    # ------------------------------------------------------------------
    # Forwarded chain
    # ------------------------------------------------------------------

    def __resolveForwardedChain(
        self,
        adapter: TransportAdapter,
        fallback_ip: str,
    ) -> tuple[str, list[str], list[str]]:
        """
        Resolve the real client IP from the forwarded header chain.

        Walks the chain right-to-left to skip trusted intermediaries
        and find the first untrusted address.

        Parameters
        ----------
        adapter : TransportAdapter
            Transport abstraction providing header access.
        fallback_ip : str
            IP to return when no forwarded chain header is present.

        Returns
        -------
        tuple[str, list[str], list[str]]
            A three-element tuple of ``(real_ip, proxies, full_chain)``.
        """
        chain = self.__getForwardedChain(adapter)

        if not chain:
            return fallback_ip, [], [fallback_ip]

        real_ip: str | None = None

        # Traverse right-to-left; the first untrusted IP is the real client
        for ip in reversed(chain):
            if not self.__isTrusted(ip):
                real_ip = ip
                break

        # If every hop is trusted, fall back to the leftmost IP
        if real_ip is None:
            real_ip = chain[0]

        proxies = [ip for ip in chain if ip != real_ip]

        return real_ip, proxies, chain

    def __resolveScheme(self, adapter: TransportAdapter) -> str | None:
        """
        Determine the original request scheme from forwarded headers.

        Parameters
        ----------
        adapter : TransportAdapter
            Transport abstraction providing header access.

        Returns
        -------
        str or None
            ``'http'`` or ``'https'`` when the header is valid;
            ``None`` otherwise.
        """
        values = adapter.getAllHeaders(self.__proto_header)

        if not values:
            return None

        # Only the first header value is considered; normalize case
        value = values[0].strip().lower()

        if value in ("http", "https"):
            return value

        return None

    def __getForwardedChain(self, adapter: TransportAdapter) -> list[str]:
        """
        Extract and validate all IPs from the forwarded-for header.

        Parameters
        ----------
        adapter : TransportAdapter
            Transport abstraction providing header access.

        Returns
        -------
        list[str]
            Ordered list of valid IP addresses found in the header.
        """
        ips: list[str] = []

        for value in adapter.getAllHeaders(self.__ip_header):
            # Headers may contain comma-separated IP lists
            for raw_ip in value.split(","):
                ip = raw_ip.strip()
                if ip and self.__isValidIP(ip):
                    ips.append(ip)

        return ips

    def _compile(
        self,
        proxies: Iterable[str],
    ) -> list[IPv4Network | IPv6Network]:
        """
        Compile proxy identifiers into network objects.

        The special token ``'private'`` expands into the standard
        RFC-1918 and loopback address ranges.

        Parameters
        ----------
        proxies : Iterable[str]
            An iterable of CIDR strings or the keyword ``'private'``.

        Returns
        -------
        list[IPv4Network | IPv6Network]
            Compiled network objects used for IP membership tests.
        """
        networks: list[IPv4Network | IPv6Network] = []

        for p in proxies:
            if p == "private":
                # Expand shorthand to RFC-1918 + loopback networks
                networks.extend(self.__privateNetworks())
            else:
                networks.append(ip_network(p, strict=False))

        return networks

    def __isTrusted(self, ip: str) -> bool:
        """
        Determine whether an IP address belongs to a trusted network.

        Parameters
        ----------
        ip : str
            The IP address string to evaluate.

        Returns
        -------
        bool
            ``True`` if the address is within a trusted network;
            ``False`` otherwise, including on parse errors.
        """
        try:
            ip_obj = ip_address(ip)
        except ValueError:
            return False

        return any(ip_obj in net for net in self.__trusted_networks)

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------

    def __isValidIP(self, value: str) -> bool:
        """
        Validate that a string represents a well-formed IP address.

        Parameters
        ----------
        value : str
            The string to validate.

        Returns
        -------
        bool
            ``True`` if ``value`` is a valid IPv4 or IPv6 address;
            ``False`` otherwise.
        """
        try:
            ip_address(value)
            return True
        except ValueError:
            return False

    def __privateNetworks(self) -> list[IPv4Network]:
        """
        Return the standard set of private and loopback IPv4 networks.

        Returns
        -------
        list[IPv4Network]
            Networks covering loopback (127/8) and RFC-1918 ranges
            10/8, 172.16/12, and 192.168/16.
        """
        return [
            ip_network("127.0.0.0/8"),
            ip_network("10.0.0.0/8"),
            ip_network("172.16.0.0/12"),
            ip_network("192.168.0.0/16"),
        ]
