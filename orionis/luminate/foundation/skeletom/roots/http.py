from dataclasses import asdict, dataclass, field
from pathlib import Path
from orionis.luminate.foundation.skeletom.exceptions.integrity import SkeletomIntegrityException

@dataclass(frozen=True, kw_only=True)
class RootHttp:
    """
    Root configuration for HTTP controllers, middleware, and request validation paths.

    Attributes
    ----------
    path_controllers : str
        Path to the directory containing HTTP controller classes.
    path_middleware : str
        Path to the directory containing HTTP middleware classes.
    path_request : str
        Path to the directory containing HTTP request validation classes.
    """

    path_controllers: str = field(
        default='app/http/controllers',
        metadata={
            'description': 'Path to the directory containing HTTP controller classes.'
        }
    )

    path_middleware: str = field(
        default='app/http/middleware',
        metadata={
            'description': 'Path to the directory containing HTTP middleware classes.'
        }
    )

    path_request: str = field(
        default='app/http/requests',
        metadata={
            'description': 'Path to the directory containing HTTP request validation classes.'
        }
    )

    def __post_init__(self):
        """
        Validates the initialization of RootHttp fields.

        Ensures that all paths are strings and point to existing directories.

        Raises:
            SkeletomIntegrityException: If any validation fails.
        """
        for attr_name in ['path_controllers', 'path_middleware', 'path_request']:
            value = getattr(self, attr_name)
            if not isinstance(value, str):
                raise SkeletomIntegrityException(f"{attr_name} must be a string.")
            path = Path(value)
            if not path.exists() or not path.is_dir():
                raise SkeletomIntegrityException(
                    f"{attr_name} must exist and be a directory (got: {value})"
                )

    def getControllersPath(self) -> Path:
        """
        Returns the path to the controllers directory as a Path object.

        Returns:
            Path: The path to the controllers directory.
        """
        return Path(self.path_controllers)

    def getMiddlewarePath(self) -> Path:
        """
        Returns the path to the middleware directory as a Path object.

        Returns:
            Path: The path to the middleware directory.
        """
        return Path(self.path_middleware)

    def getRequestPath(self) -> Path:
        """
        Returns the path to the request validation directory as a Path object.

        Returns:
            Path: The path to the request validation directory.
        """
        return Path(self.path_request)

    def toDict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        Returns:
            dict: A dictionary representation of the Dataclass object.
        """
        return asdict(self)