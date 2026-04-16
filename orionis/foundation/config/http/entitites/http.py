from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.http.entitites.cors import Cors
from orionis.foundation.config.http.entitites.proxies import (
    HTTPProxies,
)
from orionis.foundation.config.http.entitites.rate_limit import (
    HTTPRateLimit,
)
from orionis.foundation.config.http.entitites.request import (
    HTTPRequest,
)
from orionis.foundation.config.http.entitites.security import (
    HTTPSecurity,
)
from orionis.support.entities.base import BaseEntity


@dataclass(frozen=True, kw_only=True)
class HTTP(BaseEntity):
    """Configure HTTP request handling and security."""

    proxies: HTTPProxies | dict = field(
        default_factory=HTTPProxies,
        metadata={
            "description": (
                "Trusted proxy resolution settings."
            ),
        },
    )

    security: HTTPSecurity | dict = field(
        default_factory=HTTPSecurity,
        metadata={
            "description": (
                "Security header validation settings."
            ),
        },
    )

    rate_limit: HTTPRateLimit | dict = field(
        default_factory=HTTPRateLimit,
        metadata={
            "description": (
                "Global rate limiting settings."
            ),
        },
    )

    request: HTTPRequest | dict = field(
        default_factory=HTTPRequest,
        metadata={
            "description": (
                "Request body and method handling "
                "settings."
            ),
        },
    )

    cors: Cors | dict = field(
        default_factory=Cors,
        metadata={
            "description": (
                "CORS (Cross-Origin Resource Sharing) "
                "settings."
            ),
        },
    )

    def __post_init__(self) -> None:
        """Validate and coerce all composite fields.

        Convert dict values to their corresponding
        entity instances when provided as plain dicts.

        Raises
        ------
        TypeError
            If any field has an unexpected type.

        Returns
        -------
        None
        """
        super().__post_init__()
        self.__validateProxies()
        self.__validateSecurity()
        self.__validateRateLimit()
        self.__validateRequest()
        self.__validateCors()

    def __validateProxies(self) -> None:
        """Validate the ``proxies`` field.

        Coerce a dict to ``HTTPProxies`` if needed.

        Raises
        ------
        TypeError
            If the value is not an ``HTTPProxies``
            or dict.

        Returns
        -------
        None
        """
        if not isinstance(
            self.proxies, (HTTPProxies, dict),
        ):
            error_msg = (
                "Invalid type for 'proxies': expected "
                "an HTTPProxies instance or dict."
            )
            raise TypeError(error_msg)

        if isinstance(self.proxies, dict):
            object.__setattr__(
                self,
                "proxies",
                HTTPProxies(**self.proxies),
            )

    def __validateSecurity(self) -> None:
        """Validate the ``security`` field.

        Coerce a dict to ``HTTPSecurity`` if needed.

        Raises
        ------
        TypeError
            If the value is not an ``HTTPSecurity``
            or dict.

        Returns
        -------
        None
        """
        if not isinstance(
            self.security, (HTTPSecurity, dict),
        ):
            error_msg = (
                "Invalid type for 'security': expected "
                "an HTTPSecurity instance or dict."
            )
            raise TypeError(error_msg)

        if isinstance(self.security, dict):
            object.__setattr__(
                self,
                "security",
                HTTPSecurity(**self.security),
            )

    def __validateRateLimit(self) -> None:
        """Validate the ``rate_limit`` field.

        Coerce a dict to ``HTTPRateLimit`` if needed.

        Raises
        ------
        TypeError
            If the value is not an ``HTTPRateLimit``
            or dict.

        Returns
        -------
        None
        """
        if not isinstance(
            self.rate_limit, (HTTPRateLimit, dict),
        ):
            error_msg = (
                "Invalid type for 'rate_limit': "
                "expected an HTTPRateLimit instance "
                "or dict."
            )
            raise TypeError(error_msg)

        if isinstance(self.rate_limit, dict):
            object.__setattr__(
                self,
                "rate_limit",
                HTTPRateLimit(**self.rate_limit),
            )

    def __validateRequest(self) -> None:
        """Validate the ``request`` field.

        Coerce a dict to ``HTTPRequest`` if needed.

        Raises
        ------
        TypeError
            If the value is not an ``HTTPRequest``
            or dict.

        Returns
        -------
        None
        """
        if not isinstance(
            self.request, (HTTPRequest, dict),
        ):
            error_msg = (
                "Invalid type for 'request': expected "
                "an HTTPRequest instance or dict."
            )
            raise TypeError(error_msg)

        if isinstance(self.request, dict):
            object.__setattr__(
                self,
                "request",
                HTTPRequest(**self.request),
            )

    def __validateCors(self) -> None:
        """Validate the ``cors`` field.

        Coerce a dict to ``Cors`` if needed.

        Raises
        ------
        TypeError
            If the value is not a ``Cors``
            or dict.

        Returns
        -------
        None
        """
        if not isinstance(self.cors, (Cors, dict)):
            error_msg = (
                "Invalid type for 'cors': expected "
                "a Cors instance or dict."
            )
            raise TypeError(error_msg)

        if isinstance(self.cors, dict):
            object.__setattr__(
                self,
                "cors",
                Cors(**self.cors),
            )

