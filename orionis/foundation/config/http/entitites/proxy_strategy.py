from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class ProxyStrategy:
    """
    Define how Orionis resolves client IP and scheme from proxy headers.

    Attributes
    ----------
    ip_header : str
        Header name to extract client IP address.
    proto_header : str
        Header name to extract client protocol/scheme.
    """

    ip_header: str
    proto_header: str
