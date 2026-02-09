from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.session.enums import SameSitePolicy
from orionis.foundation.config.session.helpers.secret_key import SecretKey
from orionis.services.environment.env import Env
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Session(BaseEntity):
    """
    Configure the Starlette session middleware.

    Parameters
    ----------
    secret_key : str
        Secret key for signing session cookies (required).
    session_cookie : str
        Name of the session cookie. Defaults to 'session'.
    max_age : int | None
        Session expiration in seconds. None for browser session.
    same_site : str | SameSitePolicy
        SameSite cookie policy.
    path : str
        Cookie path. Defaults to '/'.
    https_only : bool
        Restrict cookies to HTTPS. Defaults to False.
    domain : str | None
        Cookie domain for cross-subdomain usage.

    Returns
    -------
    None
        This class does not return a value.
    """

    # ruff: noqa: PLW0108

    secret_key: str = field(
        default_factory=lambda: Env.get("APP_KEY", SecretKey.random()),
        metadata={
            "description": "Secret key for signing session cookies (required).",
            "default": lambda: SecretKey.random(),
        },
    )

    session_cookie: str = field(
        default_factory=lambda: Env.get("SESSION_COOKIE_NAME", "orionis_session"),
        metadata={
            "description": "Name of the session cookie.",
            "default": "orionis_session",
        },
    )

    max_age: int | None = field(
        default_factory=lambda: Env.get("SESSION_MAX_AGE", 30 * 60),
        metadata={
            "description": "Session expiration in seconds. None for browser session.",
            "default": 30 * 60,
        },
    )

    same_site: str | SameSitePolicy = field(
        default_factory=lambda: Env.get("SESSION_SAME_SITE", SameSitePolicy.LAX.value),
        metadata={
            "description": "SameSite cookie policy.",
            "default": SameSitePolicy.LAX.value,
        },
    )

    path: str = field(
        default_factory=lambda: Env.get("SESSION_PATH", "/"),
        metadata={
            "description": "Cookie path.",
            "default": "/",
        },
    )

    https_only: bool = field(
        default_factory=lambda: Env.get("SESSION_HTTPS_ONLY", False),
        metadata={
            "description": "Restrict cookies to HTTPS.",
            "default": False,
        },
    )

    domain: str | None = field(
        default_factory=lambda: Env.get("SESSION_DOMAIN"),
        metadata={
            "description": "Cookie domain for cross-subdomain usage.",
            "default": None,
        },
    )

    def __validateSecretKey(self) -> None:
        """
        Validate the secret_key attribute.

        Ensures the secret_key is a non-empty string or bytes. Generates a random
        secret key if not provided.

        Parameters
        ----------
        self : Session
            The Session instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Generate a random secret key if not provided
        if self.secret_key is None:
            object.__setattr__(self, "secret_key", SecretKey.random())
        if not isinstance(self.secret_key, (bytes, str)) or not self.secret_key.strip():
            error_msg = "secret_key must be a non-empty string"
            raise ValueError(error_msg)

    def __validateSessionCookie(self) -> None:
        """
        Validate the session_cookie attribute.

        Ensures the session_cookie is a non-empty string and does not contain
        spaces, semicolons, or commas.

        Parameters
        ----------
        self : Session
            The Session instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.session_cookie, str) or not self.session_cookie.strip():
            error_msg = "session_cookie must be a non-empty string"
            raise ValueError(error_msg)
        # Check for invalid characters in session_cookie
        if any(c in self.session_cookie for c in " ;,"):
            error_msg = (
                "session_cookie must not contain spaces, semicolons, or commas"
            )
            raise ValueError(error_msg)

    def __validateMaxAge(self) -> None:
        """
        Validate the max_age attribute.

        Ensures max_age is an integer greater than zero or None.

        Parameters
        ----------
        self : Session
            The Session instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        if self.max_age is not None:
            if not isinstance(self.max_age, int):
                error_msg = "max_age must be an integer or None"
                raise TypeError(error_msg)
            if self.max_age <= 0:
                error_msg = "max_age must be a positive integer if set"
                raise ValueError(error_msg)

    def __validateSameSite(self) -> None:
        """
        Validate the same_site attribute.

        Ensures same_site is a valid string or SameSitePolicy value.

        Parameters
        ----------
        self : Session
            The Session instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        if not isinstance(self.same_site, (str, SameSitePolicy)):
            error_msg = "same_site must be a string or SameSitePolicy"
            raise TypeError(error_msg)
        # Normalize and validate same_site value
        if isinstance(self.same_site, str):
            options = SameSitePolicy._member_names_
            _value = self.same_site.upper().strip()
            if _value not in options:
                error_msg = (
                    f"same_site must be one of: {', '.join(options)}"
                )
                raise ValueError(error_msg)
            object.__setattr__(self, "same_site", SameSitePolicy[_value].value)
        elif isinstance(self.same_site, SameSitePolicy):
            object.__setattr__(self, "same_site", self.same_site.value)

    def __validateDomain(self) -> None:
        """
        Validate the domain attribute.

        Ensures domain is a non-empty string or None, and does not start or end
        with a dot or contain consecutive dots.

        Parameters
        ----------
        self : Session
            The Session instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        if self.domain is not None:
            if not isinstance(self.domain, str) or not self.domain.strip():
                error_msg = "domain must be a non-empty string or None"
                raise ValueError(error_msg)
            if self.domain.startswith(".") or self.domain.endswith("."):
                error_msg = "domain must not start or end with a dot"
                raise ValueError(error_msg)
            if ".." in self.domain:
                error_msg = "domain must not contain consecutive dots"
                raise ValueError(error_msg)

    def __post_init__(self) -> None:
        """
        Validate the initialization parameters of the session entity.

        Calls validation methods for each attribute to ensure correctness.

        Parameters
        ----------
        self : Session
            The Session instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__post_init__()

        # Validate secret_key
        self.__validateSecretKey()

        # Validate session_cookie
        self.__validateSessionCookie()

        # Validate max_age
        self.__validateMaxAge()

        # Validate same_site
        self.__validateSameSite()

        # Validate path
        if not isinstance(self.path, str) or not self.path.startswith("/"):
            error_msg = "path must be a string starting with '/'"
            raise ValueError(error_msg)

        # Validate https_only
        if not isinstance(self.https_only, bool):
            error_msg = "https_only must be a boolean value"
            raise TypeError(error_msg)

        # Validate domain
        self.__validateDomain()
