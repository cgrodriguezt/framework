from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.session.entities.session import Session
from orionis.foundation.config.session.enums import SameSitePolicy
from orionis.services.environment.env import Env

@dataclass(frozen=True, kw_only=True)
class BootstrapSession(Session):

    # ------------------------------------------------------------------------------
    # secret_key : str, optional
    # --- Secret key for signing session cookies.
    # --- Required for session security.
    # ------------------------------------------------------------------------------
    secret_key: str = field(
        default_factory=lambda: Env.get("APP_KEY"),
    )

    # ------------------------------------------------------------------------------
    # session_cookie : str, optional
    # --- Name of the session cookie.
    # --- Defaults to 'orionis_session'.
    # ------------------------------------------------------------------------------
    session_cookie: str = field(
        default_factory=lambda: Env.get("SESSION_COOKIE_NAME", "orionis_session"),
    )

    # ------------------------------------------------------------------------------
    # max_age : int | None, optional
    # --- Session expiration in seconds.
    # --- None means session ends when browser closes.
    # ------------------------------------------------------------------------------
    max_age: int | None = field(
        default_factory=lambda: Env.get("SESSION_MAX_AGE", 30 * 60),
    )

    # ------------------------------------------------------------------------------
    # same_site : str | SameSitePolicy, optional
    # --- SameSite cookie policy: 'lax', 'strict', or 'none'.
    # --- If 'none', https_only must be True.
    # ------------------------------------------------------------------------------
    same_site: str | SameSitePolicy = field(
        default_factory=lambda: Env.get("SESSION_SAME_SITE", SameSitePolicy.LAX.value),
    )

    # ------------------------------------------------------------------------------
    # path : str, optional
    # --- Path for the session cookie.
    # --- Defaults to '/'.
    # ------------------------------------------------------------------------------
    path: str = field(
        default_factory=lambda: Env.get("SESSION_PATH", "/"),
    )

    # ------------------------------------------------------------------------------
    # https_only : bool, optional
    # --- Restricts session cookie to HTTPS if True.
    # --- Must be True if same_site is 'none'.
    # ------------------------------------------------------------------------------
    https_only: bool = field(
        default_factory=lambda: Env.get("SESSION_HTTPS_ONLY", False),
    )

    # ------------------------------------------------------------------------------
    # domain : str | None, optional
    # --- Domain for the session cookie.
    # --- None means cookie is valid for current domain only.
    # ------------------------------------------------------------------------------
    domain: str | None = field(
        default_factory=lambda: Env.get("SESSION_DOMAIN"),
    )
