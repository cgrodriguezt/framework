from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Type
from orionis.luminate.foundation.skeletom.roots.console import RootConsole
from orionis.luminate.foundation.skeletom.roots.http import RootHttp
from orionis.luminate.foundation.skeletom.exceptions.integrity import SkeletomIntegrityException

@dataclass(frozen=True, kw_only=True)
class SkeletomConfig:
    """
    Configuration for the Skeletom framework components and application structure.

    Attributes
    ----------
    console : RootConsole
        Console configuration for logging and command registration.
    http : RootHttp
        HTTP server configuration.
    exceptions : str
        Directory where exception classes are stored.
    models : str
        Directory where model classes are stored.
    providers : str
        Directory where provider classes are stored.
    services : str
        Directory where service classes are stored.
    notifications : str
        Directory where notification classes are stored.
    """

    console: RootConsole = field(
        default_factory=RootConsole,
        metadata={
            "description": "Console configuration for logging and command registration."
        }
    )

    http: RootHttp = field(
        default_factory=RootHttp,
        metadata={
            "description": "HTTP server configuration."
        }
    )

    exceptions: str = field(
        default="app/exceptions",
        metadata={
            "description": "Directory where exception classes are stored."
        }
    )

    models: str = field(
        default="app/models",
        metadata={
            "description": "Directory where model classes are stored."
        }
    )

    providers: str = field(
        default="app/providers",
        metadata={
            "description": "Directory where provider classes are stored."
        }
    )

    services: str = field(
        default="app/services",
        metadata={
            "description": "Directory where service classes are stored."
        }
    )

    notifications: str = field(
        default="app/notifications",
        metadata={
            "description": "Directory where notification classes are stored."
        }
    )

    def __post_init__(self):
        # Validate all string paths
        for attr in ['exceptions', 'models', 'providers', 'services', 'notifications']:
            value = getattr(self, attr)
            if not isinstance(value, str):
                raise SkeletomIntegrityException(f"{attr} must be a string (got: {type(value).__name__})")

        # Validate console type
        if not isinstance(self.console, RootConsole):
            raise SkeletomIntegrityException("console must be an instance of RootConsole.")

        # Validate http type
        if not isinstance(self.http, RootHttp):
            raise SkeletomIntegrityException("http must be an instance of RootHttp.")

    def toDict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        Returns:
            dict: A dictionary representation of the Dataclass object.
        """
        return asdict(self)