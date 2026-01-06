from enum import Enum

class MySQLEngine(Enum):
    """
    Enumerate supported MySQL storage engines.

    This enum is used to specify the storage engine for MySQL database tables.

    Attributes
    ----------
    INNODB : str
        Default transactional storage engine, supports ACID compliance and
        foreign keys.
    MYISAM : str
        Legacy non-transactional storage engine, faster for read-heavy
        workloads but lacks transaction support.
    MEMORY : str
        Stores all data in RAM for fast access, data is lost on server restart.
    NDB : str
        Clustered storage engine designed for distributed MySQL setups.

    Returns
    -------
    MySQLEngine
        An enumeration member representing a MySQL storage engine.
    """

    INNODB = "InnoDB"      # Default engine (transactional)
    MYISAM = "MyISAM"      # Legacy engine (non-transactional)
    MEMORY = "MEMORY"      # In-memory storage
    NDB = "NDB"            # Clustered storage engine
