from enum import Enum

class PersistentDrivers(Enum):
    """
    Enumerate supported persistent storage drivers.

    Attributes
    ----------
    JSON : str
        Represents the JSON file-based storage driver.
    SQLITE : str
        Represents the SQLite database storage driver.

    Returns
    -------
    PersistentDrivers
        The enumeration member representing a storage driver.
    """

    JSON = "json"
    SQLITE = "sqlite"
