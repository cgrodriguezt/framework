from __future__ import annotations
from dataclasses import dataclass, field, fields
from pathlib import Path
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Paths(BaseEntity):
    """
    Represent canonical filesystem paths for core directories and files.

    The `Paths` class provides strongly-typed, validated, and normalized access to
    all major directories and files used by the application, such as the root, app,
    config, storage, resources, and more. Each attribute corresponds to a specific
    directory or file path, with sensible defaults based on the current working
    directory. All paths are stored as strings and validated upon initialization.

    Attributes
    ----------
    root : str
        The root directory of the application.
    app : str
        The main application directory containing core code.
    console : str
        Directory containing subfolders for console commands and scheduler.py.
    exceptions : str
        Directory containing exception handler classes.
    http : str
        Directory containing HTTP-related classes (controllers, middleware, requests).
    models : str
        Directory containing ORM model classes.
    providers : str
        Directory containing service provider classes.
    notifications : str
        Directory containing notification classes.
    services : str
        Directory containing business logic service classes.
    jobs : str
        Directory containing queued job classes.
    bootstrap : str
        Directory containing application bootstrap files.
    config : str
        Directory containing application configuration files.
    database : str
        Directory containing the SQLite database file.
    resources : str
        Directory containing application resources (views, lang, assets).
    routes : str
        Path to the web routes definition file.
    storage : str
        Directory for application storage files.
    tests : str
        Directory containing test files.
    """

    root: str = field(
        default_factory=lambda: str(Path.cwd().resolve()),
        metadata={
            "description": "The root directory of the application.",
            "default": lambda: str(Path.cwd().resolve()),
        },
    )

    app: str = field(
        default_factory=lambda: str((Path.cwd() / "app").resolve()),
        metadata={
            "description": "The main application directory containing core code.",
            "default": lambda: str((Path.cwd() / "app").resolve()),
        },
    )

    console: str = field(
        default_factory=lambda: str((Path.cwd() / "app" / "console").resolve()),
        metadata={
            "description": (
                "Directory containing subfolders for console commands and scheduler.py."
            ),
            "default": lambda: str((Path.cwd() / "app" / "console").resolve()),
        },
    )

    exceptions: str = field(
        default_factory=lambda: str((Path.cwd() / "app" / "exceptions").resolve()),
        metadata={
            "description": "Directory containing exception handler classes.",
            "default": lambda: str((Path.cwd() / "app" / "exceptions").resolve()),
        },
    )

    http: str = field(
        default_factory=lambda: str((Path.cwd() / "app" / "http").resolve()),
        metadata={
            "description": (
                "Directory containing HTTP-related classes (controllers, middleware, "
                "requests)."
            ),
            "default": lambda: str((Path.cwd() / "app" / "http").resolve()),
        },
    )

    models: str = field(
        default_factory=lambda: str((Path.cwd() / "app" / "models").resolve()),
        metadata={
            "description": "Directory containing ORM model classes.",
            "default": lambda: str((Path.cwd() / "app" / "models").resolve()),
        },
    )

    providers: str = field(
        default_factory=lambda: str((Path.cwd() / "app" / "providers").resolve()),
        metadata={
            "description": "Directory containing service provider classes.",
            "default": lambda: str((Path.cwd() / "app" / "providers").resolve()),
        },
    )

    notifications: str = field(
        default_factory=lambda: str((Path.cwd() / "app" / "notifications").resolve()),
        metadata={
            "description": "Directory containing notification classes.",
            "default": lambda: str((Path.cwd() / "app" / "notifications").resolve()),
        },
    )

    services: str = field(
        default_factory=lambda: str((Path.cwd() / "app" / "services").resolve()),
        metadata={
            "description": "Directory containing business logic service classes.",
            "default": lambda: str((Path.cwd() / "app" / "services").resolve()),
        },
    )

    jobs: str = field(
        default_factory=lambda: str((Path.cwd() / "app" / "jobs").resolve()),
        metadata={
            "description": "Directory containing queued job classes.",
            "default": lambda: str((Path.cwd() / "app" / "jobs").resolve()),
        },
    )

    bootstrap: str = field(
        default_factory=lambda: str((Path.cwd() / "bootstrap").resolve()),
        metadata={
            "description": "Directory containing application bootstrap files.",
            "default": lambda: str((Path.cwd() / "bootstrap").resolve()),
        },
    )

    config: str = field(
        default_factory=lambda: str((Path.cwd() / "config").resolve()),
        metadata={
            "description": "Directory containing application configuration files.",
            "default": lambda: str((Path.cwd() / "config").resolve()),
        },
    )

    database: str = field(
        default_factory=lambda: str((Path.cwd() / "database" / "database").resolve()),
        metadata={
            "description": "Directory containing the SQLite database file.",
            "default": lambda: str((Path.cwd() / "database" / "database").resolve()),
        },
    )

    resources: str = field(
        default_factory=lambda: str((Path.cwd() / "resources").resolve()),
        metadata={
            "description": (
                "Directory containing application resources (views, lang, assets)."
            ),
            "default": lambda: str((Path.cwd() / "resources").resolve()),
        },
    )

    routes: str = field(
        default_factory=lambda: str((Path.cwd() / "routes").resolve()),
        metadata={
            "description": "Path to the web routes definition file.",
            "default": lambda: str((Path.cwd() / "routes").resolve()),
        },
    )

    storage: str = field(
        default_factory=lambda: str((Path.cwd() / "storage").resolve()),
        metadata={
            "description": "Directory for application storage files.",
            "default": lambda: str((Path.cwd() / "storage").resolve()),
        },
    )

    tests: str = field(
        default_factory=lambda: str((Path.cwd() / "tests").resolve()),
        metadata={
            "description": "Directory containing test files.",
            "default": lambda: str((Path.cwd() / "tests").resolve()),
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize path attributes after initialization.

        Ensures all path-related attributes are stored as strings. Converts any
        `pathlib.Path` attributes to strings and raises an exception if any
        attribute cannot be converted to a string.

        Parameters
        ----------
        self : Paths
            Instance of the Paths dataclass.

        Returns
        -------
        None
            This method does not return a value. It only validates and normalizes
            attributes in place.
        """
        # Call the parent class's __post_init__ if it exists
        super().__post_init__()

        try:
            # Iterate over all dataclass fields to validate and normalize their values
            for field_ in fields(self):
                value = getattr(self, field_.name)
                # Convert Path objects to strings
                if isinstance(value, Path):
                    object.__setattr__(self, field_.name, str(value))
                    value = str(value)
                # Raise an exception if the value is not a string
                if not isinstance(value, str):
                    error_msg = (
                        f"Invalid type for '{field_.name}': expected str, "
                        f"got {type(value).__name__}"
                    )
                    raise TypeError(error_msg)
        except Exception as e:
            # Wrap and re-raise any exception as a ValueError
            error_msg = (
                f"Error during Paths post-initialization: {e!s}"
            )
            raise ValueError(error_msg) from e
