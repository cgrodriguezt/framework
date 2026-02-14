from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.app.enums.ciphers import Cipher
from orionis.foundation.config.app.enums.environments import Environments
from orionis.services.environment.env import Env

@dataclass(frozen=True, kw_only=True)
class BootstrapApp(App):

    # ----------------------------------------------------------------------------------
    # name : str, optional
    # --- The name of the application. Defaults to the value of the 'APP_NAME'
    #     environment variable or 'Orionis Application'.
    # ----------------------------------------------------------------------------------
    name: str = field(
        default_factory=lambda: Env.get("APP_NAME", "Orionis Application"),
    )

    # ----------------------------------------------------------------------------------
    # env : str | Environments, optional
    # --- The environment in which the application runs. Defaults to the value of the
    #     'APP_ENV' environment variable or Environments.DEVELOPMENT.
    # ----------------------------------------------------------------------------------
    env: str | Environments = field(
        default_factory=lambda: Env.get("APP_ENV", Environments.DEVELOPMENT),
    )

    # ----------------------------------------------------------------------------------
    # debug : bool, optional
    # --- Whether debug mode is enabled. Defaults to the value of the 'APP_DEBUG'
    #     environment variable or True.
    # ----------------------------------------------------------------------------------
    debug: bool = field(
        default_factory=lambda: Env.get("APP_DEBUG", True),
    )

    # ----------------------------------------------------------------------------------
    # host : str, optional
    # --- The host address of the application. Defaults to the value of the 'APP_HOST'
    #     environment variable or '127.0.0.1'.
    # ----------------------------------------------------------------------------------
    host: str = field(
        default_factory=lambda: Env.get("APP_HOST", "127.0.0.1"),
    )

    # ----------------------------------------------------------------------------------
    # port : int, optional
    # --- The port on which the application will run. Defaults to the value of the
    #     'APP_PORT' environment variable or 8000.
    # ----------------------------------------------------------------------------------
    port: int = field(
        default_factory=lambda: Env.get("APP_PORT", 8000),
    )

    # ----------------------------------------------------------------------------------
    # workers : int, optional
    # --- Number of worker processes to handle requests. Defaults to the value of the
    #     'APP_WORKERS' environment variable or 1.
    # ----------------------------------------------------------------------------------
    workers: int = field(
        default_factory=lambda: Env.get("APP_WORKERS", 1),
    )

    # ----------------------------------------------------------------------------------
    # reload : bool, optional
    # --- Whether the application should reload on code changes. Defaults to the value
    #     of the 'APP_RELOAD' environment variable or True.
    # ----------------------------------------------------------------------------------
    reload: bool = field(
        default_factory=lambda: Env.get("APP_RELOAD", True),
    )

    # ----------------------------------------------------------------------------------
    # timezone : str, optional
    # --- The timezone of the application. Defaults to the value of the 'APP_TIMEZONE'
    #     environment variable or 'UTC'.
    # ----------------------------------------------------------------------------------
    timezone: str = field(
        default_factory=lambda: Env.get("APP_TIMEZONE", "UTC"),
    )

    # ----------------------------------------------------------------------------------
    # locale : str, optional
    # --- The locale for the application. Defaults to the value of the 'APP_LOCALE'
    #     environment variable or 'en'.
    # ----------------------------------------------------------------------------------
    locale: str = field(
        default_factory=lambda: Env.get("APP_LOCALE", "en"),
    )

    # ----------------------------------------------------------------------------------
    # fallback_locale : str, optional
    # --- The fallback locale for the application. Defaults to the value of the
    #     'APP_FALLBACK_LOCALE' environment variable or 'en'.
    # ----------------------------------------------------------------------------------
    fallback_locale: str = field(
        default_factory=lambda: Env.get("APP_FALLBACK_LOCALE", "en"),
    )

    # ----------------------------------------------------------------------------------
    # cipher : str | Cipher, optional
    # --- The cipher used for encryption. Defaults to the value of the 'APP_CIPHER'
    #     environment variable or Cipher.AES_256_CBC.
    # ----------------------------------------------------------------------------------
    cipher: str | Cipher = field(
        default_factory=lambda: Env.get("APP_CIPHER", Cipher.AES_256_CBC),
    )

    # ----------------------------------------------------------------------------------
    # key : str | None, optional
    # --- The encryption key for the application. Defaults to the value of the
    #     'APP_KEY' environment variable or None.
    # ----------------------------------------------------------------------------------
    key: str | None = field(
        default_factory=lambda: Env.get("APP_KEY"),
    )

    # ----------------------------------------------------------------------------------
    # maintenance : str, optional
    # --- The maintenance route for the application. Defaults to the value of the
    #     'APP_MAINTENANCE' environment variable or '/maintenance'.
    # ----------------------------------------------------------------------------------
    maintenance: str = field(
        default_factory=lambda: Env.get("APP_MAINTENANCE", False),
    )
