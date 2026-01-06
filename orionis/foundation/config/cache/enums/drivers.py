from enum import Enum

class Drivers(Enum):
    """
    Enumerate supported cache drivers.

    Attributes
    ----------
    FILE : str
        Represents a file-based cache driver.
    MEMCACHED : str
        Represents a Memcached cache driver.
    REDIS : str
        Represents a Redis cache driver.

    Returns
    -------
    Drivers
        An enumeration member representing a cache driver.
    """

    FILE = "file"
    MEMCACHED = "memcached"
    REDIS = "redis"
