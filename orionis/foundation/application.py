from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Self
from orionis.console.contracts.base_scheduler import IBaseScheduler
from orionis.container.container import Container
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.failure.contracts.handler import IBaseExceptionHandler
from orionis.foundation.contracts.application import IApplication

if TYPE_CHECKING:
    from orionis.services.cache.contracts.file_based_cache import IFileBasedCache

_SENTINEL = object()

class Application(Container, IApplication):

    # ruff : noqa: PLC0415, PERF203, RUF005, PLR0912, C901

    @property
    def isBooted(self) -> bool:
        """
        Check if the application service providers have been booted.

        Returns
        -------
        bool
            True if all service providers have been booted and the application is
            ready for use; otherwise, False.
        """
        return self.__booted

    @property
    def startAt(self) -> int:
        """
        Return the application startup timestamp in nanoseconds.

        Returns
        -------
        int
            Timestamp in nanoseconds since Unix epoch when the application
            instance was initialized.
        """
        return self.__start_at

    def __init__(
        self,
    ) -> None:
        """
        Initialize the Application container with default configuration.

        Set up the initial application state, including service provider list,
        configuration storage, and boot status. Implement a singleton pattern
        to prevent multiple initializations of the same application instance.

        Returns
        -------
        None
            This method initializes internal state and does not return a value.
        """
        # Call the parent Container initializer
        super().__init__()

        # Ensure singleton initialization for the Application instance
        if not hasattr(self, "_Application__initialized"):

            # Initialize application startup timestamp
            self.__start_at: int = self.__startAt()

            # Initialize cache-related attributes
            self.__cache_driver: IFileBasedCache | None = None
            self.__cached: bool = False

            # Initialize resolved service instances
            self.__scheduler_resolved: IBaseScheduler | None = None
            self.__exception_handler_resolved: IBaseExceptionHandler | None = None

            # Initialize application state flags
            self.__booted: bool = False
            self.__configured: bool = False

            # Initialize configuration dictionaries
            self.__bootstrap: dict[str, Any] = {}
            self.__runtime_config: dict[str, Any] = {}

            # Initialize kernel CLI instance
            self.__kernel_cli: Callable | None = None

            # Initialize deferred providers cache
            self.__cache_resolved_providers: dict[str, IServiceProvider] = {}

            # Initialize providers registry sentinel
            self.__providers_registry_initialized: bool = False

            # Mark the Application as initialized to enforce singleton behavior
            self._Application__initialized = True

    # --- Default Configuration Setup Methods ---

    def __defaultBootstrap(
        self,
    ) -> dict[str, Any]:
        """
        Return the default bootstrap configuration dictionary.

        Create and return the default bootstrap configuration containing all
        necessary sections for application initialization including config,
        exception handler, kernels, paths, providers, routing, and scheduler.

        Returns
        -------
        dict[str, Any]
            The default bootstrap configuration dictionary with all core
            sections initialized.
        """
        # Import default constants for bootstrap configuration
        from orionis.foundation.core_exception_handler import CORE_EXCEPTION_HANDLER
        from orionis.foundation.core_kernels import CORE_KERNELS
        from orionis.foundation.core_scheduler import CORE_SCHEDULER
        from orionis.support.structures.freezer import FreezeThaw

        # Deep unfreeze core configurations for mutability
        core_exception_handler = FreezeThaw.thaw(CORE_EXCEPTION_HANDLER)
        core_scheduler = FreezeThaw.thaw(CORE_SCHEDULER)
        core_kernels = FreezeThaw.thaw(CORE_KERNELS)

        # Return the default bootstrap dictionary with all core sections
        return {
            "commands": {},
            "config": {},
            "exception_handler": core_exception_handler,
            "kernels": core_kernels,
            "paths": {},
            "providers": {},
            "routing": {},
            "scheduler": core_scheduler,
        }

    def __ensureDefaultBootstrap(
        self,
    ) -> None:
        """
        Initialize the bootstrap configuration with default values.

        Initialize the internal bootstrap configuration dictionary with the default
        bootstrap configuration if it is currently empty. This ensures the
        application has a valid configuration structure before any customization.

        Returns
        -------
        None
            This method does not return a value. It modifies the internal bootstrap
            configuration state in place.
        """
        # If bootstrap is not empty, return immediately
        if self.__bootstrap:
            return

        # Initialize bootstrap configuration if not already set
        self.__bootstrap = self.__defaultBootstrap()

    def __ensureDefaultPaths(
        self,
    ) -> None:
        """
        Ensure default application paths are set in the bootstrap configuration.

        Initialize the 'paths' key in the bootstrap dictionary using default
        configuration paths if it is missing or empty.

        Returns
        -------
        None
            This method does not return a value. It modifies the internal
            bootstrap state to ensure paths are set.
        """
        # If paths exist and are not empty, return immediately
        if self.__bootstrap.get("paths"):
            return

        # Set default paths if not already present in bootstrap configuration
        self.withConfigPaths()

    # --- Utility Functions for Application Loading ---

    def __startAt(
        self,
    ) -> int:
        """
        Return the application startup timestamp in nanoseconds.

        Returns
        -------
        int
            The timestamp in nanoseconds since the Unix epoch when the
            application instance was initialized.
        """
        # Lazy import
        import time

        # Return the current time in nanoseconds
        return time.time_ns()

    def __assertConfigMutable(
        self,
    ) -> None:
        """
        Assert that configuration is mutable before modification.

        Raises
        ------
        RuntimeError
            If attempting to modify configuration after application boot.

        Returns
        -------
        None
            This method does not return a value. Raises if configuration is locked.
        """
        # Prevent configuration changes after boot
        if self.__booted:
            error_msg = (
                "Cannot modify configuration after application has been booted."
            )
            raise RuntimeError(error_msg)

        # Initialize bootstrap configuration if not already set
        self.__ensureDefaultBootstrap()

    def __lockConfig(
        self,
    ) -> None:
        """
        Deeply freeze and lock the application configuration.

        Deeply freeze the internal bootstrap configuration to prevent further
        modifications. Sets the booted flag to True, indicating that the
        application's configuration is finalized and cannot be changed.

        Returns
        -------
        None
            This method does not return a value. The configuration is locked
            in-place.
        """
        # Deep freeze the bootstrap configuration to make it immutable
        from orionis.support.structures.freezer import FreezeThaw
        self.__bootstrap = FreezeThaw.freeze(self.__bootstrap)

    # --- Application Cache Handling Driver (If Configured) ---

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
        # Lazy import
        from orionis.services.cache.file_based_cache import FileBasedCache

        # Store cache settings for later use
        self.__cache_driver = FileBasedCache(
            path=path,
            filename=filename or "startup",
            monitored_dirs=monitored_dirs or [],
            monitored_files=monitored_files or [],
        )

        # Retrieve current cache settings
        current_cache = self.__cache_driver.get()

        # If valid cache exists, store it and mark as cached
        if current_cache is not None:
            self.__bootstrap = current_cache
            self.__cached = True
            self.__commitConfig()

        # Return self for method chaining
        return self

    def __saveCache(
        self,
    ) -> None:
        """
        Save the current bootstrap configuration to cache if caching is enabled.

        Returns
        -------
        None
            This method does not return a value. It saves the configuration
            to cache if a cache driver is configured.
        """
        # Lazy import
        from copy import deepcopy

        # If no cache driver is configured, do nothing
        if self.__cache_driver is None:
            return

        # Save the current bootstrap configuration to cache
        self.__cache_driver.save(deepcopy(self.__bootstrap))

    # --- Service Provider Bootstrapping Logic ---

    def __loadCoreProviders(
        self,
    ) -> None:
        """
        Load and register core framework service providers.

        Imports and registers essential service providers required for
        framework operation, including console, dumping, path resolution,
        progress bars, workers, logging, and testing capabilities. Ensures
        core services are available before user-defined providers.

        Parameters
        ----------
        self : ProvidersLoader
            Instance of ProvidersLoader.

        Returns
        -------
        None
            Modifies the internal providers registry in-place.
        """
        # Import core providers list [MappingProxyType]
        from orionis.foundation.core_providers import CORE_PROVIDERS

        # Register each provider in the appropriate registry
        for provider in CORE_PROVIDERS:
            self.__storeProviderInstance(provider)

    def __ensureProvidersRegistryStructure(
        self,
    ) -> None:
        """
        Ensure the providers registry structure is properly initialized.

        Initialize the eager and deferred provider registries in the bootstrap
        configuration if they do not already exist. This method creates the
        necessary dictionary structure for storing service provider information
        and prevents duplicate initialization through a sentinel attribute.

        Returns
        -------
        None
            This method does not return a value. It modifies internal state.
        """
        # Ensure eager and deferred provider registries exist
        if not self.__providers_registry_initialized:
            if "eager" not in self.__bootstrap["providers"]:
                self.__bootstrap["providers"]["eager"] = {}
            if "deferred" not in self.__bootstrap["providers"]:
                self.__bootstrap["providers"]["deferred"] = {}
            self.__providers_registry_initialized = True

    def __validateProviderClass(
        self,
        provider_class: type[IServiceProvider],
    ) -> None:
        """
        Validate that the provider class meets IServiceProvider requirements.

        Parameters
        ----------
        provider_class : type[IServiceProvider]
            The service provider class to validate.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions if validation
            fails.

        Raises
        ------
        TypeError
            If the provider is not a class or not a subclass of IServiceProvider.
        """
        # Validate that the provider is a class
        if not isinstance(provider_class, type):
            error_msg = (
                f"Expected IServiceProvider class, got "
                f"{type(provider_class).__name__}"
            )
            raise TypeError(error_msg)

        # Validate that the provider is a subclass of IServiceProvider
        if not issubclass(provider_class, IServiceProvider):
            error_msg = (
                f"Expected IServiceProvider subclass, got "
                f"{type(provider_class).__name__}"
            )
            raise TypeError(error_msg)

    def __storeEagerProviderInstance(
        self,
        provider: type[IServiceProvider],
    ) -> None:
        """
        Store an eager service provider instance in the eager registry.

        Parameters
        ----------
        provider : type[IServiceProvider]
            The service provider class to register.

        Returns
        -------
        None
            This method does not return a value. It modifies the internal eager
            providers registry in-place.

        Raises
        ------
        TypeError
            If the provider is not a class or not a subclass of IServiceProvider.
        """
        # Lazy import
        from collections import OrderedDict

        # Prepare eager provider registry
        eager = OrderedDict(self.__bootstrap["providers"]["eager"])

        # Extract module and class name for storage
        module = provider.__module__
        class_name = provider.__name__
        provider_full_path = f"{module}.{class_name}"

        # Remove if already exists to prevent duplicates
        eager.pop(provider_full_path, None)

        # Insert at the beginning to prioritize this provider
        eager[provider_full_path] = {
            "module": provider.__module__,
            "class": provider.__name__,
        }
        eager.move_to_end(provider_full_path, last=False)

        # Save the updated eager providers registry
        self.__bootstrap["providers"]["eager"] = eager

    def __storeDeferredProviderInstance(
        self,
        provider: type[IServiceProvider],
    ) -> None:
        """
        Store a deferred service provider instance in the deferred registry.

        Parameters
        ----------
        provider : type[IServiceProvider]
            The service provider class to register.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provider is not a class or not a subclass of IServiceProvider.
        """
        # Prepare deferred provider registry
        deferred: dict = self.__bootstrap["providers"]["deferred"]

        # Extract module and class name for storage
        module = provider.__module__
        class_name = provider.__name__
        provider_full_path = f"{module}.{class_name}"

        # For deferred providers, get their provides() method result
        provider_instance = provider(self)
        provides_method = getattr(provider_instance, "provides", None)
        if not callable(provides_method):
            error_msg = (
                f"Deferred provider {provider_full_path} must have a "
                "'provides' method"
            )
            raise TypeError(error_msg)

        # Register each service provided by the deferred provider
        provided_services:list = provides_method()
        for service in provided_services:
            service_full_path = f"{service.__module__}.{service.__name__}"
            deferred.pop(service_full_path, None)
            deferred[service_full_path] = {
                "module": module,
                "class": class_name,
            }

    def __storeProviderInstance(
        self,
        provider: type[IServiceProvider],
    ) -> None:
        """
        Store a service provider instance in the appropriate registry.

        Register the provider class in either the eager or deferred registry based
        on its inheritance hierarchy. Validates provider type and ensures proper
        registry structure before storage.

        Parameters
        ----------
        provider : type[IServiceProvider]
            The service provider class to register.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If the provider is not a class or not a subclass of IServiceProvider.
        """
        # Lazy import
        from orionis.container.providers.deferrable_provider import DeferrableProvider

        # Ensure providers registry structure is initialized
        self.__ensureProvidersRegistryStructure()

        # Validate the provider class meets requirements
        self.__validateProviderClass(provider)

        # Register as deferred or eager based on provider inheritance
        if issubclass(provider, DeferrableProvider):
            self.__storeDeferredProviderInstance(provider)
        else:
            self.__storeEagerProviderInstance(provider)

    def __discoverProviders(
        self,
        modules: set[str],
    ) -> None:
        """
        Discover and register service providers from the providers folder.

        Imports each discovered module, identifies classes that are
        subclasses of ServiceProvider, and registers them in the appropriate
        registry based on whether they are deferred or immediate providers.

        Parameters
        ----------
        self : ProvidersLoader
            Instance of ProvidersLoader.

        Returns
        -------
        None
            Modifies the internal providers registry in-place.
        """
        # Lazy import
        from orionis.container.providers.deferrable_provider import DeferrableProvider

        # Import each module and register its service providers
        for module_name in modules:
            module = __import__(module_name, fromlist=["*"])
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if (
                    isinstance(attribute, type) and
                    issubclass(attribute, ServiceProvider) and
                    attribute is not ServiceProvider and
                    attribute is not DeferrableProvider
                ):
                    self.__storeProviderInstance(attribute)

    def __loadProviders(
        self,
    ) -> None:
        """
        Load and register all service providers from the providers directory.

        Discovers provider modules, registers provider classes, and loads core
        framework providers. This ensures that all service providers are available
        for dependency injection and application bootstrapping.

        Parameters
        ----------
        self : Application
            The current application instance.

        Returns
        -------
        None
            This method does not return any value. It updates the internal
            providers registry in place.
        """
        # Lazy import
        from orionis.services.introspection.modules.engine import ModuleEngine

        # Discover provider modules in the providers directory
        config_paths = self.__bootstrap["paths"]
        providers_modules: set[str] = ModuleEngine.scan(
            app_root=config_paths["root"],
            tarjet_path=config_paths["providers"],
        )

        # Register discovered provider classes
        self.__discoverProviders(
            modules=providers_modules,
        )

        # Load and register core framework providers
        self.__loadCoreProviders()

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
        # Retrieve the deferred providers registry for fast lookup
        deferred = self.__bootstrap["providers"]["deferred"]

        # Compute the fully qualified service path
        if isinstance(service, type):
            service_full_path = f"{service.__module__}.{service.__name__}"
        elif isinstance(service, str):
            service_full_path = service
        else:
            error_msg = (
                f"Expected type or str for service, got {type(service).__name__}"
            )
            raise TypeError(error_msg)

        # Attempt to retrieve provider info for the given service
        provider_info = deferred.get(service_full_path)
        if provider_info is None:
            return None

        # Load and register the deferred provider class
        self.__registerAndBootProvider({
            service_full_path: provider_info
        })


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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Normalize input to a list of providers for uniform processing
        if isinstance(providers, type):
            providers = [providers]
        elif not isinstance(providers, list):
            error_msg = (
                "Expected IServiceProvider class or list, got "
                f"{type(providers).__name__}"
            )
            raise TypeError(error_msg)

        # Register each provider using the internal storage method
        for provider in providers:
            self.__storeProviderInstance(provider)

        # Return self instance for method chaining
        return self

    # --- Routing Configuration and Validation ---

    def __ensureRoutingDefinition(
        self,
        path: Path,
    ) -> None:
        """
        Ensure the file contains valid routing definitions.

        Parameters
        ----------
        path : Path
            File path to check for routing definitions.

        Returns
        -------
        None
            This method raises if the file does not contain valid routing
            definitions.

        Raises
        ------
        TypeError
            If the file does not contain valid routing definitions.
        """
        # Import the module engine for introspection
        from orionis.services.introspection.modules.engine import ModuleEngine

        # Check for required routing imports in the file
        required_imports = {
            "orionis.support.facades.reactor",
            "orionis.support.facades.router",
        }

        # Validate that the file contains routing definitions
        if not ModuleEngine.containsImports(path, required_imports):
            error_msg = (
                f"The file '{path}' does not contain valid routing definitions."
            )
            raise TypeError(error_msg)

    def __validateRoutingArgument(
        self,
        arg: Path | list[Path] | None,
        name: str,
    ) -> None:
        """
        Validate routing argument type and ensure routing definition.

        Parameters
        ----------
        arg : Path | list[Path] | None
            The routing argument to validate.
        name : str
            The name of the routing argument for error reporting.

        Returns
        -------
        None
            Raises TypeError if validation fails.

        Notes
        -----
        Ensures that the argument is either a Path or a list of Paths and that
        each Path contains a valid routing definition.
        """
        # Validate argument type and routing definition recursively for lists
        if arg is not None:
            if isinstance(arg, list):
                for route in arg:
                    self.__validateRoutingArgument(route, name)
            elif isinstance(arg, Path):
                self.__ensureRoutingDefinition(arg)
            else:
                error_msg = (
                    f"Expected Path or list[Path] for '{name}' routing, got "
                    f"{type(arg).__name__}."
                )
                raise TypeError(error_msg)

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Validate that at least one routing path is provided
        if all(route is None for route in (api, web, console, health)):
            error_msg = (
                "At least one routing path must be provided."
            )
            raise ValueError(error_msg)

        # Validate types of routing arguments
        self.__validateRoutingArgument(api, "api")
        self.__validateRoutingArgument(web, "web")
        self.__validateRoutingArgument(console, "console")

        # Validate health route type
        if health is not None and not isinstance(health, str):
            error_msg = (
                f"Expected str for 'health' routing, got {type(health).__name__}."
            )
            raise TypeError(error_msg)

        # Store routing configuration
        self.__bootstrap["routing"] = {
            "api": api,
            "web": web,
            "console": console,
            "health": health,
        }

        # Return self instance for method chaining
        return self

    # --- Exception Handler Configuration ---

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Ensure the provided handler is a class type
        if not isinstance(handler, type):
            error_msg = (
                f"Expected exception handler class, got {type(handler).__name__}"
            )
            raise TypeError(error_msg)

        # Ensure the provided handler is a subclass of BaseExceptionHandler
        if not issubclass(handler, IBaseExceptionHandler):
            error_msg = (
                f"Expected BaseExceptionHandler subclass, got {type(handler).__name__}"
            )
            raise TypeError(error_msg)

        # Store the exception handler class for later instantiation
        self.__bootstrap["exception_handler"] = {
            "module": handler.__module__,
            "class": handler.__name__,
        }

        # Return the application instance for method chaining
        return self

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
        # Ensure the application is booted before accessing the exception handler
        if not self.__booted:
            error_msg = (
                "Cannot retrieve exception handler before application is booted."
            )
            raise RuntimeError(error_msg)

        # Lazy import
        from orionis.services.introspection.modules.engine import ModuleEngine

        # Resolve and cache the exception handler instance if not already done
        if self.__exception_handler_resolved is None:
            exception_handler = self.__bootstrap["exception_handler"]
            self.__exception_handler_resolved = ModuleEngine.resolveClass(
                exception_handler["module"],
                exception_handler["class"],
            )

        # Return the exception handler instance
        return self.__exception_handler_resolved

    # --- Scheduler Configuration ---

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Validate that the scheduler is a subclass of BaseScheduler
        if not issubclass(scheduler, IBaseScheduler):
            error_msg = (
                f"Expected BaseScheduler subclass, got {type(scheduler).__name__}"
            )
            raise TypeError(error_msg)

        # Store the scheduler class for later instantiation
        self.__bootstrap["scheduler"] = {
            "module": scheduler.__module__,
            "class": scheduler.__name__,
        }

        # Return the application instance for method chaining
        return self

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
        # Ensure the application is booted before accessing the scheduler
        if not self.__booted:
            error_msg = "Cannot retrieve scheduler before application is booted."
            raise RuntimeError(error_msg)

        # Lazy import
        from orionis.services.introspection.modules.engine import ModuleEngine

        # Resolve and cache the scheduler instance if not already done
        if self.__scheduler_resolved is None:
            scheduler = self.__bootstrap["scheduler"]
            self.__scheduler_resolved = ModuleEngine.resolveClass(
                scheduler["module"],
                scheduler["class"],
            )

        # Return the scheduler instance
        return self.__scheduler_resolved()

    # --- Configuration Subsystem Setup Methods ---

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided application configuration
        self.__bootstrap["config"]["app"] = app_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided authentication configuration
        self.__bootstrap["config"]["auth"] = auth_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided cache configuration
        self.__bootstrap["config"]["cache"] = cache_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided CORS configuration
        self.__bootstrap["config"]["cors"] = cors_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided database configuration
        self.__bootstrap["config"]["database"] = database_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided filesystems configuration
        self.__bootstrap["config"]["filesystems"] = filesystems_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided logging configuration
        self.__bootstrap["config"]["logging"] = logging_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided mail configuration
        self.__bootstrap["config"]["mail"] = mail_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided queue configuration
        self.__bootstrap["config"]["queue"] = queue_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided session configuration
        self.__bootstrap["config"]["session"] = session_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Store the provided testing configuration
        self.__bootstrap["config"]["testing"] = testing_config

        # Return the application instance for method chaining
        return self

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
        # Return early if already cached
        if self.__cached:
            return self

        # Ensure configuration is not locked
        self.__assertConfigMutable()

        # Lazy import and deep freeze core paths
        from orionis.foundation.core_paths import CORE_APP_PATHS
        from orionis.support.structures.freezer import FreezeThaw

        # Deep unfreeze core application paths for mutability
        core_app_paths = FreezeThaw.thaw(CORE_APP_PATHS)

        # Get app root once and cache it
        app_root = Path.cwd().resolve()

        # Path validation function for performance
        def is_valid_path(path_arg: type[Any]) -> bool:
            """
            Check if the provided argument is a valid path type.

            Parameters
            ----------
            path_arg : type[Any]
                The argument to validate as a path type.

            Returns
            -------
            bool
                True if the argument is a valid path (str or Path), False otherwise.
            """
            return path_arg is not None and isinstance(path_arg, (str, Path))

        # Define default path mappings for performance
        default_paths = {"root": app_root, **core_app_paths}

        # Collect all arguments in a dictionary for batch processing
        path_args = {
            "root": paths.get("root"),
            "app": paths.get("app"),
            "console": paths.get("console"),
            "exceptions": paths.get("exceptions"),
            "http": paths.get("http"),
            "models": paths.get("models"),
            "providers": paths.get("providers"),
            "notifications": paths.get("notifications"),
            "services": paths.get("services"),
            "jobs": paths.get("jobs"),
            "bootstrap": paths.get("bootstrap"),
            "config": paths.get("config"),
            "database": paths.get("database"),
            "resources": paths.get("resources"),
            "routes": paths.get("routes"),
            "storage": paths.get("storage"),
            "tests": paths.get("tests"),
        }

        # Build final paths dictionary efficiently
        final_paths = {}
        for key, value in path_args.items():
            if is_valid_path(value):
                # Use provided path (convert to Path object and resolve)
                final_paths[key] = Path(value).resolve()
            # Use default path
            elif key == "root":
                final_paths[key] = default_paths[key]
            else:
                # Resolve default relative path as Path object
                final_paths[key] = (app_root / default_paths[key]).resolve()

        # Store the resolved paths in the application configuration
        self.__bootstrap["paths"] = final_paths

        # Return self for method chaining
        return self

    # --- Configuration Loading Methods ---

    def __loadCustomConfig(
        self,
        default_config: dict[str, Any],
        custom_config: dict[str, Any],
        dataclasses: set[tuple[str, str, str, type[Any]]] | None = None,
    ) -> dict[str, Any]:
        """
        Merge custom configuration and dataclass defaults into the base config.

        Parameters
        ----------
        default_config : dict[str, Any]
            The base configuration dictionary containing default values.
        custom_config : dict[str, Any]
            The custom configuration dictionary to merge into defaults.
        dataclasses : set[tuple[str, str, str, Type[Any]]] | None, optional
            Set of tuples containing dataclass info to merge, or None.

        Returns
        -------
        dict[str, Any]
            The merged configuration dictionary containing all sections.
        """
        # Lazy import
        from dataclasses import asdict

        # Helper function to update a config section
        def update_section(
            section: str,
            values: dict[str, Any],
            base: dict[str, Any],
        ) -> None:
            # Merge values into the base config section
            if section in base and isinstance(base[section], dict):
                base[section].update(values)
            else:
                base[section] = values

        # Merge custom config sections into defaults
        for section, values in custom_config.items():
            if isinstance(values, dict):
                update_section(section, values, default_config)

        # Merge dataclass config sections into defaults
        if dataclasses:
            for section, _, _, cls in dataclasses:
                try:
                    update_section(section, asdict(cls()), default_config)
                except Exception as e:
                    error_msg = str(e)
                    raise RuntimeError(error_msg) from e

        # Return merged configuration dictionary
        return default_config

    def __loadConfig(
        self,
    ) -> None:
        """
        Load and merge final configuration from discovered dataclasses & custom config.

        Discovers configuration modules and dataclasses, loads default configuration
        values, merges them with custom configuration, and updates the application's
        bootstrap dictionary with the final configuration and discovered providers.

        Returns
        -------
        None
            This method updates the internal bootstrap configuration in place.
        """
        # Lazy import
        from orionis.foundation.core_config import CORE_CONFIG
        from orionis.support.structures.freezer import FreezeThaw
        from orionis.services.introspection.modules.engine import ModuleEngine
        from copy import deepcopy

        # Deep freeze core configuration for processing
        core_config = FreezeThaw.thaw(CORE_CONFIG)

        # Discover configuration modules in the config directory
        config_paths = self.__bootstrap["paths"]
        config_modules = ModuleEngine.scan(
            app_root=config_paths["root"],
            tarjet_path=config_paths["config"],
        )

        # Discover final dataclasses in the discovered modules
        config_dataclasses = (
            ModuleEngine.discoverFinalDataclasses(
                modules=config_modules,
            )
        )

        # Load default configuration values from built-in dataclasses
        default_config = core_config

        # Retrieve custom configuration values if provided
        custom_config = {}
        if "config" in self.__bootstrap:
            custom_config = deepcopy(self.__bootstrap["config"])

        # Merge custom configuration and dataclass defaults into the base config
        final_config = self.__loadCustomConfig(
            default_config=default_config,
            custom_config=custom_config,
            dataclasses=config_dataclasses,
        )

        # Update the bootstrap configuration with the final merged config
        self.__bootstrap["config"] = final_config

    def __commitConfig(
        self,
    ) -> None:
        """
        Lock configuration and mark application as initialized.

        Freeze the bootstrap configuration to prevent further modifications and
        set the configured flag to indicate the application is ready for use.

        Returns
        -------
        None
            This method does not return a value. It modifies internal state
            to lock configuration.
        """
        # Deep freeze the configuration to prevent further modifications
        self.__lockConfig()

        # Mark configuration as initialized
        self.__configured = True

    # --- Bootstrap Application Methods ---

    def __registerAndBootProvider(
        self,
        providers: dict[str, dict[str, str]] | None = None,
    ) -> None:
        """
        Register and boot service providers in order, using cache to avoid duplicates.

        Parameters
        ----------
        providers : dict[str, dict[str, str]] | None
            Dictionary mapping provider names to their module and class info.

        Returns
        -------
        None
            This method does not return a value. Providers are initialized in place.
        """
        # Lazy import
        import asyncio
        from inspect import iscoroutinefunction

        async def _run_method(method: Callable[[], None]) -> None:
            """
            Run the given method, awaiting if it is a coroutine.

            Parameters
            ----------
            method : Callable[[], None]
            The method to execute, which may be synchronous or asynchronous.

            Returns
            -------
            None
            This function does not return a value.
            """
            # Check if the method is a coroutine and await if necessary.
            if iscoroutinefunction(method):
                await method()
            else:
                method()

        async def _process_provider(
            provider_key: str,
            provider_cls: dict[str, str],
        ) -> None:
            """
            Register and boot a single service provider asynchronously.

            Parameters
            ----------
            provider_key : str
            The unique key identifying the provider.
            provider_cls : dict[str, str]
            Dictionary with 'module' and 'class' keys for provider resolution.

            Returns
            -------
            None
            This function does not return a value.
            """
            # Import module engine for dynamic class resolution.
            from orionis.services.introspection.modules.engine import ModuleEngine

            # Use cache to avoid duplicate initialization.
            if provider_key in self.__cache_resolved_providers:
                return

            # Resolve and instantiate the provider class.
            provider_class = ModuleEngine.resolveClass(
                provider_cls["module"],
                provider_cls["class"],
            )

            # Instantiate the provider with the application instance.
            instance = provider_class(self)

            # Cache the resolved provider instance.
            self.__cache_resolved_providers[provider_key] = instance

            # Call register and boot methods if they exist.
            register_method = getattr(instance, "register", None)
            if callable(register_method):
                await _run_method(register_method)

            # Call boot method if it exists.
            boot_method = getattr(instance, "boot", None)
            if callable(boot_method):
                await _run_method(boot_method)

        async def _run_all_providers() -> None:
            """
            Run all provider registration and boot processes asynchronously.

            Iterates over the given providers dictionary and processes each
            provider using the asynchronous _process_provider function.

            Returns
            -------
            None
            This function does not return a value.
            """
            # Process each provider in the given dictionary.
            for provider_key, provider_cls in (providers or {}).items():
                await _process_provider(provider_key, provider_cls)

        # Run the asynchronous provider registration and booting.
        asyncio.run(_run_all_providers())

    def __load(
        self,
    ) -> None:
        """
        Load and initialize the application configuration and providers.

        This method ensures the bootstrap configuration is initialized, sets up
        default paths, loads the final application configuration, loads service
        providers, saves the configuration to cache, and locks the configuration.
        It then registers and boots all service providers.

        Returns
        -------
        None
            This method does not return a value. It modifies internal state.
        """
        # Skip loading if already cached
        if not self.__cached:

            # Ensure bootstrap configuration is initialized
            self.__ensureDefaultBootstrap()

            # Ensure default application paths are set
            self.__ensureDefaultPaths()

            # Load the final application configuration
            self.__loadConfig()

            # Load all service providers
            self.__loadProviders()

            # Save configuration to cache if enabled
            self.__saveCache()

            # Lock and commit the configuration
            self.__commitConfig()

        # Register and boot all service providers
        self.__registerAndBootProvider(
            self.__bootstrap.get("providers", {}).get("eager", {})
        )

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
        # Check if already booted to prevent duplicate initialization
        if not self.__booted:

            # Register application instance in the container
            self.instance(
                IApplication,
                self,
                alias=f"x-{IApplication.__module__}.{IApplication.__name__}",
            )

            # Load and initialize all application components
            self.__load()

            # Mark application as fully booted
            self.__booted = True

        # Return the application instance for method chaining
        return self

    # --- CLI Kernel Handling Method ---

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
        # Initialize CLI kernel if not already cached
        if not self.__kernel_cli:

            # Retrieve CLI kernel configuration from bootstrap
            try:
                kernel_conf = self.__bootstrap["kernels"]["KernelCLI"]
            except KeyError:
                error_msg = "CLI Kernel is not configured in the application."
                raise RuntimeError(error_msg) from None

            # Instantiate the kernel class using configuration
            from orionis.services.introspection.modules.engine import ModuleEngine
            kernel_cls = ModuleEngine.resolveClass(
                kernel_conf["module"],
                kernel_conf["class"],
            )
            kernel_instance = kernel_cls(self)

            # Validate that the kernel has a callable handle method
            handle = getattr(kernel_instance, "handle", None)
            if not callable(handle):
                error_msg = "The CLI kernel does not have a handle method."
                raise TypeError(error_msg)

            # Cache the kernel handle method for future calls
            self.__kernel_cli = handle

        # Execute the kernel's handle method with provided arguments
        return self.__kernel_cli(args or [])

    # --- Runtime Configuration Access Methods ---

    def __getRuntimeConfigValue(
        self,
        key_parts: list[str],
    ) -> object:
        """
        Retrieve a value from a nested dictionary using dot notation.

        Parameters
        ----------
        key_parts : list[str]
            List of keys representing the path in the nested dictionary.

        Returns
        -------
        Any
            The value found at the nested key path, or None if not found.
        """
        cfg = self.__runtime_config
        for part in key_parts:
            if isinstance(cfg, dict) and part in cfg:
                cfg = cfg[part]
            else:
                return None
        return cfg

    def __setRuntimeConfigValue(
        self,
        key_parts: list[str],
        value: object,
    ) -> object:
        """
        Set a value in a nested dictionary using dot notation.

        Parameters
        ----------
        key_parts : list[str]
            List of keys representing the path in the nested dictionary.
        value : Any
            The value to set at the specified nested key path.

        Returns
        -------
        Any
            The value that was set.
        """
        current = self.__runtime_config
        for part in key_parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[key_parts[-1]] = value
        return value

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
        # Ensure configuration is initialized before accessing or modifying it
        if not self.__configured:
            error_msg = (
                "Application configuration is not initialized."
                "Please call create() first."
            )
            raise RuntimeError(error_msg)

        # Reset the runtime configuration to a mutable copy of the bootstrap config
        if not self.__runtime_config:
            self.resetRuntimeConfig()

        # Return the entire configuration if no key or value is provided
        if key is None and value is _SENTINEL:
            return self.__runtime_config

        # Ensure the key is a string
        if not isinstance(key, str):
            error_msg = "Configuration key must be a string."
            raise TypeError(error_msg)

        # Split the key into parts for nested access
        key_parts: list[str] = key.split(".")

        # If value is not provided, retrieve the configuration value
        if value is _SENTINEL:
            return self.__getRuntimeConfigValue(key_parts)

        # Otherwise, set the configuration value and return it
        return self.__setRuntimeConfigValue(key_parts, value)

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
        from copy import deepcopy
        from orionis.support.structures.freezer import FreezeThaw

        # Obtain current bootstrap configuration
        bootstrap_config = self.__bootstrap.get("config", {})

        # Deepcopy and unfreeze to ensure mutability and isolation
        self.__runtime_config = FreezeThaw.thaw(deepcopy(bootstrap_config))

        # Return True to indicate successful reset
        return True

    # --- Application Path Access Method ---

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

    # --- Environment Check Methods ---

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
        # Retrieve the current application environment from configuration
        app_env = self.config("app.env")

        # Ensure the application is booted before accessing configuration
        if app_env is None:
            error_msg = (
                "Application configuration is not initialized. Please call "
                "create() before checking the environment."
            )
            raise RuntimeError(error_msg)

        # Return True if the environment is 'production', otherwise False
        return "prod" in str(app_env).lower()

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
        # Retrieve the current debug setting from configuration
        app_debug = self.config("app.debug")

        # Raise if configuration is not initialized
        if app_debug is None:
            error_msg = (
                "Application configuration is not initialized. Please call "
                "create() before checking the debug mode."
            )
            raise RuntimeError(error_msg)

        # Return True if debug mode is enabled, otherwise False
        return bool(app_debug)
