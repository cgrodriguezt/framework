from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.auth.entities.auth import Auth
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.http.entitites.http import HTTP
from orionis.foundation.config.database.entities.database import Database
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.queue.entities.queue import Queue
from orionis.foundation.config.session.entities.session import Session
from orionis.foundation.config.testing.entities.testing import Testing
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Configuration(BaseEntity):
    """
    Represent the main configuration for Orionis Framework startup.

    Parameters
    ----------
    app : App | dict, optional
        Application configuration settings.
    auth : Auth | dict, optional
        Authentication configuration settings.
    cache : Cache | dict, optional
        Cache configuration settings.
    database : Database | dict, optional
        Database configuration settings.
    filesystems : Filesystems | dict, optional
        Filesystem configuration settings.
    logging : Logging | dict, optional
        Logging configuration settings.
    mail : Mail | dict, optional
        Mail configuration settings.
    http : HTTP | dict, optional
        HTTP configuration settings.
    queue : Queue | dict, optional
        Queue configuration settings.
    session : Session | dict, optional
        Session configuration settings.
    testing : Testing | dict, optional
        Testing configuration settings.

    Raises
    ------
    TypeError
        If any configuration section is initialized with an invalid type.

    Returns
    -------
    None
        This class does not return a value upon instantiation.
    """

    # ruff: noqa: PLW0108

    app: App | dict = field(
        default_factory=lambda: App(),
        metadata={
            "description": "Application configuration settings.",
            "default": lambda: App().toDict(),
        },
    )

    auth: Auth | dict = field(
        default_factory=lambda: Auth(),
        metadata={
            "description": "Authentication configuration settings.",
            "default": lambda: Auth().toDict(),
        },
    )

    cache: Cache | dict = field(
        default_factory=lambda: Cache(),
        metadata={
            "description": "Cache configuration settings.",
            "default": lambda: Cache().toDict(),
        },
    )

    database: Database | dict = field(
        default_factory=lambda: Database(),
        metadata={
            "description": "Database configuration settings.",
            "default": lambda: Database().toDict(),
        },
    )

    filesystems: Filesystems | dict = field(
        default_factory=lambda: Filesystems(),
        metadata={
            "description": "Filesystem configuration settings.",
            "default": lambda: Filesystems().toDict(),
        },
    )

    http: HTTP | dict = field(
        default_factory=lambda: HTTP(),
        metadata={
            "description": "HTTP configuration settings.",
            "default": lambda: HTTP().toDict(),
        },
    )

    logging: Logging | dict = field(
        default_factory=lambda: Logging(),
        metadata={
            "description": "Logging configuration settings.",
            "default": lambda: Logging().toDict(),
        },
    )

    mail: Mail | dict = field(
        default_factory=lambda: Mail(),
        metadata={
            "description": "Mail configuration settings.",
            "default": lambda: Mail().toDict(),
        },
    )

    queue: Queue | dict = field(
        default_factory=lambda: Queue(),
        metadata={
            "description": "Queue configuration settings.",
            "default": lambda: Queue().toDict(),
        },
    )

    session: Session | dict = field(
        default_factory=lambda: Session(),
        metadata={
            "description": "Session configuration settings.",
            "default": lambda: Session().toDict(),
        },
    )

    testing: Testing | dict = field(
        default_factory=lambda: Testing(),
        metadata={
            "description": "Testing configuration settings.",
            "default": lambda: Testing().toDict(),
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and convert configuration attributes to their entity types.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Call parent post-init for base validation
        super().__post_init__()
        # Validate each configuration section
        self.__validateApp()
        self.__validateAuth()
        self.__validateCache()
        self.__validateDatabase()
        self.__validateFilesystems()
        self.__validateHttp()
        self.__validateLogging()
        self.__validateMail()
        self.__validateQueue()
        self.__validateSession()
        self.__validateTesting()

    def __validateApp(self) -> None:
        """
        Validate the 'app' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.app, (App, dict)):
            error_msg = (
                f"Invalid type for 'app': expected App or dict, "
                f"got {type(self.app).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to App instance if necessary
        if isinstance(self.app, dict):
            object.__setattr__(self, "app", App(**self.app))

    def __validateAuth(self) -> None:
        """
        Validate the 'auth' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.auth, (Auth, dict)):
            error_msg = (
                f"Invalid type for 'auth': expected Auth or dict, "
                f"got {type(self.auth).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to Auth instance if necessary
        if isinstance(self.auth, dict):
            object.__setattr__(self, "auth", Auth(**self.auth))

    def __validateCache(self) -> None:
        """
        Validate the 'cache' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.cache, (Cache, dict)):
            error_msg = (
                f"Invalid type for 'cache': expected Cache or dict, "
                f"got {type(self.cache).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to Cache instance if necessary
        if isinstance(self.cache, dict):
            object.__setattr__(self, "cache", Cache(**self.cache))

    def __validateHttp(self) -> None:
        """
        Validate the 'http' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.http, (HTTP, dict)):
            error_msg = (
                f"Invalid type for 'http': expected HTTP or dict, "
                f"got {type(self.http).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to HTTP instance if necessary
        if isinstance(self.http, dict):
            object.__setattr__(self, "http", HTTP(**self.http))

    def __validateDatabase(self) -> None:
        """
        Validate the 'database' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.database, (Database, dict)):
            error_msg = (
                f"Invalid type for 'database': expected Database or dict, "
                f"got {type(self.database).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to Database instance if necessary
        if isinstance(self.database, dict):
            object.__setattr__(self, "database", Database(**self.database))

    def __validateFilesystems(self) -> None:
        """
        Validate the 'filesystems' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.filesystems, (Filesystems, dict)):
            error_msg = (
                f"Invalid type for 'filesystems': expected Filesystems or dict, "
                f"got {type(self.filesystems).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to Filesystems instance if necessary
        if isinstance(self.filesystems, dict):
            object.__setattr__(self, "filesystems", Filesystems(**self.filesystems))

    def __validateLogging(self) -> None:
        """
        Validate the 'logging' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.logging, (Logging, dict)):
            error_msg = (
                f"Invalid type for 'logging': expected Logging or dict, "
                f"got {type(self.logging).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to Logging instance if necessary
        if isinstance(self.logging, dict):
            object.__setattr__(self, "logging", Logging(**self.logging))

    def __validateMail(self) -> None:
        """
        Validate the 'mail' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.mail, (Mail, dict)):
            error_msg = (
                f"Invalid type for 'mail': expected Mail or dict, "
                f"got {type(self.mail).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to Mail instance if necessary
        if isinstance(self.mail, dict):
            object.__setattr__(self, "mail", Mail(**self.mail))

    def __validateQueue(self) -> None:
        """
        Validate the 'queue' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.queue, (Queue, dict)):
            error_msg = (
                f"Invalid type for 'queue': expected Queue or dict, "
                f"got {type(self.queue).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to Queue instance if necessary
        if isinstance(self.queue, dict):
            object.__setattr__(self, "queue", Queue(**self.queue))

    def __validateSession(self) -> None:
        """
        Validate the 'session' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.session, (Session, dict)):
            error_msg = (
                f"Invalid type for 'session': expected Session or dict, "
                f"got {type(self.session).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to Session instance if necessary
        if isinstance(self.session, dict):
            object.__setattr__(self, "session", Session(**self.session))

    def __validateTesting(self) -> None:
        """
        Validate the 'testing' configuration attribute type and convert if needed.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.testing, (Testing, dict)):
            error_msg = (
                f"Invalid type for 'testing': expected Testing or dict, "
                f"got {type(self.testing).__name__}"
            )
            raise TypeError(error_msg)
        # Convert dict to Testing instance if necessary
        if isinstance(self.testing, dict):
            object.__setattr__(self, "testing", Testing(**self.testing))
