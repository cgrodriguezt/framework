from __future__ import annotations
from dataclasses import dataclass, field
from orionis.environment.env import Env
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Redis(BaseEntity):
    """
    Represent the configuration entity for a Redis cache store.

    Attributes
    ----------
    driver : str
        The driver type. Defaults to ``'redis'``.
    endpoint : str | None
        Redis host address. Resolved from the ``REDIS_HOST`` environment
        variable or defaults to ``'127.0.0.1'``.
    port : int
        Redis port number. Resolved from the ``REDIS_PORT`` environment
        variable or defaults to ``6379``.
    db : int
        Redis database index. Resolved from the ``REDIS_DB`` environment
        variable or defaults to ``0``.
    password : str | None
        Redis password. Resolved from the ``REDIS_PASSWORD`` environment
        variable or defaults to ``None``.
    """

    driver: str = field(
        default="redis",
        metadata={
            "description": (
                "The driver type for the cache store. Defaults to 'redis'."
            ),
            "default": "redis",
        },
    )

    endpoint: str | None = field(
        default_factory=lambda: Env.get("REDIS_HOST", "127.0.0.1"),
        metadata={
            "description": "Redis host address.",
            "default": "127.0.0.1",
        },
    )

    port: int = field(
        default_factory=lambda: Env.get("REDIS_PORT", 6379),
        metadata={
            "description": "Redis port.",
            "default": 6379,
        },
    )

    db: int = field(
        default_factory=lambda: Env.get("REDIS_DB", 0),
        metadata={
            "description": "Redis database index.",
            "default": 0,
        },
    )

    password: str | None = field(
        default_factory=lambda: Env.get("REDIS_PASSWORD"),
        metadata={
            "description": "Redis password.",
            "default": None,
        },
    )

    def __post_init__(self) -> None:
        """
        Validate the Redis configuration after initialization.

        Returns
        -------
        None
            Delegates validation to the parent ``BaseEntity.__post_init__``.
        """
        # Delegate base-class field validation
        super().__post_init__()
