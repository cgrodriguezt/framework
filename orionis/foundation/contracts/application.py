from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from orionis.container.contracts.container import IContainer

if TYPE_CHECKING:
    from pathlib import Path
    from orionis.console.contracts.base_scheduler import IBaseScheduler
    from orionis.container.contracts.service_provider import IServiceProvider
    from orionis.failure.contracts.handler import IBaseExceptionHandler


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
    def cacheConfiguration(self) -> dict[str, Any]:
        """
        Return the current cache configuration settings.

        Returns
        -------
        dict[str, Any]
            Dictionary containing cache configuration settings including folder
            path, monitored directories, and monitored files. Returns empty
            dictionary if caching is not configured.
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

    @abstractmethod
    def withCache(
        self,
        path: Path,
        filename: str | None = None,
        monitored_dirs: list[Path] | None = None,
        monitored_files: list[Path] | None = None,
    ) -> Self:
        """
        Register cache configuration for the application.

        Parameters
        ----------
        path : Path
            The directory path for cache storage.
        filename : str | None, optional
            The cache filename. Defaults to "setup" if not provided.
        monitored_dirs : list[Path] | None, optional
            List of directories to monitor for cache invalidation.
        monitored_files : list[Path] | None, optional
            List of files to monitor for cache invalidation.

        Returns
        -------
        Application
            The current Application instance for method chaining.

        Raises
        ------
        TypeError
            If any argument is not of the expected type.
        """

    @abstractmethod
    def resolveDeferredProvider(
        self,
        service: type | str,
    ) -> None:
        """
        Resolve and register the deferred service provider for a given service.

        Parameters
        ----------
        service : type | str
            The service type or fully qualified class name for which to find the
            deferred provider.

        Returns
        -------
        None
            This method does not return any value. Registers the deferred service
            provider in the application container if found.

        Raises
        ------
        TypeError
            If the service parameter is not a type or string.
        """

    @abstractmethod
    def withProviders(
        self,
        providers: type[IServiceProvider] | list[type[IServiceProvider]],
    ) -> Self:
        """
        Register one or more service providers for the application.

        Parameters
        ----------
        providers : type[IServiceProvider] | list[type[IServiceProvider]]
            A single service provider class or a list of service provider classes
            to register. Each must inherit from IServiceProvider.

        Returns
        -------
        Application
            The current Application instance for method chaining.

        Raises
        ------
        TypeError
            If any argument is not a class or does not inherit from IServiceProvider.
        KeyError
            If a provider is already registered.
        """

    @abstractmethod
    def withRouting(
        self,
        api: Path | list[Path] | None = None,
        web: Path | list[Path] | None = None,
        console: Path | list[Path] | None = None,
        health: str | None = None,
    ) -> Self:
        """
        Configure routing paths for the application.

        Parameters
        ----------
        api : Path | list[Path] | None
            Path or list of Paths for API routing.
        web : Path | list[Path] | None
            Path or list of Paths for web routing.
        console : Path | list[Path] | None
            Path or list of Paths for console routing.
        health : str | None
            Health check route as a string.

        Returns
        -------
        Application
            The current Application instance for method chaining.

        Raises
        ------
        ValueError
            If all routing arguments are None.
        TypeError
            If any argument is not of the expected type.
        """

    @abstractmethod
    def withExceptionHandler(
        self,
        handler: type[IBaseExceptionHandler],
    ) -> Self:
        """
        Register a custom exception handler class for the application.

        Allow specification of a custom exception handler class that inherits from
        BaseExceptionHandler. The handler class manages exceptions raised within
        the application, including reporting and rendering error messages. The
        provided handler must be a class (not an instance) and must inherit from
        BaseExceptionHandler.

        Parameters
        ----------
        handler : Type[IBaseExceptionHandler]
            The exception handler class to be used by the application. Must be a
            subclass of BaseExceptionHandler.

        Returns
        -------
        Application
            The current Application instance, allowing for method chaining.

        Raises
        ------
        TypeError
            If the provided handler is not a class or is not a subclass of
            BaseExceptionHandler.
        RuntimeError
            If attempting to set handler after application has been booted.
        ValueError
            If handler has already been set and cannot be modified.
        """

    @abstractmethod
    def getExceptionHandler(
        self,
    ) -> IBaseExceptionHandler:
        """
        Return the registered exception handler instance.

        Retrieve an instance of the exception handler set via `setExceptionHandler`.
        If no custom handler is set, return a default `BaseExceptionHandler` instance.
        This object manages exception reporting and rendering within the application.

        Returns
        -------
        IBaseExceptionHandler
            Instance of the registered exception handler. If none is set, returns
            a default `BaseExceptionHandler` instance.

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

        This method allows you to specify a custom scheduler class that inherits
        from `BaseScheduler`. The scheduler is responsible for managing scheduled
        tasks within the application. The provided class will be validated to
        ensure it is a subclass of `BaseScheduler` and then stored for later use.

        Parameters
        ----------
        scheduler : Type[IBaseScheduler]
            The scheduler class to be used by the application. Must inherit from
            `BaseScheduler`.

        Returns
        -------
        Application
            The current `Application` instance to enable method chaining.

        Raises
        ------
        RuntimeError
            If attempting to set scheduler after application has been booted.
        ValueError
            If scheduler has already been set and cannot be modified.
        TypeError
            If the provided scheduler is not a subclass of `BaseScheduler`.
        """

    @abstractmethod
    def getScheduler(
        self,
    ) -> IBaseScheduler:
        """
        Return the currently registered scheduler instance.

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
        Configure the application using keyword arguments.

        This method provides a convenient way to set application configuration
        by passing individual configuration parameters as keyword arguments.
        The parameters are used to create an App configuration instance.

        Parameters
        ----------
        **app_config : dict
            Configuration parameters for the application. These must match the
            field names and types expected by the App dataclass from
            orionis.foundation.config.app.entities.app.App.

        Returns
        -------
        Application
            The current application instance to enable method chaining.
        """

    @abstractmethod
    def withConfigAuth(
        self,
        **auth_config: dict,
    ) -> Self:
        """
        Configure the authentication subsystem using keyword arguments.

        This method allows you to set authentication configuration for the application
        by passing individual configuration parameters as keyword arguments.
        The provided parameters are used to construct an `Auth` configuration instance,
        which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **auth_config : dict
            Keyword arguments representing authentication configuration options.
            These must match the field names and types expected by the `Auth` dataclass
            from `orionis.foundation.config.auth.entities.auth.Auth`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigCache(
        self,
        **cache_config: dict,
    ) -> Self:
        """
        Configure the cache subsystem using keyword arguments.

        This method allows you to set cache configuration for the application
        by passing individual configuration parameters as keyword arguments.
        The provided parameters are used to construct a `Cache` configuration instance,
        which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **cache_config : dict
            Keyword arguments representing cache configuration options.
            These must match the field names and types expected by the `Cache` dataclass
            from `orionis.foundation.config.cache.entities.cache.Cache`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigCors(
        self,
        **cors_config: dict,
    ) -> Self:
        """
        Configure the CORS subsystem using keyword arguments.

        This method allows you to set CORS configuration for the application
        by passing individual configuration parameters as keyword arguments.
        The provided parameters are used to construct a `Cors` configuration
        instance, which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **cors_config : dict
            Keyword arguments representing CORS configuration options.
            These must match the field names and types expected by the `Cors` dataclass
            from `orionis.foundation.config.cors.entities.cors.Cors`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigDatabase(
        self,
        **database_config: dict,
    ) -> Self:
        """
        Configure the database subsystem using keyword arguments.

        This method allows you to set database configuration for the application
        by passing individual configuration parameters as keyword arguments.
        The provided parameters are used to construct a `Database` configuration
        instance, which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **database_config : dict
            Keyword arguments representing database configuration options.
            These must match the field names and types expected by the `Database`
            dataclass from
                `orionis.foundation.config.database.entities.database.Database`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigFilesystems(
        self,
        **filesystems_config: dict,
    ) -> Self:
        """
        Configure the filesystems subsystem using keyword arguments.

        This method allows you to set filesystems configuration for the application
        by passing individual configuration parameters as keyword arguments.
        The provided parameters are used to construct a `Filesystems` configuration
        instance, which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **filesystems_config : dict
            Keyword arguments representing filesystems configuration options.
            These must match the field names and types expected by the `Filesystems`
            dataclass from:
              `orionis.foundation.config.filesystems.entitites.filesystems.Filesystems`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigLogging(
        self,
        **logging_config: dict,
    ) -> Self:
        """
        Configure the logging subsystem using keyword arguments.

        This method allows you to set logging configuration for the application
        by passing individual configuration parameters as keyword arguments.
        The provided parameters are used to construct a `Logging` configuration
        instance, which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **logging_config : dict
            Keyword arguments representing logging configuration options.
            These must match the field names and types expected by the `Logging`
            dataclass from `orionis.foundation.config.logging.entities.logging.Logging`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigMail(
        self,
        **mail_config: dict,
    ) -> Self:
        """
        Configure the mail subsystem using keyword arguments.

        This method allows you to set mail configuration for the application
        by passing individual configuration parameters as keyword arguments. The
        provided parameters are used to construct a `Mail` configuration instance,
        which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **mail_config : dict
            Keyword arguments representing mail configuration options.
            These must match the field names and types expected by the `Mail` dataclass
            from `orionis.foundation.config.mail.entities.mail.Mail`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigQueue(
        self,
        **queue_config: dict,
    ) -> Self:
        """
        Configure the queue subsystem using keyword arguments.

        This method allows you to set queue configuration for the application
        by passing individual configuration parameters as keyword arguments.
        The provided parameters are used to construct a `Queue` configuration
        instance, which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **queue_config : dict
            Keyword arguments representing queue configuration options.
            These must match the field names and types expected by the `Queue` dataclass
            from `orionis.foundation.config.queue.entities.queue.Queue`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigSession(
        self,
        **session_config: dict,
    ) -> Self:
        """
        Configure the session subsystem using keyword arguments.

        This method allows you to set session configuration for the application
        by passing individual configuration parameters as keyword arguments.
        The provided parameters are used to construct a `Session` configuration
        instance, which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **session_config : dict
            Keyword arguments representing session configuration options.
            These must match the field names and types expected by the `Session`
            dataclass from `orionis.foundation.config.session.entities.session.Session`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigTesting(
        self,
        **testing_config: dict,
    ) -> Self:
        """
        Configure the testing subsystem using keyword arguments.

        This method allows you to set testing configuration for the application
        by passing individual configuration parameters as keyword arguments.
        The provided parameters are used to construct a `Testing` configuration
        instance, which is then loaded into the application's internal configurators.

        Parameters
        ----------
        **testing_config : dict
            Keyword arguments representing testing configuration options.
            These must match the field names and types expected by the `Testing`
            dataclass from `orionis.foundation.config.testing.entities.testing.Testing`.

        Returns
        -------
        Application
            Returns the current `Application` instance to enable method chaining.
        """

    @abstractmethod
    def withConfigPaths(
        self,
        **paths: dict[str, str | Path | None],
    ) -> Self:
        """
        Set and resolve application directory paths with optimized performance.

        Parameters
        ----------
        root : str | Path | None, optional
            Root directory path.
        app : str | Path | None, optional
            Application directory path.
        console : str | Path | None, optional
            Console directory path.
        exceptions : str | Path | None, optional
            Exceptions directory path.
        http : str | Path | None, optional
            HTTP directory path.
        models : str | Path | None, optional
            Models directory path.
        providers : str | Path | None, optional
            Providers directory path.
        notifications : str | Path | None, optional
            Notifications directory path.
        services : str | Path | None, optional
            Services directory path.
        jobs : str | Path | None, optional
            Jobs directory path.
        bootstrap : str | Path | None, optional
            Bootstrap directory path.
        config : str | Path | None, optional
            Config directory path.
        database : str | Path | None, optional
            Database directory path.
        resources : str | Path | None, optional
            Resources directory path.
        routes : str | Path | None, optional
            Routes directory path.
        storage : str | Path | None, optional
            Storage directory path.
        tests : str | Path | None, optional
            Tests directory path.

        Returns
        -------
        Application
            The current Application instance for method chaining.
        """

    @abstractmethod
    def create(
        self,
    ) -> Self:
        """
        Bootstrap and initialize the complete application framework.

        Create and configure the application instance by registering it in the
        container, loading all configurations, and marking it as booted.

        Returns
        -------
        Self
            The current Application instance for method chaining.
        """

    @abstractmethod
    def handleCommand(
        self,
        args: list[str] | None = None,
    ) -> int:
        """
        Handle CLI command using the configured KernelCLI.

        Parameters
        ----------
        args : list[str] | None, optional
            Arguments to pass to the kernel's handle method. Defaults to empty
            list if not provided.

        Returns
        -------
        int
            The exit code returned by the CLI kernel's handle method.

        Raises
        ------
        RuntimeError
            If KernelCLI is not configured in the application.
        TypeError
            If the CLI kernel does not have a handle method.
        """

    @abstractmethod
    def config(
        self,
        key: str | None = None,
        value: object = _SENTINEL,
    ) -> object:
        """
        Get or set application configuration values using dot notation.

        Parameters
        ----------
        key : str | None, optional
            Dot-notated key specifying the configuration value to get or set.
            If None and value is not provided, returns the entire configuration.
        value : Any, optional
            Value to set at the specified key. If not provided, retrieves the value.

        Returns
        -------
        Any
            The configuration value for the given key, or the entire configuration
            if no key is provided. If setting a value, returns the value set.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        ValueError
            If the configuration key is not a string.
        """

    @abstractmethod
    def routingPaths(
        self,
        key: str | None = None,
    ) -> list[Path] | dict | Path | None:
        """
        Return routing file paths from application configuration.

        Retrieve routing file paths configured for the application. Return paths
        for a specific routing type if key is provided, otherwise return the
        complete routing configuration dictionary.

        Parameters
        ----------
        key : str | None, optional
            The routing type to retrieve ('api', 'web', 'console', or 'health').
            If None, returns the complete routing configuration.

        Returns
        -------
        list[Path] | dict | Path | None
            List of Path objects for the specified routing type, complete routing
            configuration dictionary if no key is provided, single Path for health
            routes, or None if the key does not exist.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        TypeError
            If the key is not a string or None.
        """

    @abstractmethod
    def resetRuntimeConfig(self) -> bool:
        """
        Reset the runtime configuration to a mutable copy of the bootstrap config.

        Reset the application's runtime configuration to a mutable copy of the
        bootstrap configuration. Marks the application as unconfigured, allowing
        re-initialization by calling `create()` again. Useful for testing or
        dynamic configuration reloads.

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
        Retrieve an application path configuration value.

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
        ValueError
            If the key is not a string.
        """
        # Ensure configuration is initialized before accessing paths
        if not self.__configured:
            error_msg = (
                "Application configuration is not initialized. Please call create() "
                "first."
            )
            raise RuntimeError(error_msg)

        # Retrieve the paths configuration
        paths: dict = self.__bootstrap.get("paths", {})

        # Return all paths if no key is provided
        if key is None:
            return paths

        # Validate key type
        if not isinstance(key, str):
            error_msg = (
                "Key must be a string. Use path() without arguments to get all paths."
            )
            raise TypeError(error_msg)

        # Return the requested path or None if not found
        return paths.get(key)

    @abstractmethod
    def isProduction(
        self,
    ) -> bool:
        """
        Check if the application is running in a production environment.

        Check the 'app.env' configuration value to determine if the current
        environment is set to 'production'. This is useful for conditionally
        executing code based on the environment, such as enabling or disabling
        debug features.

        Returns
        -------
        bool
            True if the application environment contains 'prod', False otherwise.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        """

    @abstractmethod
    def isDebug(
        self,
    ) -> bool:
        """
        Check if the application is running in debug mode.

        Retrieve the 'app.debug' configuration value to determine if debug mode
        is currently enabled for the application.

        Returns
        -------
        bool
            True if debug mode is enabled, False otherwise.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        """

    def hasWebSockets(
        self,
    ) -> bool:
        """
        Check if WebSockets are configured/enabled in the application.

        Returns
        -------
        bool
            True if WebSockets are enabled/configured, False otherwise.

        Raises
        ------
        RuntimeError
            If the application configuration is not initialized.
        """
