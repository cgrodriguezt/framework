from dataclasses import dataclass
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.app.enums.ciphers import Cipher
from orionis.foundation.config.app.enums.environments import Environments
from orionis.services.environment.env import Env
from orionis.services.system.workers import Workers

@dataclass
class BootstrapApp(App):

    # -------------------------------------------------------------------------
    # name : str
    #     - The name of the application.
    #     - Loaded from environment variable 'APP_NAME' or defaults to 'Orionis Application'.
    # -------------------------------------------------------------------------
    name = Env.get('APP_NAME', 'Orionis Application')

    # -------------------------------------------------------------------------
    # env : str | Environments
    #     - Application environment (DEVELOPMENT, TESTING, PRODUCTION).
    #     - Loaded from 'APP_ENV' or defaults to Environments.DEVELOPMENT.
    # -------------------------------------------------------------------------
    env = Env.get('APP_ENV', Environments.DEVELOPMENT)

    # -------------------------------------------------------------------------
    # debug : bool
    #     - Debug mode flag.
    #     - Loaded from 'APP_DEBUG' or defaults to True.
    # -------------------------------------------------------------------------
    debug = Env.get('APP_DEBUG', True)

    # -------------------------------------------------------------------------
    # url : str
    #     - Base URL of the application.
    #     - Loaded from 'APP_URL' or defaults to 'http://127.0.0.1'.
    # -------------------------------------------------------------------------
    url = Env.get('APP_URL', 'http://127.0.0.1')

    # -------------------------------------------------------------------------
    # port : int
    #     - Port number for the application server.
    #     - Loaded from 'APP_PORT' or defaults to 8000.
    # -------------------------------------------------------------------------
    port = Env.get('APP_PORT', 8000)

    # -------------------------------------------------------------------------
    # workers : int
    #     - Number of worker processes.
    #     - Loaded from 'APP_WORKERS' or calculated by Workers().calculate().
    # -------------------------------------------------------------------------
    workers = Env.get('APP_WORKERS', Workers().calculate())

    # -------------------------------------------------------------------------
    # reload : bool
    #     - Enable or disable auto-reload on code changes.
    #     - Loaded from 'APP_RELOAD' or defaults to True.
    # -------------------------------------------------------------------------
    reload = Env.get('APP_RELOAD', True)

    # -------------------------------------------------------------------------
    # timezone : str
    #     - Default timezone for the application.
    #     - Loaded from 'APP_TIMEZONE' or defaults to 'UTC'.
    # -------------------------------------------------------------------------
    timezone = Env.get('APP_TIMEZONE', 'America/Bogota')

    # -------------------------------------------------------------------------
    # locale : str
    #     - Default locale for the application.
    #     - Loaded from 'APP_LOCALE' or defaults to 'en'.
    # -------------------------------------------------------------------------
    locale = Env.get('APP_LOCALE', 'en')

    # -------------------------------------------------------------------------
    # fallback_locale : str
    #     - Fallback locale if the default locale is unavailable.
    #     - Loaded from 'APP_FALLBACK_LOCALE' or defaults to 'en'.
    # -------------------------------------------------------------------------
    fallback_locale = Env.get('APP_FALLBACK_LOCALE', 'en')

    # -------------------------------------------------------------------------
    # cipher : str | Cipher
    #     - Cipher algorithm for encryption.
    #     - Loaded from 'APP_CIPHER' or defaults to Cipher.AES_256_CBC.
    # -------------------------------------------------------------------------
    cipher = Env.get('APP_CIPHER', Cipher.AES_256_CBC)

    # -------------------------------------------------------------------------
    # key : str
    #     - Encryption key for the application.
    #     - Loaded from 'APP_KEY' or defaults to an empty string.
    # -------------------------------------------------------------------------
    key = Env.get('APP_KEY')