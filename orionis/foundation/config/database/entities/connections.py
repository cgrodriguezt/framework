from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.database.entities.mysql import MySQL
from orionis.foundation.config.database.entities.oracle import Oracle
from orionis.foundation.config.database.entities.pgsql import PGSQL
from orionis.foundation.config.database.entities.sqlite import SQLite
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Connections(BaseEntity):
    """
    Represent all database connections used by the application.

    Attributes
    ----------
    sqlite : SQLite | dict
        Configuration for the SQLite database connection.
    mysql : MySQL | dict
        Configuration for the MySQL database connection.
    pgsql : PGSQL | dict
        Configuration for the PostgreSQL database connection.
    oracle : Oracle | dict
        Configuration for the Oracle database connection.
    """

    sqlite: SQLite | dict = field(
        default_factory=lambda: SQLite(),
        metadata={
            "description": "SQLite database connection configuration",
            "default": lambda: SQLite().toDict(),
        },
    )

    mysql: MySQL | dict = field(
        default_factory=lambda: MySQL(),
        metadata={
            "description": "MySQL database connection configuration",
            "default": lambda: MySQL().toDict(),
        },
    )

    pgsql: PGSQL | dict = field(
        default_factory=lambda: PGSQL(),
        metadata={
            "description": "PostgreSQL database connection configuration",
            "default": lambda: PGSQL().toDict(),
        },
    )

    oracle: Oracle | dict = field(
        default_factory=lambda: Oracle(),
        metadata={
            "description": "Oracle database connection configuration",
            "default": lambda: Oracle().toDict(),
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and convert database connection attributes after initialization.

        Ensures that the attributes `sqlite`, `mysql`, `pgsql`, and `oracle`
        are instances of their respective classes. Converts from dict if needed.

        Raises
        ------
        TypeError
            If any attribute is not an instance of its expected class or dict.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__post_init__()

        # Validate and convert `sqlite` attribute
        if not isinstance(self.sqlite, (SQLite, dict)):
            error_msg = (
                "Invalid type for 'sqlite': expected 'SQLite' or 'dict', got "
                f"'{type(self.sqlite).__name__}'."
            )
            raise TypeError(error_msg)
        if isinstance(self.sqlite, dict):
            # Convert dict to SQLite instance
            object.__setattr__(self, "sqlite", SQLite(**self.sqlite))

        # Validate and convert `mysql` attribute
        if not isinstance(self.mysql, (MySQL, dict)):
            error_msg = (
                "Invalid type for 'mysql': expected 'MySQL' or 'dict', got "
                f"'{type(self.mysql).__name__}'."
            )
            raise TypeError(error_msg)
        if isinstance(self.mysql, dict):
            # Convert dict to MySQL instance
            object.__setattr__(self, "mysql", MySQL(**self.mysql))

        # Validate and convert `pgsql` attribute
        if not isinstance(self.pgsql, (PGSQL, dict)):
            error_msg = (
                "Invalid type for 'pgsql': expected 'PGSQL' or 'dict', got "
                f"'{type(self.pgsql).__name__}'."
            )
            raise TypeError(error_msg)
        if isinstance(self.pgsql, dict):
            # Convert dict to PGSQL instance
            object.__setattr__(self, "pgsql", PGSQL(**self.pgsql))

        # Validate and convert `oracle` attribute
        if not isinstance(self.oracle, (Oracle, dict)):
            error_msg = (
                "Invalid type for 'oracle': expected 'Oracle' or 'dict', got "
                f"'{type(self.oracle).__name__}'."
            )
            raise TypeError(error_msg)
        if isinstance(self.oracle, dict):
            # Convert dict to Oracle instance
            object.__setattr__(self, "oracle", Oracle(**self.oracle))
