from __future__ import annotations
from typing import TYPE_CHECKING, Any
from sqlalchemy import URL, event
from sqlalchemy.pool import StaticPool
from orionis.database.exceptions import (
    MissingDatabaseDependencyException,
    UnsupportedDriverException,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

# Map of Orionis driver names to SQLAlchemy async dialect names.
_DIALECTS: dict[str, str] = {
    "sqlite": "sqlite+aiosqlite",
    "mysql": "mysql+aiomysql",
    "pgsql": "postgresql+asyncpg",
    "oracle": "oracle+oracledb_async",
    "sqlserver": "mssql+aioodbc",
}

# Map of Orionis driver names to (pip package, install extra) hints.
_DRIVER_PACKAGES: dict[str, tuple[str, str]] = {
    "sqlite": ("aiosqlite", "orionis"),
    "mysql": ("aiomysql", "orionis[mysql]"),
    "pgsql": ("asyncpg", "orionis[pgsql]"),
    "oracle": ("oracledb", "orionis[oracle]"),
    "sqlserver": ("aioodbc", "orionis[sqlserver]"),
}

# Default ODBC driver used for SQL Server connections.
_DEFAULT_ODBC_DRIVER: str = "ODBC Driver 18 for SQL Server"

# SQLite database markers that identify an in-memory database.
_SQLITE_MEMORY_MARKERS: frozenset[str] = frozenset({":memory:", ""})


def resolveDriver(config: dict[str, Any]) -> str:
    """
    Extract and validate the driver name from a connection configuration.

    Parameters
    ----------
    config : dict
        Connection configuration containing a ``driver`` key.

    Returns
    -------
    str
        Normalized driver name.

    Raises
    ------
    UnsupportedDriverException
        If the driver is missing or has no registered dialect.
    """
    driver = str(config.get("driver", "")).strip().lower()
    if driver not in _DIALECTS:
        supported = ", ".join(sorted(_DIALECTS))
        error_msg = (
            f"Unsupported database driver '{driver}'. "
            f"Supported drivers: {supported}."
        )
        raise UnsupportedDriverException(error_msg)
    return driver


def missingDependencyError(
    driver: str,
    cause: ModuleNotFoundError,
) -> MissingDatabaseDependencyException:
    """
    Build the exception raised when an async DB driver package is absent.

    Parameters
    ----------
    driver : str
        Orionis driver name whose package is missing.
    cause : ModuleNotFoundError
        Original import error raised by the engine.

    Returns
    -------
    MissingDatabaseDependencyException
        Exception with an actionable installation hint.
    """
    package, extra = _DRIVER_PACKAGES.get(driver, (driver, "orionis"))
    error_msg = (
        f"The '{driver}' connection requires the '{package}' package "
        f"({cause}). Install it with: pip install {extra}"
    )
    return MissingDatabaseDependencyException(error_msg)


def buildEngineUrl(config: dict[str, Any]) -> URL:
    """
    Build the engine URL for a connection configuration.

    Parameters
    ----------
    config : dict
        Connection configuration produced by the database config entities.

    Returns
    -------
    URL
        Engine URL for the configured driver.

    Raises
    ------
    UnsupportedDriverException
        If the driver has no registered dialect.
    """
    driver = resolveDriver(config)
    if driver == "sqlite":
        return _sqliteUrl(config)
    if driver == "oracle":
        return _oracleUrl(config)
    return _serverUrl(driver, config)


def engineOptions(config: dict[str, Any]) -> dict[str, Any]:
    """
    Build keyword options for the async engine factory.

    Parameters
    ----------
    config : dict
        Connection configuration.

    Returns
    -------
    dict
        Options such as pool class and driver connect arguments.
    """
    driver = resolveDriver(config)
    options: dict[str, Any] = {"echo": False, "future": True}

    if driver == "sqlite":
        # A shared in-memory database requires a single pooled connection.
        if _isSqliteMemory(config):
            options["poolclass"] = StaticPool
            options["connect_args"] = {"check_same_thread": False}
        return options

    if driver == "pgsql":
        # asyncpg accepts libpq-style ssl mode strings directly.
        sslmode = str(config.get("sslmode", "") or "").strip()
        if sslmode:
            options["connect_args"] = {"ssl": sslmode}
        return options

    if driver == "oracle":
        # A full DSN bypasses the host/port URL components entirely.
        dsn = config.get("dsn") or config.get("tns_name")
        if dsn:
            options["connect_args"] = {"dsn": str(dsn)}
        return options

    return options


def configureEngine(engine: AsyncEngine, config: dict[str, Any]) -> None:
    """
    Apply driver-specific session settings to a freshly built engine.

    For SQLite this installs a connect hook applying the configured
    PRAGMA settings on every new pooled connection.

    Parameters
    ----------
    engine : AsyncEngine
        Engine to configure.
    config : dict
        Connection configuration.

    Returns
    -------
    None
        This function does not return a value.
    """
    if resolveDriver(config) != "sqlite":
        return

    pragmas = _sqlitePragmas(config)
    if not pragmas:
        return

    # Register a Core pool event on the underlying sync engine; the aiosqlite
    # adapter exposes a synchronous cursor facade suitable for PRAGMAs.
    @event.listens_for(engine.sync_engine, "connect")
    def _applyPragmas(dbapi_connection: Any, _record: Any) -> None:  # noqa: ANN401
        cursor = dbapi_connection.cursor()
        for pragma in pragmas:
            cursor.execute(pragma)
        cursor.close()


# ── URL builders ────────────────────────────────────────────────────────────


def _sqliteUrl(config: dict[str, Any]) -> URL:
    """
    Build the engine URL for a SQLite connection.

    Parameters
    ----------
    config : dict
        SQLite connection configuration.

    Returns
    -------
    URL
        SQLite engine URL.
    """
    database = str(config.get("database", "") or "")
    if database in _SQLITE_MEMORY_MARKERS:
        database = ":memory:"
    return URL.create(_DIALECTS["sqlite"], database=database)


def _configText(config: dict[str, Any], key: str) -> str | None:
    """
    Extract a trimmed text value from a configuration mapping.

    Parameters
    ----------
    config : dict
        Connection configuration.
    key : str
        Configuration key to read.

    Returns
    -------
    str or None
        Trimmed value, or ``None`` when empty or absent.
    """
    value = str(config.get(key, "") or "").strip()
    return value or None


def _serverUrl(driver: str, config: dict[str, Any]) -> URL:
    """
    Build the engine URL for host-based drivers.

    Covers MySQL, PostgreSQL, and SQL Server connections addressed by
    host, port, and database name.

    Parameters
    ----------
    driver : str
        Normalized driver name.
    config : dict
        Connection configuration.

    Returns
    -------
    URL
        Engine URL with credentials, host, port, and database.
    """
    return URL.create(
        _DIALECTS[driver],
        username=_configText(config, "username"),
        password=_configText(config, "password"),
        host=_configText(config, "host"),
        port=int(config["port"]) if config.get("port") else None,
        database=_configText(config, "database"),
        query=_serverQuery(driver, config),
    )


def _serverQuery(driver: str, config: dict[str, Any]) -> dict[str, str]:
    """
    Build the URL query parameters for host-based drivers.

    Parameters
    ----------
    driver : str
        Normalized driver name.
    config : dict
        Connection configuration.

    Returns
    -------
    dict of str to str
        Query parameters for the engine URL.
    """
    query: dict[str, str] = {}

    if driver == "mysql":
        charset = _configText(config, "charset")
        if charset:
            query["charset"] = charset
        unix_socket = _configText(config, "unix_socket")
        if unix_socket:
            query["unix_socket"] = unix_socket

    if driver == "sqlserver":
        query["driver"] = _configText(config, "odbc_driver") or _DEFAULT_ODBC_DRIVER
        if config.get("encrypt") is not None:
            query["Encrypt"] = _yesNo(config["encrypt"])
        if config.get("trust_server_certificate") is not None:
            query["TrustServerCertificate"] = _yesNo(
                config["trust_server_certificate"],
            )

    return query


def _oracleUrl(config: dict[str, Any]) -> URL:
    """
    Build the engine URL for an Oracle connection.

    Parameters
    ----------
    config : dict
        Oracle connection configuration.

    Returns
    -------
    URL
        Oracle engine URL using service name or SID addressing.
    """
    # When a DSN or TNS alias is present, addressing happens via
    # connect_args and the URL only carries the credentials.
    if config.get("dsn") or config.get("tns_name"):
        return URL.create(
            _DIALECTS["oracle"],
            username=_configText(config, "username"),
            password=_configText(config, "password"),
        )

    sid = _configText(config, "sid")
    return URL.create(
        _DIALECTS["oracle"],
        username=_configText(config, "username"),
        password=_configText(config, "password"),
        host=_configText(config, "host"),
        port=int(config["port"]) if config.get("port") else None,
        database=sid,
        query=_oracleQuery(config, sid),
    )


def _oracleQuery(config: dict[str, Any], sid: str | None) -> dict[str, str]:
    """
    Build the URL query parameters for an Oracle connection.

    Parameters
    ----------
    config : dict
        Oracle connection configuration.
    sid : str or None
        Resolved SID; service-name addressing applies only without it.

    Returns
    -------
    dict of str to str
        Query parameters for the engine URL.
    """
    service_name = _configText(config, "service_name")
    if service_name and not sid:
        return {"service_name": service_name}
    return {}


# ── SQLite helpers ──────────────────────────────────────────────────────────


def _isSqliteMemory(config: dict[str, Any]) -> bool:
    """
    Report whether a SQLite configuration targets an in-memory database.

    Parameters
    ----------
    config : dict
        SQLite connection configuration.

    Returns
    -------
    bool
        ``True`` for in-memory databases.
    """
    database = str(config.get("database", "") or "")
    return database in _SQLITE_MEMORY_MARKERS


def _sqlitePragmas(config: dict[str, Any]) -> tuple[str, ...]:
    """
    Build the PRAGMA statements for a SQLite configuration.

    Parameters
    ----------
    config : dict
        SQLite connection configuration.

    Returns
    -------
    tuple of str
        PRAGMA statements to run on each new connection.
    """
    pragmas: list[str] = []

    foreign_keys = config.get("foreign_key_constraints")
    if foreign_keys is not None:
        state = _normalizeSwitch(foreign_keys)
        pragmas.append(f"PRAGMA foreign_keys={state}")

    busy_timeout = config.get("busy_timeout")
    if isinstance(busy_timeout, int) and busy_timeout > 0:
        pragmas.append(f"PRAGMA busy_timeout={busy_timeout}")

    journal_mode = _enumValue(config.get("journal_mode"))
    if journal_mode:
        pragmas.append(f"PRAGMA journal_mode={journal_mode}")

    synchronous = _enumValue(config.get("synchronous"))
    if synchronous:
        pragmas.append(f"PRAGMA synchronous={synchronous}")

    return tuple(pragmas)


def _normalizeSwitch(value: Any) -> str:  # noqa: ANN401
    """
    Normalize a boolean-like configuration value to ``ON`` or ``OFF``.

    Parameters
    ----------
    value : Any
        Boolean, string, or enum member describing the switch state.

    Returns
    -------
    str
        ``"ON"`` or ``"OFF"``.
    """
    raw = _enumValue(value)
    if isinstance(value, bool):
        return "ON" if value else "OFF"
    return "ON" if str(raw).strip().upper() in {"ON", "TRUE", "1"} else "OFF"


def _yesNo(value: Any) -> str:  # noqa: ANN401
    """
    Normalize a boolean-like configuration value to ``yes`` or ``no``.

    Parameters
    ----------
    value : Any
        Boolean, string, or enum member describing the switch state.

    Returns
    -------
    str
        ``"yes"`` or ``"no"``.
    """
    if isinstance(value, bool):
        return "yes" if value else "no"
    raw = str(_enumValue(value)).strip().upper()
    return "yes" if raw in {"YES", "ON", "TRUE", "1"} else "no"


def _enumValue(value: Any) -> str:  # noqa: ANN401
    """
    Extract the primitive value from a possible enum member.

    Parameters
    ----------
    value : Any
        Enum member, string, or ``None``.

    Returns
    -------
    str
        String form of the value; empty when the input is ``None``.
    """
    if value is None:
        return ""
    inner = getattr(value, "value", value)
    return str(inner)
