from enum import StrEnum

class SessionDriver(StrEnum):
    """Session driver enum."""

    MEMORY = "memory"
    FILE = "file"
    DATABASE = "database"
    CACHE = "cache"
