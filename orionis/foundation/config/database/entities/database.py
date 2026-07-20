from __future__ import annotations
from dataclasses import dataclass, field, fields
from orionis.foundation.config.database.entities.connections import Connections
from orionis.environment.env import Env
from orionis.support.entities.base import BaseEntity

# Pre-computed connection option names
_CONNECTION_OPTIONS: frozenset[str] = frozenset(f.name for f in fields(Connections))

@dataclass(frozen=True, kw_only=True)
class Database(BaseEntity):
    """
    Represent the general database configuration.

    Attributes
    ----------
    default : str
        The name of the default database connection to use.
    connections : Connections or dict
        The different database connections available to the application.
    """

    default: str = field(
        default_factory=lambda: Env.get("DB_CONNECTION", "sqlite"),
        metadata={
            "description": "Default database connection name",
            "default": "sqlite",
        },
    )

    connections: Connections | dict = field(
        default_factory=Connections,
        metadata={
            "description": "Database connections",
            "default": lambda: Connections().toDict(),
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the 'default' and 'connections' attributes.

        Validates that the 'default' attribute is a valid string corresponding to a
        member of Connections. Ensures that the 'connections' attribute is an instance
        of Connections or a non-empty dictionary. Raises an exception if validation
        fails.

        Parameters
        ----------
        self : Database
            The instance of the Database class.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__post_init__()

        # Validate 'default' against pre-cached connection field names
        if isinstance(self.default, str):
            if self.default not in _CONNECTION_OPTIONS:
                error_msg = (
                    "The 'default' attribute must be one of "
                    f"{sorted(_CONNECTION_OPTIONS)!s}."
                )
                raise ValueError(error_msg)
        else:
            error_msg = (
                f"The 'default' attribute cannot be empty. Options are: "
                f"{sorted(_CONNECTION_OPTIONS)!s}"
            )
            raise TypeError(error_msg)

        # Validate the 'connections' attribute
        if not self.connections or not isinstance(
            self.connections, (Connections, dict),
        ):
            error_msg = (
                "The 'connections' attribute must be an instance of Connections or a "
                "non-empty dictionary."
            )
            raise TypeError(error_msg)
        # Convert dict to Connections if necessary
        if isinstance(self.connections, dict):
            object.__setattr__(self, "connections", Connections(**self.connections))
