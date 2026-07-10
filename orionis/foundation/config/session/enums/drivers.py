from enum import StrEnum

class SessionDriver(StrEnum):
    """Session driver enum."""

    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"
    MEMCACHED = "memcached"
    DATABASE = "database"
