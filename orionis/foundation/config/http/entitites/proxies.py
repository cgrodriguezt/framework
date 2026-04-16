from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.http.enums.strategies import ProxyStrategy
from orionis.foundation.config.http.entitites.proxy_strategy import (
    ProxyStrategy as ProxyStrategyEntity,
)
from orionis.services.environment.env import Env
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class HTTPProxies(BaseEntity):
    """Configure trusted proxy resolution."""

    trusted_proxies: list[str] = field(
        default_factory=lambda: Env.get("TRUSTED_PROXIES", []),
        metadata={
            "description": (
                "List of trusted proxy IP addresses or CIDR ranges."
            ),
        },
    )

    proxy_strategy: ProxyStrategy | str = field(
        default=Env.get("PROXY_STRATEGY", ProxyStrategy.STANDARD),
        metadata={
            "description": (
                "Proxy strategy to determine client IP and scheme resolution."
            ),
        },
    )

    proxy_strategies: dict[str, ProxyStrategyEntity] = field(
        default_factory=lambda: {
            "standard": ProxyStrategyEntity(
                ip_header="x-forwarded-for",
                proto_header="x-forwarded-proto",
            ),
            "nginx": ProxyStrategyEntity(
                ip_header="x-real-ip",
                proto_header="x-forwarded-proto",
            ),
            "cloudflare": ProxyStrategyEntity(
                ip_header="cf-connecting-ip",
                proto_header="x-forwarded-proto",
            ),
            "aws": ProxyStrategyEntity(
                ip_header="x-forwarded-for",
                proto_header="x-forwarded-proto",
            ),
            "fastly": ProxyStrategyEntity(
                ip_header="fastly-client-ip",
                proto_header="x-forwarded-proto",
            ),
        },
        metadata={
            "description": (
                "Mapping of proxy strategy names to their configurations."
            ),
        },
    )

    def __post_init__(self) -> None:
        """Validate and normalise proxy fields.

        Raises
        ------
        TypeError
            If any field has an unexpected type.
        ValueError
            If any field is outside its allowed domain.

        Returns
        -------
        None
        """
        super().__post_init__()
        self.__validateTrustedProxies()
        self.__validateProxyStrategy()
        self.__validateProxyStrategies()

    def __validateTrustedProxies(self) -> None:
        """Validate the ``trusted_proxies`` field.

        Raises
        ------
        TypeError
            If the value is not a list of strings.

        Returns
        -------
        None
        """
        if not isinstance(self.trusted_proxies, list):
            error_msg = (
                "Invalid type for 'trusted_proxies': expected a list of strings."
            )
            raise TypeError(error_msg)

        if not all(
            isinstance(p, str)
            for p in self.trusted_proxies
        ):
            error_msg = (
                "Invalid type for 'trusted_proxies': all items must be strings."
            )
            raise TypeError(error_msg)

    def __validateProxyStrategy(self) -> None:
        """Validate and normalise ``proxy_strategy``.

        Coerce a raw string to the corresponding
        ``ProxyStrategy`` enum value.

        Raises
        ------
        TypeError
            If the value is not a ``ProxyStrategy``
            or str.
        ValueError
            If the string does not match any member.

        Returns
        -------
        None
        """
        if not isinstance(
            self.proxy_strategy, (ProxyStrategy, str),
        ):
            error_msg = (
                "Invalid type for 'proxy_strategy': expected a ProxyStrategy or string."
            )
            raise TypeError(error_msg)

        # Normalise string values to canonical enum value
        if isinstance(self.proxy_strategy, str):
            _value = self.proxy_strategy.upper().strip()
            if _value not in ProxyStrategy._member_names_:
                error_msg = (
                    f"Invalid proxy strategy: {self.proxy_strategy}. Must be one "
                    f"of {ProxyStrategy._member_names_!s}."
                )
                raise ValueError(error_msg)
            object.__setattr__(
                self,
                "proxy_strategy",
                ProxyStrategy[_value].value,
            )
        else:
            object.__setattr__(
                self,
                "proxy_strategy",
                self.proxy_strategy.value,
            )

    def __validateProxyStrategies(self) -> None:
        """Validate and normalise ``proxy_strategies``.

        Ensure the mapping contains string keys and
        ``ProxyStrategyEntity`` or dict values. Dicts are
        coerced into ``ProxyStrategyEntity`` instances.

        Raises
        ------
        TypeError
            If the structure or entries have wrong types.

        Returns
        -------
        None
        """
        if not isinstance(self.proxy_strategies, dict):
            error_msg = (
                "Invalid type for 'proxy_strategies': expected a dict."
            )
            raise TypeError(error_msg)

        for key, val in self.proxy_strategies.items():
            if not isinstance(key, str):
                error_msg = (
                    "Invalid type for 'proxy_strategies': all keys must be strings."
                )
                raise TypeError(error_msg)
            if not isinstance(
                val, (ProxyStrategyEntity, dict),
            ):
                error_msg = (
                    f"Invalid type for 'proxy_strategies[{key}]': "
                    "expected a ProxyStrategy entity or dict, "
                    f"got {type(val).__name__}."
                )
                raise TypeError(error_msg)

        # Coerce dict entries into entity instances
        _normalised: dict[str, ProxyStrategyEntity] = {}
        for key, val in self.proxy_strategies.items():
            _normalised[key] = (
                ProxyStrategyEntity(**val)
                if isinstance(val, dict)
                else val
            )
        object.__setattr__(
            self, "proxy_strategies", _normalised,
        )
