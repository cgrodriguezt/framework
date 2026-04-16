from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self
from orionis.container.contracts.container import IContainer

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from pathlib import Path
    from orionis.console.base.contracts.scheduler import IBaseScheduler
    from orionis.container.contracts.service_provider import IServiceProvider
    from orionis.failure.contracts.handler import IBaseExceptionHandler
    from orionis.foundation.enums.lifespan import Lifespan
    from orionis.foundation.enums.runtimes import Runtime

_SENTINEL = object()

class IApplication(IContainer, ABC):

    @property
    @abstractmethod
    def isBooted(self) -> bool:
        """
        Check if the application service providers have been booted.

        Returns
        -------
        bool
            True if all service providers have been booted and the application is
            ready for use; otherwise, False.
        """

    @property
    @abstractmethod
    def startAt(self) -> int:
        """
        Return the application startup timestamp in nanoseconds.

        Returns
        -------
        int
            Timestamp in nanoseconds since Unix epoch when the application
            instance was initialized.
        """

    @property
    @abstractmethod
    def routeHealthCheck(self) -> str:
        """
        Return the health check route for the application.

        Returns
        -------
        str
            The configured health check route path. Returns "/up" if not set.
        """

    @property
    @abstractmethod
    def entryPoint(self) -> str | None:
        """
        Return the entry point module path where the application was created.

        Returns
        -------
        str | None
            The module path (dot notation, e.g., 'folder.subfolder.file') where
            the application instance was created, or None if not available.
        """

    @property
    @abstractmethod
    def basePath(self) -> Path:
        """
        Return the base path of the application.

        Returns
        -------
        Path
            The base directory path of the application.
        """

    @property
    @abstractmethod
    def compiled(self) -> bool:
        """
        Indicate whether the application is running in compiled mode.

        Returns
        -------
        bool
            True if the application is configured to run in compiled mode,
            otherwise False.
        """

    @property
    @abstractmethod
    def compiledPath(self) -> Path | None:
        """
        Return the path where compiled cache files are stored.

        Returns
        -------
        Path or None
            The directory path for compiled cache storage, or None if not
            configured.
        """

    @property
    @abstractmethod
    def compiledInvalidationPathsDirs(self) -> list[Path]:
        """
        Return the list of directory paths monitored for cache invalidation.

        Returns
        -------
        list of Path
            List of directory paths monitored for cache invalidation.
        """

    @property
    @abstractmethod
    def compiledInvalidationPathsFiles(self) -> list[Path]:
        """
        Return the list of file paths monitored for cache invalidation.

        Returns
        -------
        list of Path
            List of file paths monitored for cache invalidation.
        """

    @abstractmethod
    def on(
        self,
        lifespan: Lifespan,
        *callbacks: Callable[..., Any] | Callable[..., Awaitable[Any]],
        runtime: Runtime | None = None,
    ) -> Self:
        """
        Register callbacks for a specific application lifespan event.

        Parameters
        ----------
        lifespan : Lifespan
            The application lifespan event to register callbacks for.
        *callbacks : Callable[..., Any] | Callable[..., Awaitable[Any]]
            One or more callback functions to execute during the event.
        runtime : Runtime | None, optional
            The runtime environment for which to register the callbacks.
            If None, callbacks are registered for all runtimes.

        Returns
        -------
        Self
            The current Application instance for method chaining.

        Raises
        ------
        TypeError
            If `lifespan` is not a Lifespan enum or any callback is not callable.
        ValueError
            If no callbacks are provided.

        Notes
        -----
        Callbacks are stored as-is and executed during the specified lifespan
        event. Lambdas and dynamic callables are supported.
        """

    @abstractmethod
    def withProviders(
        self,
        *providers: type[IServiceProvider],
    ) -> Self:
        """
        Register service providers for the application.

        Parameters
        ----------
        providers : tuple[type[IServiceProvider], ...]
            Service provider classes to register. Each must inherit from
            IServiceProvider.

        Returns
        -------
        Self
            The current Application instance for method chaining.

        Raises
        ------
        TypeError
            If any argument is not a class or does not inherit from
            IServiceProvider.
        """

    @abstractmethod
    def withRouting(
        self,
        api: str | list[str] | None = None,
        web: str | list[str] | None = None,
        console: str | list[str] | None = None,
        health: str | None = None,
    ) -> Self:
        """
        Configure routing paths for the application.

        Parameters
        ----------
        api : str | list[str] | None, optional
            Path(s) to API routing files.
        web : str | list[str] | None, optional
            Path(s) to web routing files.
        console : str | list[str] | None, optional
            Path(s) to console routing files.
        health : str | None, optional
            Path to health check route.

        Returns
        -------
        Self
            The current Application instance for method chaining.

        Raises
        ------
        ValueError
            If no routing path is provided.
        TypeError
            If routing arguments are of invalid types.
        """

    @abstractmethod
    def withExceptionHandler(
        self,
        handler: type[IBaseExceptionHandler],
    ) -> Self:
        """
        Register a custom exception handler class for the application.

        Parameters
        ----------
        handler : type[IBaseExceptionHandler]
            Exception handler class to use. Must inherit from BaseExceptionHandler.

        Returns
        -------
        Self
            The current Application instance for method chaining.

        Raises
        ------
        TypeError
            If the handler is not a class or not a subclass of BaseExceptionHandler.
        RuntimeError
            If attempting to set handler after application has been booted.
        ValueError
            If handler has already been set and cannot be modified.

        Notes
        -----
        Stores the handler class for later instantiation.
        """

    @abstractmethod
    async def getExceptionHandler(
        self,
    ) -> IBaseExceptionHandler:
        """
        Retrieve the registered exception handler instance.

        Parameters
        ----------
        self : Application
            The current application instance.

        Returns
        -------
        IBaseExceptionHandler
            The registered exception handler instance. If none is set, returns
            the default BaseExceptionHandler instance.

        Raises
        ------
        RuntimeError
            If called before the application is booted.
        """

    @abstractmethod
    def withScheduler(
        self,
        scheduler: type[IBaseScheduler],
    ) -> Self:
        """
        Register a custom scheduler class for the application.

        Parameters
        ----------
        scheduler : type[IBaseScheduler]
            The scheduler class to be used. Must inherit from IBaseScheduler.

        Returns
        -------
        Self
            The current Application instance for method chaining.

        Raises
        ------
        RuntimeError
            If attempting to set scheduler after application has been booted.
        ValueError
            If scheduler has already been set and cannot be modified.
        TypeError
            If the provided scheduler is not a subclass of IBaseScheduler.

        Notes
        -----
        Stores the scheduler class metadata for later instantiation.
        """

    @abstractmethod
    async def getScheduler(
        self,
    ) -> IBaseScheduler:
        """
        Retrieve the currently registered scheduler instance.

        Returns
        -------
        IBaseScheduler
            The registered scheduler instance.

        Raises
        ------
        RuntimeError
            If the application is not booted.
        """

    @abstractmethod
    def withConfigApp(
        self,
        **app_config: dict,
    ) -> Self:
        """
        Configure application settings using keyword arguments.

        Parameters
        ----------
        **app_config : dict
            Configuration parameters for the application. Keys must match the
            field names and types expected by the App dataclass from
            orionis.foundation.config.app.entities.app.App.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigAuth(
        self,
        **auth_config: dict,
    ) -> Self:
        """
        Configure authentication subsystem using keyword arguments.

        Parameters
        ----------
        **auth_config : dict
            Keyword arguments for authentication configuration. Keys must match
            the fields of the `Auth` dataclass from
            `orionis.foundation.config.auth.entities.auth.Auth`.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigCache(
        self,
        **cache_config: dict,
    ) -> Self:
        """
        Configure the cache subsystem using keyword arguments.

        Parameters
        ----------
        **cache_config : dict
            Keyword arguments representing cache configuration options. Keys must
            match the field names and types expected by the `Cache` dataclass from
            `orionis.foundation.config.cache.entities.cache.Cache`.

        Returns
        -------
        Self
            The current Application instance to enable method chaining.
        """

    @abstractmethod
    def withConfigHttp(
        self,
        **http_config: dict,
    ) -> Self:
        """
        Configure the HTTP subsystem using keyword arguments.

        Parameters
        ----------
        **http_config : dict
            Keyword arguments for HTTP configuration. Keys must match the field
            names and types expected by the `HTTP` dataclass from
            `orionis.foundation.config.http.entitites.http.HTTP`.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigDatabase(
        self,
        **database_config: dict,
    ) -> Self:
        """
        Configure the database subsystem using keyword arguments.

        Parameters
        ----------
        **database_config : dict
            Keyword arguments for database configuration. Keys must match the
            fields of the `Database` dataclass from
            `orionis.foundation.config.database.entities.database.Database`.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigFilesystems(
        self,
        **filesystems_config: dict,
    ) -> Self:
        """
        Configure the filesystems subsystem using keyword arguments.

        Parameters
        ----------
        **filesystems_config : dict
            Keyword arguments for filesystems configuration. Keys must match the
            fields of the `Filesystems` dataclass from
            `orionis.foundation.config.filesystems.entitites.filesystems.Filesystems`.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigLogging(
        self,
        **logging_config: dict,
    ) -> Self:
        """
        Configure logging subsystem using keyword arguments.

        Parameters
        ----------
        **logging_config : dict
            Keyword arguments for logging configuration. Keys must match the
            fields of the `Logging` dataclass from
            `orionis.foundation.config.logging.entities.logging.Logging`.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigMail(
        self,
        **mail_config: dict,
    ) -> Self:
        """
        Configure mail subsystem using keyword arguments.

        Parameters
        ----------
        **mail_config : dict
            Keyword arguments for mail configuration. Keys must match the fields
            of the `Mail` dataclass from
            `orionis.foundation.config.mail.entities.mail.Mail`.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigQueue(
        self,
        **queue_config: dict,
    ) -> Self:
        """
        Configure the queue subsystem using keyword arguments.

        Parameters
        ----------
        **queue_config : dict
            Keyword arguments representing queue configuration options. Keys must
            match the field names and types expected by the `Queue` dataclass from
            `orionis.foundation.config.queue.entities.queue.Queue`.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigSession(
        self,
        **session_config: dict,
    ) -> Self:
        """
        Configure session subsystem using keyword arguments.

        Parameters
        ----------
        session_config : dict
            Keyword arguments for session configuration. Keys must match the
            fields of the `Session` dataclass from
            `orionis.foundation.config.session.entities.session.Session`.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigTesting(
        self,
        **testing_config: dict,
    ) -> Self:
        """
        Configure the testing subsystem using keyword arguments.

        Parameters
        ----------
        **testing_config : dict
            Keyword arguments for testing configuration. Keys must match the
            fields of the `Testing` dataclass from
            `orionis.foundation.config.testing.entities.testing.Testing`.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def withConfigPaths(
        self,
        **paths: dict[str, str | Path | None],
    ) -> Self:
        """
        Set and resolve application directory paths.

        Parameters
        ----------
        **paths : dict[str, str | Path | None]
            Optional directory paths to override defaults. Valid keys include
            'root', 'app', 'console', 'exceptions', 'http', 'models',
            'providers', 'notifications', 'services', 'jobs', 'bootstrap',
            'config', 'database', 'resources', 'routes', 'storage', 'tests'.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def create(self) -> Self:
        """
        Bootstrap and initialize the application framework.

        Register the application instance, load all configurations, set timezone
        and locale, and mark the application as booted.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def config(
        self,
        key: str | None = None,
        value: object = _SENTINEL,
    ) -> object:
        """
        Get or set an application configuration value.

        Parameters
        ----------
        key : str or None, optional
            Dot-notated key specifying the configuration value to get or set.
            If None and value is not provided, returns the entire configuration.
        value : object, optional
            Value to set at the specified key. If not provided, retrieves the value.

        Returns
        -------
        object
            The configuration value for the given key, or the entire configuration
            if no key is provided. If setting a value, returns the value set.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        TypeError
            If the configuration key is not a string.
        """

    @abstractmethod
    def resetRuntimeConfig(self) -> bool:
        """
        Reset the runtime configuration to a mutable copy of the bootstrap config.

        Resets the application's runtime configuration to a mutable and isolated
        copy of the bootstrap configuration. Marks the runtime config as fresh,
        allowing re-initialization by calling `create()` again.

        Returns
        -------
        bool
            True if the configuration was reset successfully.
        """

    @abstractmethod
    def path(
        self,
        key: str | None = None,
    ) -> Path | dict | None:
        """
        Retrieve an application path by key or return all paths.

        Parameters
        ----------
        key : str | None, optional
            The key for the desired path. If None, returns all paths.

        Returns
        -------
        Path | dict | None
            The resolved path for the given key, all paths as a dictionary,
            or None if the key does not exist.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        TypeError
            If the key is not a string.
        """

    @abstractmethod
    def routingPaths(
        self,
        key: str | None = None,
    ) -> list[Path] | dict | None:
        """
        Retrieve routing file paths from configuration.

        Only 'api', 'web', and 'console' routing types are supported.
        The health-check route is exposed through the ``routeHealthCheck``
        property and is not accessible via this method.

        Parameters
        ----------
        key : str | None, optional
            Routing type to retrieve: 'api', 'web', or 'console'.
            If None, returns the complete routing configuration dictionary.

        Returns
        -------
        list[Path] | dict | None
            List of Path objects for the specified routing type, the complete
            routing configuration dictionary if no key is provided, or None
            if the key is not one of the valid routing types.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        TypeError
            If the key is not a string or None.
        """

    @abstractmethod
    def isProduction(self) -> bool:
        """
        Determine if the application is running in a production environment.

        Checks the 'app.env' configuration value to see if it contains 'prod'.
        This is useful for toggling production-specific features.

        Returns
        -------
        bool
            True if the application environment contains 'prod', otherwise False.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        """

    @abstractmethod
    def isDebug(self) -> bool:
        """
        Determine if the application is running in debug mode.

        Returns
        -------
        bool
            True if debug mode is enabled in the configuration, otherwise False.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        """
