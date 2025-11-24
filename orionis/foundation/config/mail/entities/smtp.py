from dataclasses import dataclass, field
from typing import Optional
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.support.entities.base import BaseEntity
from orionis.services.environment.env import Env

@dataclass(unsafe_hash=True, kw_only=True)
class Smtp(BaseEntity):
    """
    Smtp dataclass representing SMTP configuration settings.
    Parameters
    ----------
    url : str
        The full URL for the SMTP service. Default is obtained from the environment variable 'MAIL_URL'.
    host : str
        The hostname of the SMTP server. Default is obtained from 'MAIL_HOST'.
    port : int
        The port number used for SMTP communication. Default is obtained from 'MAIL_PORT' or 587.
    encryption : str
        The encryption type used for secure communication. Default is obtained from 'MAIL_ENCRYPTION' or 'TLS'.
    username : str
        The username for authentication with the SMTP server. Default is obtained from 'MAIL_USERNAME'.
    password : str
        The password for authentication with the SMTP server. Default is obtained from 'MAIL_PASSWORD'.
    timeout : Optional[int], default=None
        The connection timeout duration in seconds. Default is None.
    Raises
    ------
    OrionisIntegrityException
        If any of the attributes do not meet their type or value requirements.
    """

    url: str = field(
        default_factory=lambda: Env.get('MAIL_URL', ''),
        metadata={
            "description": "The full URL for the SMTP service.",
            "default": Env.get('MAIL_URL')
        }
    )

    host: str = field(
        default_factory=lambda: Env.get('MAIL_HOST', ''),
        metadata={
            "description": "The hostname of the SMTP server.",
            "default": Env.get('MAIL_HOST', '')
        }
    )

    port: int = field(
        default_factory=lambda: Env.get('MAIL_PORT', 587),
        metadata={
            "description": "The port number used for SMTP communication.",
            "default": Env.get('MAIL_PORT', 587)
        }
    )

    encryption: str = field(
        default_factory=lambda: Env.get('MAIL_ENCRYPTION', 'TLS'),
        metadata={
            "description": "The encryption type used for secure communication.",
            "default": Env.get('MAIL_ENCRYPTION', 'TLS')
        }
    )

    username: str = field(
        default_factory=lambda: Env.get('MAIL_USERNAME', ''),
        metadata={
            "description": "The username for authentication with the SMTP server.",
            "default": Env.get('MAIL_USERNAME')
        }
    )

    password: str = field(
        default_factory=lambda: Env.get('MAIL_PASSWORD', ''),
        metadata={
            "description": "The password for authentication with the SMTP server.",
            "default": Env.get('MAIL_PASSWORD')
        }
    )

    timeout: Optional[int] = field(
        default=None,
        metadata={
            "description": "The connection timeout duration in seconds.",
            "default": None
        }
    )

    def __post_init__(self):
        """
        Validates the initialization of SMTP configuration attributes.

        Parameters
        ----------
        None

        Raises
        ------
        OrionisIntegrityException
            If any of the following conditions are met:
                - 'url' is not a string.
                - 'host' is not a string.
                - 'port' is not a non-negative integer.
                - 'encryption' is not a string.
                - 'username' is not a string.
                - 'password' is not a string.
                - 'timeout' is not None and is not a non-negative integer.
        """
        if not isinstance(self.url, str):
            raise OrionisIntegrityException("The 'url' attribute must be a string.")
        if not isinstance(self.host, str):
            raise OrionisIntegrityException("The 'host' attribute must be a string.")
        if not isinstance(self.port, int) or self.port < 0:
            raise OrionisIntegrityException("The 'port' attribute must be a non-negative integer.")
        if not isinstance(self.encryption, str):
            raise OrionisIntegrityException("The 'encryption' attribute must be a string.")
        if not isinstance(self.username, str):
            raise OrionisIntegrityException("The 'username' attribute must be a string.")
        if not isinstance(self.password, str):
            raise OrionisIntegrityException("The 'password' attribute must be a string.")
        if self.timeout is not None and (not isinstance(self.timeout, int) or self.timeout < 0):
            raise OrionisIntegrityException("The 'timeout' attribute must be a non-negative integer or None.")
