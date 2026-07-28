from typing import Any
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from orionis.database.connection import Connection
from orionis.database.contracts.connection import IConnection
from orionis.database.contracts.manager import IConnectionManager
from orionis.database.dialect import (
    buildSyncEngineUrl,
    missingDependencyError,
    resolveDriver,
    syncEngineOptions,
)
from orionis.database.exceptions import ConnectionNotFoundException
from orionis.foundation.contracts.application import IApplication

# ruff: noqa: TC001

class ConnectionManager(IConnectionManager):
    """
    Resolve, cache, and control the lifecycle of database connections.

    The manager reads the ``database`` configuration, keeps one plain
    configuration mapping per connection name, and builds
    :class:`Connection` objects lazily, caching them for reuse.

    Notes
    -----
    This module must not enable ``from __future__ import annotations``:
    the container resolves constructor dependencies from evaluated
    annotations, and stringized annotations cannot be injected.
    """

    __slots__ = ("_configs", "_connections", "_default")

    def __init__(self, app: IApplication) -> None:
        """
        Initialize the manager from the application configuration.

        Parameters
        ----------
        app : IApplication
            Application container providing the database configuration.

        Returns
        -------
        None
            This method does not return a value.
        """
        raw = app.config("database") or {}
        raw = self._asDict(raw)

        self._default: str = str(raw.get("default", "sqlite"))
        self._connections: dict[str, Connection] = {}

        # Normalize every connection entry into a plain dictionary.
        entries = self._asDict(raw.get("connections", {}) or {})
        self._configs: dict[str, dict[str, Any]] = {
            str(name): self._asDict(config)
            for name, config in entries.items()
        }

    # ── Resolution ──────────────────────────────────────────────────────────

    def connection(self, name: str | None = None) -> IConnection:
        """
        Resolve the connection registered under the given name.

        The connection is built on first access and cached for reuse.

        Parameters
        ----------
        name : str or None, optional
            Connection name as declared in the database configuration,
            or ``None`` for the default connection.

        Returns
        -------
        IConnection
            Connection bound to its configuration.

        Raises
        ------
        ConnectionNotFoundException
            If the connection is not declared in the configuration.
        """
        resolved = name or self._default
        cached = self._connections.get(resolved)
        if cached is not None:
            return cached

        config = self._configFor(resolved)
        instance = Connection(resolved, config)
        self._connections[resolved] = instance
        return instance

    def addConnection(self, name: str, config: dict[str, Any]) -> None:
        """
        Register or replace a named connection configuration at runtime.

        A live connection built from a previous configuration keeps
        serving until :meth:`disconnect` is called for that name.

        Parameters
        ----------
        name : str
            Connection name to register.
        config : dict
            Driver configuration for the connection.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If the name is empty or the configuration is not a mapping.
        """
        if not isinstance(name, str) or not name.strip():
            error_msg = "Connection name must be a non-empty string."
            raise ValueError(error_msg)
        if not isinstance(config, dict):
            error_msg = "Connection configuration must be a dictionary."
            raise TypeError(error_msg)
        self._configs[name.strip()] = dict(config)

    def hasConnection(self, name: str) -> bool:
        """
        Report whether a connection configuration exists.

        Parameters
        ----------
        name : str
            Connection name to look up.

        Returns
        -------
        bool
            ``True`` when the configuration is registered.
        """
        return name in self._configs

    # ── Default connection ──────────────────────────────────────────────────

    def getDefaultName(self) -> str:
        """
        Return the name of the default connection.

        Returns
        -------
        str
            Default connection name.
        """
        return self._default

    def setDefaultName(self, name: str) -> None:
        """
        Change the default connection name.

        Parameters
        ----------
        name : str
            Name of a registered connection.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ConnectionNotFoundException
            If the name is not registered.
        """
        if name not in self._configs:
            error_msg = (
                f"Cannot set default connection: '{name}' is not configured."
            )
            raise ConnectionNotFoundException(error_msg)
        self._default = name

    # ── Lifecycle ───────────────────────────────────────────────────────────

    async def disconnect(self, name: str | None = None) -> None:
        """
        Dispose one or all cached connections.

        Parameters
        ----------
        name : str or None, optional
            Connection to dispose, or ``None`` to dispose every cached
            connection.

        Returns
        -------
        None
            This method does not return a value.
        """
        if name is not None:
            instance = self._connections.pop(name, None)
            if instance is not None:
                await instance.disconnect()
            return

        # Dispose every cached connection and clear the registry.
        instances = list(self._connections.values())
        self._connections.clear()
        for instance in instances:
            await instance.disconnect()

    # ── APScheduler integration ─────────────────────────────────────────────

    def scheduleTaskStore(
        self,
        name: str | None = None,
        *,
        tablename: str = "scheduler_tasks",
    ) -> SQLAlchemyJobStore:
        """
        Build an APScheduler ``SQLAlchemyJobStore`` for a connection.

        APScheduler's ``SQLAlchemyJobStore`` always operates through a
        blocking SQLAlchemy engine, so the returned store is backed by a
        synchronous DBAPI driver rather than the async engine used by
        :meth:`connection`.

        Parameters
        ----------
        name : str or None, optional
            Connection name as declared in the database configuration,
            or ``None`` for the default connection.
        tablename : str, optional
            Name of the table used to persist scheduled jobs.

        Returns
        -------
        SQLAlchemyJobStore
            Job store bound to a synchronous engine for the connection.

        Raises
        ------
        ConnectionNotFoundException
            If the connection is not declared in the configuration.
        MissingDatabaseDependencyException
            If the synchronous driver package is not installed.
        """
        resolved = name or self._default
        config = self._configFor(resolved)

        url = buildSyncEngineUrl(config)
        options = syncEngineOptions(config)
        try:
            return SQLAlchemyJobStore(
                url=url,
                tablename=tablename,
                engine_options=options,
            )
        except ModuleNotFoundError as exc:
            raise missingDependencyError(
                resolveDriver(config),
                exc,
                sync=True,
            ) from exc

    # ── Internal helpers ────────────────────────────────────────────────────

    def _configFor(self, resolved: str) -> dict[str, Any]:
        """
        Look up the configuration registered under the resolved name.

        Parameters
        ----------
        resolved : str
            Connection name already resolved from ``name or default``.

        Returns
        -------
        dict
            Driver configuration for the connection.

        Raises
        ------
        ConnectionNotFoundException
            If the connection is not declared in the configuration.
        """
        config = self._configs.get(resolved)
        if config is None:
            available = ", ".join(sorted(self._configs)) or "none"
            error_msg = (
                f"Database connection '{resolved}' is not configured. "
                f"Available connections: {available}."
            )
            raise ConnectionNotFoundException(error_msg)
        return config

    @staticmethod
    def _asDict(value: Any) -> dict[str, Any]:  # noqa: ANN401
        """
        Coerce configuration entities or mappings into plain dictionaries.

        Parameters
        ----------
        value : Any
            Mapping or entity exposing a ``toDict`` method.

        Returns
        -------
        dict
            Plain dictionary representation of the value.
        """
        if isinstance(value, dict):
            return value
        to_dict = getattr(value, "toDict", None)
        if callable(to_dict):
            return dict(to_dict())
        return dict(value)
