from __future__ import annotations
from dataclasses import dataclass, field
from orionis.environment.env import Env
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Memcached(BaseEntity):
    """
    Represent the configuration entity for a Memcached cache store.

    Attributes
    ----------
    driver : str
        The driver type. Defaults to ``'memcached'``.
    endpoint : str | None
        Memcached host address. Resolved from the ``MEMCACHED_HOST``
        environment variable or defaults to ``'127.0.0.1'``.
    port : int
        Memcached port number. Resolved from the ``MEMCACHED_PORT``
        environment variable or defaults to ``11211``.
    """

    driver: str = field(
        default="memcached",
        metadata={
            "description": (
                "The driver type for the cache store. "
                "Defaults to 'memcached'."
            ),
            "default": "memcached",
        },
    )

    endpoint: str | None = field(
        default_factory=lambda: Env.get("MEMCACHED_HOST", "127.0.0.1"),
        metadata={
            "description": "Memcached host address.",
            "default": "127.0.0.1",
        },
    )

    port: int = field(
        default_factory=lambda: Env.get("MEMCACHED_PORT", 11211),
        metadata={
            "description": "Memcached port.",
            "default": 11211,
        },
    )

    def __post_init__(self) -> None:
        """
        Validate the Memcached configuration after initialization.

        Returns
        -------
        None
            Delegates validation to the parent ``BaseEntity.__post_init__``.
        """
        # Delegate base-class field validation
        super().__post_init__()
