from dataclasses import asdict, dataclass, field
from orionis.luminate.foundation.config.app.entities.app import App
from orionis.luminate.foundation.config.auth.entities.auth import Auth
from orionis.luminate.foundation.config.cache.entities.cache import Cache
from orionis.luminate.foundation.config.cors.entities.cors import Cors
from orionis.luminate.foundation.config.database.entities.database import Database
from orionis.luminate.foundation.config.exceptions.integrity import OrionisIntegrityException
from orionis.luminate.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.luminate.foundation.config.logging.entities.logging import Logging
from orionis.luminate.foundation.config.mail.entities.mail import Mail
from orionis.luminate.foundation.config.queue.entities.queue import Queue
from orionis.luminate.foundation.config.session.entities.session import Session
from orionis.luminate.foundation.config.testing.entities.testing import Testing

@dataclass
class Configuration:
    """
    Configuration class encapsulates all major configuration sections for the application.
    Attributes:
        app (App): Application configuration settings.
        auth (Auth): Authentication configuration settings.
        cache (Cache): Cache configuration settings.
        cors (Cors): CORS configuration settings.
        database (Database): Database configuration settings.
        filesystems (Filesystems): Filesystem configuration settings.
        logging (Logging): Logging configuration settings.
        mail (Mail): Mail configuration settings.
        queue (Queue): Queue configuration settings.
        session (Session): Session configuration settings.
        testing (Testing): Testing configuration settings.
    """

    app : App = field(
        default_factory=App,
        metadata={
            "description": "Application configuration settings."
        }
    )

    auth : Auth = field(
        default_factory=Auth,
        metadata={
            "description": "Authentication configuration settings."
        }
    )

    cache : Cache = field(
        default_factory=Cache,
        metadata={
            "description": "Cache configuration settings."
        }
    )

    cors : Cors = field(
        default_factory=Cors,
        metadata={
            "description": "CORS configuration settings."
        }
    )

    database : Database = field(
        default_factory=Database,
        metadata={
            "description": "Database configuration settings."
        }
    )

    filesystems : Filesystems = field(
        default_factory=Filesystems,
        metadata={
            "description": "Filesystem configuration settings."
        }
    )

    logging : Logging = field(
        default_factory=Logging,
        metadata={
            "description": "Logging configuration settings."
        }
    )

    mail : Mail = field(
        default_factory=Mail,
        metadata={
            "description": "Mail configuration settings."
        }
    )

    queue : Queue = field(
        default_factory=Queue,
        metadata={
            "description": "Queue configuration settings."
        }
    )

    session : Session = field(
        default_factory=Session,
        metadata={
            "description": "Session configuration settings."
        }
    )

    testing : Testing = field(
        default_factory=Testing,
        metadata={
            "description": "Testing configuration settings."
        }
    )

    def __post_init__(self):
        """
        Post-initialization method to ensure integrity of configuration sections.
        Raises:
            OrionisIntegrityException: If any configuration section is not of the expected type.
        """
        if not isinstance(self.app, App):
            raise OrionisIntegrityException("app must be an instance of App")
        if not isinstance(self.auth, Auth):
            raise OrionisIntegrityException("auth must be an instance of Auth")
        if not isinstance(self.cache, Cache):
            raise OrionisIntegrityException("cache must be an instance of Cache")
        if not isinstance(self.cors, Cors):
            raise OrionisIntegrityException("cors must be an instance of Cors")
        if not isinstance(self.database, Database):
            raise OrionisIntegrityException("database must be an instance of Database")
        if not isinstance(self.filesystems, Filesystems):
            raise OrionisIntegrityException("filesystems must be an instance of Filesystems")
        if not isinstance(self.logging, Logging):
            raise OrionisIntegrityException("logging must be an instance of Logging")
        if not isinstance(self.mail, Mail):
            raise OrionisIntegrityException("mail must be an instance of Mail")
        if not isinstance(self.queue, Queue):
            raise OrionisIntegrityException("queue must be an instance of Queue")
        if not isinstance(self.session, Session):
            raise OrionisIntegrityException("session must be an instance of Session")
        if not isinstance(self.testing, Testing):
            raise OrionisIntegrityException("testing must be an instance of Testing")

    def toDict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        Returns:
            dict: A dictionary representation of the Dataclass object.
        """
        return asdict(self)