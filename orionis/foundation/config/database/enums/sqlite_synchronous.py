from enum import Enum

class SQLiteSynchronous(Enum):
    """
    Represent SQLite synchronous settings for transaction durability.

    Attributes
    ----------
    FULL : str
        Provides maximum data integrity and durability, but is the slowest option.
    NORMAL : str
        Offers a balance between data safety and performance.
    OFF : str
        Maximizes speed, but data may be lost in the event of a crash.

    Returns
    -------
    SQLiteSynchronous
        Enum member representing the synchronous setting.
    """

    FULL = "FULL"      # Greater safety, slower
    NORMAL = "NORMAL"  # Balance between safety and performance
    OFF = "OFF"        # Greater speed, less safe in case of failures
