from dataclasses import dataclass
from orionis.foundation.config.session.entities.session import Session
from orionis.foundation.config.session.enums import SameSitePolicy
from orionis.services.environment.env import Env

@dataclass
class BootstrapSession(Session):

    # -------------------------------------------------------------------------
    # secret_key : str
    #    - Secret key for signing session cookies (required).
    #    - Defaults to a random key if not set.
    # -------------------------------------------------------------------------
    secret_key = Env.get('APP_KEY')

    # -------------------------------------------------------------------------
    # session_cookie : str
    #    - Name of the session cookie.
    #    - Defaults to 'orionis_session'.
    # -------------------------------------------------------------------------
    session_cookie = Env.get('SESSION_COOKIE_NAME', 'orionis_session')

    # -------------------------------------------------------------------------
    # max_age : Optional[int]
    #    - Session expiration in seconds. If None, the session lasts until the browser is
    #      closed.
    #    - Defaults to 30 minutes (1800 seconds).
    # -------------------------------------------------------------------------
    max_age = Env.get('SESSION_MAX_AGE', 30 * 60)

    # -------------------------------------------------------------------------
    # same_site : str | SameSitePolicy
    #    - SameSite cookie policy. Can be 'lax', 'strict', or 'none'.
    #    - Defaults to 'lax'.
    #    - If 'none', https_only must be True.
    # -------------------------------------------------------------------------
    same_site = Env.get('SESSION_SAME_SITE', SameSitePolicy.LAX)

    # -------------------------------------------------------------------------
    # path : str
    #    - Path for the session cookie.
    #    - Defaults to '/'.
    # -------------------------------------------------------------------------
    path = Env.get('SESSION_PATH', '/')

    # -------------------------------------------------------------------------
    # https_only : bool
    #    - If True, restricts the session cookie to HTTPS connections.
    #    - Defaults to False.
    #    - If same_site is 'none', this must be True.
    # -------------------------------------------------------------------------
    https_only = Env.get('SESSION_HTTPS_ONLY', False)

    # -------------------------------------------------------------------------
    # domain : Optional[str]
    #    - Domain for the session cookie, allowing cross-subdomain usage.
    #    - Defaults to None, meaning the cookie is valid for the current domain.
    # -------------------------------------------------------------------------
    domain = Env.get('SESSION_DOMAIN')