from dataclasses import dataclass, field
from orionis.luminate.config.app.enums.ciphers import Cipher
from orionis.luminate.config.app.enums.environments import Environments
from orionis.luminate.config.exceptions.integrity_exception import OrionisIntegrityException
from orionis.luminate.services.environment.env import Env
from orionis.luminate.services.workers.maximum_workers import MaximumWorkers

@dataclass(unsafe_hash=True, kw_only=True)
class App:
    """
    Represents the configuration settings for the application.
    Attributes:
        name (str): The name of the application. Defaults to 'Orionis Application'.
        env (Environments): The environment in which the application is running. Defaults to 'DEVELOPMENT'.
        debug (bool): Flag indicating whether debug mode is enabled. Defaults to True.
        url (str): The base URL of the application. Defaults to 'http://127.0.0.1'.
        port (int): The port on which the application will run. Defaults to 8000.
        workers (int): The number of worker processes to handle requests. Defaults to the maximum available workers.
        reload (bool): Flag indicating whether the application should reload on code changes. Defaults to True.
        timezone (str): The timezone of the application. Defaults to 'UTC'.
        locale (str): The locale for the application. Defaults to 'en'.
        fallback_locale (str): The fallback locale for the application. Defaults to 'en'.
        cipher (Cipher): The cipher used for encryption. Defaults to 'AES_256_CBC'.
        key (str or None): The encryption key for the application. Defaults to None.
        maintenance (Maintenance): The maintenance configuration for the application. Defaults to '/maintenance'.
    Methods:
        __post_init__():
    """

    name: str = field(
        default_factory=lambda: Env.get('APP_NAME', 'Orionis Application'),
        metadata={
            "description": "The name of the application. Defaults to 'Orionis Application'.",
            "required": True,
            "default": "Orionis Application"
        }
    )

    env: Environments = field(
        default_factory=lambda: Env.get('APP_ENV', Environments.DEVELOPMENT),
        metadata={
            "description": "The environment in which the application is running. Defaults to 'DEVELOPMENT'.",
            "required": True,
            "default": "Environments.DEVELOPMENT"
        }
    )

    debug: bool = field(
        default_factory=lambda: Env.get('APP_DEBUG', True),
        metadata={
            "description": "Flag indicating whether debug mode is enabled. Defaults to False.",
            "required": True,
            "default": True
        }
    )

    url: str = field(
        default_factory=lambda: Env.get('APP_URL', 'http://127.0.0.1'),
        metadata={
            "description": "The base URL of the application. Defaults to 'http://127.0.0.1'.",
            "required": True,
            "default": "http://127.0.0.1"
        }
    )

    port: int = field(
        default_factory=lambda: Env.get('APP_PORT', 8000),
        metadata={
            "description": "The port on which the application will run. Defaults to 8000.",
            "required": True,
            "default": 8000
        }
    )

    workers: int = field(
        default_factory=lambda: Env.get('APP_WORKERS', MaximumWorkers().calculate()),
        metadata={
            "description": "The number of worker processes to handle requests. Defaults to the maximum available workers.",
            "required": True,
            "default": "MaximumWorkers.calculate()"
        }
    )

    reload: bool = field(
        default_factory=lambda: Env.get('APP_RELOAD', True),
        metadata={
            "description": "Flag indicating whether the application should reload on code changes. Defaults to True.",
            "required": True,
            "default": True
        }
    )

    timezone: str = field(
        default_factory=lambda: Env.get('APP_TIMEZONE', 'UTC'),
        metadata={
            "description": "The timezone of the application. Defaults to 'UTC'.",
            "required": True,
            "default": "UTC"
        }
    )

    locale: str = field(
        default_factory=lambda: Env.get('APP_LOCALE', 'en'),
        metadata={
            "description": "The locale for the application. Defaults to 'en'.",
            "required": True,
            "default": "en"
        }
    )

    fallback_locale: str = field(
        default_factory=lambda: Env.get('APP_FALLBACK_LOCALE', 'en'),
        metadata={
            "description": "The fallback locale for the application. Defaults to 'en'.",
            "required": True,
            "default": "en"
        }
    )

    cipher: str = field(
        default_factory=lambda: Env.get('APP_CIPHER', Cipher.AES_256_CBC),
        metadata={
            "description": "The cipher used for encryption. Defaults to 'AES_256_CBC'.",
            "required": True,
            "default": "Cipher.AES_256_CBC"
        }
    )

    key: str = field(
        default_factory=lambda: Env.get('APP_KEY'),
        metadata={
            "description": "The encryption key for the application. Defaults to None.",
            "required": False,
            "default": None
        }
    )

    maintenance: str = field(
        default_factory=lambda: Env.get('APP_MAINTENANCE', '/maintenance'),
        metadata={
            "description": "The maintenance configuration for the application. Defaults to '/maintenance'.",
            "required": True,
            "default": "/maintenance"
        }
    )

    def __post_init__(self):
        """
        Validates and normalizes the attributes after dataclass initialization.

        Ensures that all fields have the correct types and values, raising TypeError
        if any field is invalid. This helps catch configuration errors early.
        """
        if not isinstance(self.name, str) or not self.name.strip():
            raise OrionisIntegrityException("The 'name' attribute must be a non-empty string of type str.")

        if not isinstance(self.env, Environments):
            if isinstance(self.env, str):
                value = str(self.env).strip().upper()
                if value in Environments._member_names_:
                    self.env = getattr(Environments, value)
                else:
                    raise OrionisIntegrityException(f"Invalid environment value: {self.env}. Must be one of {Environments._member_names_}.")
            else:
                raise OrionisIntegrityException("The 'env' attribute must be of type Environments.")

        if not isinstance(self.debug, bool):
            raise OrionisIntegrityException("The 'debug' attribute must be a boolean.")

        if not isinstance(self.url, str) or not self.url.strip():
            raise OrionisIntegrityException("The 'url' attribute must be a non-empty string.")

        if not isinstance(self.port, int):
            raise OrionisIntegrityException("The 'port' attribute must be an integer.")

        if not isinstance(self.workers, int):
            raise OrionisIntegrityException("The 'workers' attribute must be an integer.")

        if not isinstance(self.reload, bool):
            raise OrionisIntegrityException("The 'reload' attribute must be a boolean.")

        if not isinstance(self.timezone, str) or not self.timezone.strip():
            raise OrionisIntegrityException("The 'timezone' attribute must be a non-empty string.")

        if not isinstance(self.locale, str) or not self.locale.strip():
            raise OrionisIntegrityException("The 'locale' attribute must be a non-empty string.")

        if not isinstance(self.fallback_locale, str) or not self.fallback_locale.strip():
            raise OrionisIntegrityException("The 'fallback_locale' attribute must be a non-empty string.")

        if not isinstance(self.cipher, Cipher):
            if isinstance(self.cipher, str):
                value = str(self.cipher).strip().upper()
                if value in Cipher._member_names_:
                    self.cipher = getattr(Cipher, value)
                else:
                    raise OrionisIntegrityException(f"Invalid cipher value: {self.cipher}. Must be one of {Cipher._member_names_}.")
            else:
                raise OrionisIntegrityException("The 'cipher' attribute must be of type Cipher.")

        if self.key is not None and not isinstance(self.key, str):
            raise OrionisIntegrityException("The 'key' attribute must be a string or None.")

        if not isinstance(self.maintenance, str):
            raise OrionisIntegrityException("The 'maintenance' attribute must be a string (A Route).")
