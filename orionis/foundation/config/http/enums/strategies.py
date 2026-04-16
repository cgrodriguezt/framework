from enum import StrEnum

class ProxyStrategy(StrEnum):
    """
    Define proxy strategy enumeration values.

    This enum represents different proxy server strategies that can be
    used for HTTP request handling.

    Returns
    -------
    StrEnum
        An enumeration with string values for each proxy strategy.

    """

    STANDARD = "standard"
    NGINX = "nginx"
    CLOUDFLARE = "cloudflare"
    AWS = "aws"
    FASTLY = "fastly"
