from dataclasses import dataclass, field
from orionis.foundation.config.database.entities.mysql import MySQL
from orionis.foundation.config.database.entities.oracle import Oracle
from orionis.foundation.config.database.entities.pgsql import PGSQL
from orionis.foundation.config.database.entities.sqlite import SQLite
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.support.entities.base import BaseEntity

@dataclass(unsafe_hash=True, kw_only=True)
class Connections(BaseEntity):
    """
    Data class to represent all database connections used by the application.

    Attributes
    ----------
    sqlite : Sqlite
        Configuration for the SQLite database connection.
    mysql : MySQL
        Configuration for the MySQL database connection.
    pgsql : Pgsql
        Configuration for the PostgreSQL database connection.
    oracle : Oracle
        Configuration for the Oracle database connection.
    """
    sqlite: SQLite = field(
        default_factory = lambda: SQLite(),
        metadata = {
            "description": "SQLite database connection configuration",
            "default": lambda: SQLite().toDict()
        }
    )

    mysql: MySQL = field(
        default_factory = lambda: MySQL(),
        metadata = {
            "description": "MySQL database connection configuration",
            "default": lambda: MySQL().toDict()
        }
    )

    pgsql: PGSQL = field(
        default_factory = lambda: PGSQL(),
        metadata = {
            "description": "PostgreSQL database connection configuration",
            "default": lambda: PGSQL().toDict()
        }
    )

    oracle: Oracle = field(
        default_factory = lambda: Oracle(),
        metadata = {
            "description": "Oracle database connection configuration",
            "default": lambda: Oracle().toDict()
        }
    )

    def __post_init__(self):
        """
        Post-initialization method to validate the types of database connection attributes.
        Ensures that the attributes `sqlite`, `mysql`, `pgsql`, and `oracle` are instances of their respective classes.
        Raises:
            OrionisIntegrityException: If any attribute is not an instance of its expected class.
        """
        if not isinstance(self.sqlite, SQLite):
            raise OrionisIntegrityException(
                f"Invalid type for 'sqlite': expected 'Sqlite', got '{type(self.sqlite).__name__}'."
            )

        if not isinstance(self.mysql, MySQL):
            raise OrionisIntegrityException(
                f"Invalid type for 'mysql': expected 'Mysql', got '{type(self.mysql).__name__}'."
            )

        if not isinstance(self.pgsql, PGSQL):
            raise OrionisIntegrityException(
                f"Invalid type for 'pgsql': expected 'Pgsql', got '{type(self.pgsql).__name__}'."
            )

        if not isinstance(self.oracle, Oracle):
            raise OrionisIntegrityException(
                f"Invalid type for 'oracle': expected 'Oracle', got '{type(self.oracle).__name__}'."
            )