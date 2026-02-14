from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.app.enums import Cipher, Environments
from orionis.services.environment.env import Env
from orionis.services.environment.key.key_generator import SecureKeyGenerator
from orionis.services.system.workers import Workers
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class App(BaseEntity):
    """
    Represent application configuration settings.

    Parameters
    ----------
    name : str, optional
        The name of the application. Default is 'Orionis Application'.
    env : str | Environments, optional
        The environment in which the application is running. Default is
        'DEVELOPMENT'.
    debug : bool, optional
        Whether debug mode is enabled. Default is True.
    host : str, optional
        The host address of the application.
    port : int, optional
        The port on which the application will run. Default is 8000.
    workers : int, optional
        Number of worker processes to handle requests. Default is 1.
    reload : bool, optional
        Whether the application should reload on code changes. Default is True.
    timezone : str, optional
        The timezone of the application. Default is 'UTC'.
    locale : str, optional
        The locale for the application. Default is 'en'.
    fallback_locale : str, optional
        The fallback locale for the application. Default is 'en'.
    cipher : str | Cipher, optional
        The cipher used for encryption. Default is 'AES_256_CBC'.
    key : str | None, optional
        The encryption key for the application. Default is None.
    maintenance : str, optional
        The maintenance route for the application. Default is '/maintenance'.
    """

    # ruff: noqa: PLR0912, PLR0915, C901

    name: str = field(
        default_factory=lambda: Env.get("APP_NAME", "Orionis Application"),
        metadata={
            "description": "The name of the application. Defaults to "
            "'Orionis Application'.",
            "default": "Orionis Application",
        },
    )

    env: str | Environments = field(
        default_factory=lambda: Env.get("APP_ENV", Environments.DEVELOPMENT.value),
        metadata={
            "description": "The environment in which the application is running. "
            "Defaults to 'DEVELOPMENT'.",
            "default": Environments.DEVELOPMENT.value,
        },
    )

    debug: bool = field(
        default_factory=lambda: Env.get("APP_DEBUG", True),
        metadata={
            "description": "Flag indicating whether debug mode is enabled. "
            "Defaults to False.",
            "default": True,
        },
    )

    host: str = field(
        default_factory=lambda: Env.get("APP_HOST", "127.0.0.1"),
        metadata={
            "description": "Host address of the application. Loaded from "
            "'APP_HOST' or defaults to '127.0.0.1'. For production or to "
            "listen on all interfaces, use '0.0.0.0'.",
            "default": "127.0.0.1",
        },
    )

    port: int = field(
        default_factory=lambda: Env.get("APP_PORT", 8000),
        metadata={
            "description": "The port on which the application will run. "
            "Defaults to 8000.",
            "default": 8000,
        },
    )

    workers: int = field(
        default_factory=lambda: Env.get("APP_WORKERS", 1),
        metadata={
            "description": "The number of worker processes to handle requests. "
            "Defaults to the maximum available workers.",
            "default": 1,
        },
    )

    reload: bool = field(
        default_factory=lambda: Env.get("APP_RELOAD", True),
        metadata={
            "description": "Flag indicating whether the application should "
            "reload on code changes. Defaults to True.",
            "default": True,
        },
    )

    timezone: str = field(
        default_factory=lambda: Env.get("APP_TIMEZONE", "UTC"),
        metadata={
            "description": "The timezone of the application. Defaults to 'UTC'.",
            "default": "UTC",
        },
    )

    locale: str = field(
        default_factory=lambda: Env.get("APP_LOCALE", "en"),
        metadata={
            "description": "The locale for the application. Defaults to 'en'.",
            "default": "en",
        },
    )

    fallback_locale: str = field(
        default_factory=lambda: Env.get("APP_FALLBACK_LOCALE", "en"),
        metadata={
            "description": "The fallback locale for the application. "
            "Defaults to 'en'.",
            "default": "en",
        },
    )

    cipher: str | Cipher = field(
        default_factory=lambda: Env.get("APP_CIPHER", Cipher.AES_256_CBC.value),
        metadata={
            "description": "The cipher used for encryption. Defaults to "
            "'AES_256_CBC'.",
            "default": Cipher.AES_256_CBC.value,
        },
    )

    key: str | None = field(
        default_factory=lambda: Env.get("APP_KEY"),
        metadata={
            "description": "The encryption key for the application. "
            "Defaults to None.",
            "default": None,
        },
    )

    maintenance: bool = field(
        default_factory=lambda: Env.get("APP_MAINTENANCE", False),
        metadata={
            "description": "Indicates whether the application is in maintenance mode.",
            "default": False,
        },
    )

    def __post_init__(self) -> None:  # NOSONAR
        """
        Validate and normalize attributes after dataclass initialization.

        Validates and normalizes all configuration fields, ensuring correct types
        and valid values. Raises exceptions if any field is invalid.

        Parameters
        ----------
        self : App
            The App instance being initialized.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If any attribute does not meet the required type constraints.
        ValueError
            If any attribute does not meet the required value constraints.
        """
        super().__post_init__()

        # Validate `name` attribute
        if not isinstance(self.name, (str, Environments)) or not str(self.name).strip():
            error_msg = (
                "The 'name' attribute must be a non-empty string or an "
                "Environments instance."
            )
            raise TypeError(error_msg)

        # Validate `env` attribute
        options_env = Environments._member_names_
        if isinstance(self.env, str):
            _value = str(self.env).strip().upper()
            if _value in options_env:
                object.__setattr__(self, "env", Environments[_value].value)
            else:
                error_msg = (
                    f"Invalid env value: {self.env}. Must be one of "
                    f"{options_env!s}."
                )
                raise ValueError(error_msg)
        elif isinstance(self.env, Environments):
            object.__setattr__(self, "env", self.env.value)
        else:
            error_msg = (
                "The 'env' attribute must be a string or Environments instance."
            )
            raise TypeError(error_msg)

        # Validate `debug` attribute
        if not isinstance(self.debug, bool):
            error_msg = "The 'debug' attribute must be a boolean."
            raise TypeError(error_msg)

        # Validate `host` attribute
        if not isinstance(self.host, str) or not self.host.strip():
            error_msg = "The 'host' attribute must be a non-empty string."
            raise TypeError(error_msg)

        # Validate `port` attribute
        if not isinstance(self.port, int):
            error_msg = "The 'port' attribute must be an integer."
            raise TypeError(error_msg)

        # Validate `workers` attribute
        if not isinstance(self.workers, int):
            error_msg = "The 'workers' attribute must be an integer."
            raise TypeError(error_msg)

        # Ensure workers count is within allowed range
        real_workers = Workers().calculate()
        if self.workers < 1 or self.workers > real_workers:
            error_msg = (
                f"The 'workers' attribute must be between 1 and {real_workers}."
            )
            raise ValueError(error_msg)

        # Validate `reload` attribute
        if not isinstance(self.reload, bool):
            error_msg = "The 'reload' attribute must be a boolean."
            raise TypeError(error_msg)

        # Validate `timezone` attribute
        if not isinstance(self.timezone, str) or not self.timezone.strip():
            error_msg = "The 'timezone' attribute must be a non-empty string."
            raise TypeError(error_msg)

        # Validate `locale` attribute
        if not isinstance(self.locale, str) or not self.locale.strip():
            error_msg = "The 'locale' attribute must be a non-empty string."
            raise TypeError(error_msg)

        # Validate `fallback_locale` attribute
        if (
            not isinstance(self.fallback_locale, str) or
            not self.fallback_locale.strip()
        ):
            error_msg = (
                "The 'fallback_locale' attribute must be a non-empty string."
            )
            raise TypeError(error_msg)

        # Validate `cipher` attribute
        options_cipher = Cipher._member_names_
        if not isinstance(self.cipher, (Cipher, str)):
            error_msg = "The 'cipher' attribute must be a Cipher or a string."
            raise TypeError(error_msg)

        if isinstance(self.cipher, str):
            _value = str(self.cipher).strip().upper().replace("-", "_")
            if _value in options_cipher:
                object.__setattr__(self, "cipher", Cipher[_value].value)
            else:
                error_msg = (
                    f"Invalid cipher value: {self.cipher}. Must be one of "
                    f"{options_cipher}."
                )
                raise ValueError(error_msg)
        elif isinstance(self.cipher, Cipher):
            object.__setattr__(self, "cipher", self.cipher.value)

        # Validate `key` attribute
        if self.key is None:
            # Generate and set a secure key if not provided
            generated_key = SecureKeyGenerator.generate()
            object.__setattr__(self, "key", generated_key)
            Env.set("APP_KEY", generated_key)
        if not isinstance(self.key, (bytes, str)) or not str(self.key).strip():
            error_msg = (
                "The 'key' attribute must be a non-empty string or bytes."
            )
            raise TypeError(error_msg)

        # Validate `maintenance` attribute
        if not isinstance(self.maintenance, bool):
            error_msg = "The 'maintenance' attribute must be a boolean."
            raise TypeError(error_msg)
