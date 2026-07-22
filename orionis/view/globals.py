from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.foundation.contracts.application import IApplication

# ruff: noqa: ANN401, PLC0415, BLE001

# ── Individual global builders ─────────────────────────────────────────────────

def _makeConfig(app: IApplication) -> Any:
    """
    Build the ``config`` template global bound to the application.

    Parameters
    ----------
    app : IApplication
        Application container providing configuration access.

    Returns
    -------
    Any
        Callable that retrieves a dot-separated configuration key.
    """
    def config(key: str, default: Any = None) -> Any:
        """
        Retrieve an application configuration value.

        Parameters
        ----------
        key : str
            Dot-separated configuration key (e.g. ``'app.name'``).
        default : Any, optional
            Value returned when the key is absent.

        Returns
        -------
        Any
            Configuration value or *default*.
        """
        try:
            return app.config(key)
        except Exception:
            return default

    return config

def _makeApp(app: IApplication) -> Any:
    """
    Build the ``app`` template global.

    Parameters
    ----------
    app : IApplication
        Application container to expose in templates.

    Returns
    -------
    Any
        Callable returning the application instance.
    """
    def application() -> IApplication:
        """
        Return the application instance.

        Returns
        -------
        IApplication
            The running application container.
        """
        return app

    return application

def _makeRequest(app: IApplication) -> Any:
    """
    Build the async ``request`` template global.

    Parameters
    ----------
    app : IApplication
        Application container used for service resolution.

    Returns
    -------
    Any
        Async callable that resolves the current HTTP request.
    """
    async def request() -> Any:
        """
        Resolve the current HTTP request from the container.

        Returns
        -------
        Any | None
            The HTTP request bound to the active request scope, or ``None``
            when no request is in scope.
        """
        from orionis.http.contracts.request import IRequest

        try:
            return await app.make(IRequest)
        except Exception:
            return None

    return request

def _makeSession(app: IApplication) -> Any:
    """
    Build the async ``session`` template global.

    Parameters
    ----------
    app : IApplication
        Application container used for service resolution.

    Returns
    -------
    Any
        Async callable that resolves the current session.
    """
    async def session() -> Any:
        """
        Resolve the current session from the container.

        Returns
        -------
        Any | None
            The session instance bound to the active request scope, or
            ``None`` when the session service is unavailable.
        """
        from orionis.session.contracts.session import ISession

        try:
            return await app.make(ISession)
        except Exception:
            return None

    return session

def _makePythonVersion() -> Any:
    """
    Build the ``python_version`` template global.

    Returns
    -------
    Any
        Callable that returns the Python version.
    """
    import sys

    def python_version() -> str:
        """
        Return the Python version.

        Returns
        -------
        str
            Python version in ``X.X.X`` format.
        """
        major = sys.version_info.major
        minor = sys.version_info.minor
        micro = sys.version_info.micro

        return f"{major}.{minor}.{micro}"

    return python_version

def _makeFrameworkVersion() -> Any:
    """
    Build the ``framework_version`` template global.

    Returns
    -------
    Any
        Callable that returns the framework version.
    """
    def framework_version() -> str:
        """
        Return the framework version.

        Returns
        -------
        str
            Framework version in ``X.X.X`` format.
        """
        from orionis.metadata import VERSION
        return VERSION

    return framework_version

# ── Public builder ─────────────────────────────────────────────────────────────

def buildViewGlobals(app: IApplication) -> dict[str, Any]:
    """
    Build all template global callables bound to the application instance.

    Each callable is a closure that captures ``app`` so it resolves the
    correct service at render time without storing stale references.
    Async callables (``request``, ``session``, ``auth``) are automatically
    awaited by Jinja2 when the environment is configured with
    ``enable_async=True``.

    Parameters
    ----------
    app : IApplication
        Application container used for configuration access and runtime
        service resolution.

    Returns
    -------
    dict[str, Any]
        Mapping of template global name to its callable implementation.
    """
    return {
        "config": _makeConfig(app),
        "app": _makeApp(app),
        "request": _makeRequest(app),
        "session": _makeSession(app),
        "python_version": _makePythonVersion(),
        "framework_version": _makeFrameworkVersion(),
    }
