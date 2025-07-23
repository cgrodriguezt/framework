import time
from pathlib import Path
from typing import Any, List, Type
from orionis.container.container import Container
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.auth.entities.auth import Auth
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.cors.entities.cors import Cors
from orionis.foundation.config.database.entities.database import Database
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.queue.entities.queue import Queue
from orionis.foundation.config.session.entities.session import Session
from orionis.foundation.config.startup import Configuration
from orionis.foundation.config.testing.entities.testing import Testing
from orionis.foundation.contracts.application import IApplication
from orionis.foundation.contracts.config import IConfig
from orionis.foundation.exceptions import OrionisTypeError, OrionisRuntimeError
from orionis.foundation.providers.logger_provider import LoggerProvider

class Application(Container, IApplication):
    """
    Application container that manages service providers and application lifecycle.

    This class extends Container to provide application-level functionality including
    service provider management, kernel loading, and application bootstrapping.
    It implements a fluent interface pattern allowing method chaining.

    Attributes
    ----------
    isBooted : bool
        Read-only property indicating if the application has been booted
    """

    @property
    def isBooted(
        self
    ) -> bool:
        """
        Check if the application providers have been booted.

        Returns
        -------
        bool
            True if providers are booted, False otherwise
        """
        return self.__booted

    def __init__(
        self
    ) -> None:
        """
        Initialize the Application container.

        Sets up initial state including empty providers list and booted flag.
        Uses singleton pattern to prevent multiple initializations.
        """
        # Initialize base container with application paths
        super().__init__()

        # Singleton pattern - prevent multiple initializations
        if not hasattr(self, '_Application__initialized'):
            self.__providers: List[IServiceProvider, Any] = []
            self.__configurators : dict = {}
            self.__config: dict = {}
            self.__booted: bool = False
            self.__startAt = time.time_ns()

            # Flag to prevent re-initialization
            self.__initialized = True

    # << Frameworks Kernel >>

    def __loadFrameworksKernel(
        self
    ) -> None:
        """
        Load and register core framework kernels.

        Instantiates and registers kernel components:
        - TestKernel: Testing framework kernel
        """
        # Import core framework kernels
        from orionis.test.kernel import TestKernel, ITestKernel

        # Core framework kernels
        core_kernels = {
            ITestKernel: TestKernel
        }

        # Register each kernel instance
        for kernel_name, kernel_cls in core_kernels.items():
            self.instance(kernel_name, kernel_cls(self))

    # << Service Providers >>

    def __loadFrameworkProviders(
        self
    ) -> None:
        """
        Load core framework service providers.

        Registers essential providers required for framework operation
        """
        # Import core framework providers
        from orionis.foundation.providers.console_provider import ConsoleProvider
        from orionis.foundation.providers.dumper_provider import DumperProvider
        from orionis.foundation.providers.path_resolver_provider import PathResolverProvider
        from orionis.foundation.providers.progress_bar_provider import ProgressBarProvider
        from orionis.foundation.providers.workers_provider import WorkersProvider
        from orionis.foundation.providers.testing_provider import TestingProvider

        # Core framework providers
        core_providers = [
            ConsoleProvider,
            DumperProvider,
            PathResolverProvider,
            ProgressBarProvider,
            WorkersProvider,
            LoggerProvider,
            TestingProvider
        ]

        # Register each core provider
        for provider_cls in core_providers:
            self.addProvider(provider_cls)

    def __registerProviders(
        self
    ) -> None:
        """
        Register all added service providers.

        Calls the register method on each provider to bind services
        into the container.
        """

        # Ensure providers list is empty before registration
        initialized_providers = []

        # Iterate over each provider and register it
        for provider in self.__providers:

            # Initialize the provider
            class_provider: IServiceProvider = provider(self)

            # Register the provider in the container
            class_provider.register()

            # Add the initialized provider to the list
            initialized_providers.append(class_provider)

        # Update the providers list with initialized providers
        self.__providers = initialized_providers

    def __bootProviders(
        self
    ) -> None:
        """
        Boot all registered service providers.

        Calls the boot method on each provider to initialize services
        after all providers have been registered.
        """
        # Iterate over each provider and boot it
        for provider in self.__providers:

            # Ensure provider is initialized before calling boot
            if hasattr(provider, 'boot') and callable(getattr(provider, 'boot')):
                provider.boot()

    def withProviders(
        self,
        providers: List[Type[IServiceProvider]] = []
    ) -> 'Application':
        """
        Add multiple service providers to the application.

        Parameters
        ----------
        providers : List[Type[IServiceProvider]], optional
            List of provider classes to add to the application

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Add each provider class
        for provider_cls in providers:
            self.addProvider(provider_cls)

        # Return self instance for method chaining
        return self

    def addProvider(
        self,
        provider: Type[IServiceProvider]
    ) -> 'Application':
        """
        Add a single service provider to the application.

        Parameters
        ----------
        provider : Type[IServiceProvider]
            The provider class to add to the application

        Returns
        -------
        Application
            The application instance for method chaining

        Raises
        ------
        OrionisTypeError
            If provider is not a subclass of IServiceProvider
        """

        # Validate provider type
        if not isinstance(provider, type) or not issubclass(provider, IServiceProvider):
            raise OrionisTypeError(f"Expected IServiceProvider class, got {type(provider).__name__}")

        # Add the provider to the list
        if provider not in self.__providers:
            self.__providers.append(provider)

        # If already added, raise an error
        else:
            raise OrionisTypeError(f"Provider {provider.__name__} is already registered.")

        # Return self instance.
        return self

    # << Paths >>

    def setConsoleSchedulerPath(
        self,
        path: str
    ) -> 'Application':
        """
        Set the console scheduler path for the application.

        Parameters
        ----------
        path : str
            The path to set for the console scheduler

        Returns
        -------
        Application
            The application instance for method chaining
        """

        if not isinstance(path, str):
            raise OrionisTypeError(f"Expected string path, got {type(path).__name__}")

        self.__configurators['paths']['console_scheduler'] = path

        # Return self instance for method chaining
        return self

    # << Configuration >>

    def __loadConfig(
        self,
    ) -> None:
        """
        Retrieve a configuration value by key.

        Returns
        -------
        None
            Initializes the application configuration if not already set.
        """

        # Try to load the configuration
        try:

            # Check if configuration is a dictionary
            if not self.__config:

                # Initialize with default configuration
                if not self.__configurators:
                    self.__config = Configuration().toDict()

                # Convert configurators to a dictionary
                else:
                    self.__config = Configuration(**self.__configurators).toDict()

        except Exception as e:

            # Handle any exceptions during configuration loading
            raise OrionisRuntimeError(f"Failed to load application configuration: {str(e)}")

    def withConfigurators(
        self,
        *,
        app: App | dict = App(),
        auth: Auth | dict = Auth(),
        cache : Cache | dict = Cache(),
        cors : Cors | dict = Cors(),
        database : Database | dict = Database(),
        filesystems : Filesystems | dict = Filesystems(),
        logging : Logging | dict = Logging(),
        mail : Mail | dict = Mail(),
        queue : Queue | dict = Queue(),
        session : Session | dict = Session(),
        testing : Testing | dict = Testing()
    ) -> 'Application':
        """
        Configure the application with various service configurators.
        This method allows you to set up different aspects of the application by providing
        configurator instances for various services like authentication, caching, database,
        etc. If no configurator is provided for a service, a default instance will be created.
        Parameters
        ----------
        app : App, optional
            Application configurator instance. If None, creates a default App() instance.
        auth : Auth, optional
            Authentication configurator instance. If None, creates a default Auth() instance.
        cache : Cache, optional
            Cache configurator instance. If None, creates a default Cache() instance.
        cors : Cors, optional
            CORS configurator instance. If None, creates a default Cors() instance.
        database : Database, optional
            Database configurator instance. If None, creates a default Database() instance.
        filesystems : Filesystems, optional
            Filesystems configurator instance. If None, creates a default Filesystems() instance.
        logging : Logging, optional
            Logging configurator instance. If None, creates a default Logging() instance.
        mail : Mail, optional
            Mail configurator instance. If None, creates a default Mail() instance.
        queue : Queue, optional
            Queue configurator instance. If None, creates a default Queue() instance.
        session : Session, optional
            Session configurator instance. If None, creates a default Session() instance.
        testing : Testing, optional
            Testing configurator instance. If None, creates a default Testing() instance.
        Returns
        -------
        Application
            Returns self to allow method chaining.
        """

        # Load app configurator
        if not isinstance(app, (App, dict)):
            raise OrionisTypeError(f"Expected App instance or dict, got {type(app).__name__}")
        self.loadConfigApp(app)

        # Load auth configurator
        if not isinstance(auth, (Auth, dict)):
            raise OrionisTypeError(f"Expected Auth instance or dict, got {type(auth).__name__}")
        self.loadConfigAuth(auth)

        # Load cache configurator
        if not isinstance(cache, (Cache, dict)):
            raise OrionisTypeError(f"Expected Cache instance or dict, got {type(cache).__name__}")
        self.loadConfigCache(cache)

        # Load cors configurator
        if not isinstance(cors, (Cors, dict)):
            raise OrionisTypeError(f"Expected Cors instance or dict, got {type(cors).__name__}")
        self.loadConfigCors(cors)

        # Load database configurator
        if not isinstance(database, (Database, dict)):
            raise OrionisTypeError(f"Expected Database instance or dict, got {type(database).__name__}")
        self.loadConfigDatabase(database)

        # Load filesystems configurator
        if not isinstance(filesystems, (Filesystems, dict)):
            raise OrionisTypeError(f"Expected Filesystems instance or dict, got {type(filesystems).__name__}")
        self.loadConfigFilesystems(filesystems)

        # Load logging configurator
        if not isinstance(logging, (Logging, dict)):
            raise OrionisTypeError(f"Expected Logging instance or dict, got {type(logging).__name__}")
        self.loadConfigLogging(logging)

        # Load mail configurator
        if not isinstance(mail, (Mail, dict)):
            raise OrionisTypeError(f"Expected Mail instance or dict, got {type(mail).__name__}")
        self.loadConfigMail(mail)

        # Load queue configurator
        if not isinstance(queue, (Queue, dict)):
            raise OrionisTypeError(f"Expected Queue instance or dict, got {type(queue).__name__}")
        self.loadConfigQueue(queue)

        # Load session configurator
        if not isinstance(session, (Session, dict)):
            raise OrionisTypeError(f"Expected Session instance or dict, got {type(session).__name__}")
        self.loadConfigSession(session)

        # Load testing configurator
        if not isinstance(testing, (Testing, dict)):
            raise OrionisTypeError(f"Expected Testing instance or dict, got {type(testing).__name__}")
        self.loadConfigTesting(testing)

        # Return self instance for method chaining
        return self

    def setConfigApp(
        self,
        **app_config
    ) -> 'Application':
        """
        Configure the application with various settings.

        Parameters
        ----------
        **app_config : dict
            Configuration parameters for the application. Must match the fields
            expected by the App dataclass (orionis.foundation.config.app.entities.app.App).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create App instance with provided parameters
        app = App(**app_config)

        # Load configuration using App instance
        self.loadConfigApp(app)

        # Return the application instance for method chaining
        return self

    def loadConfigApp(
        self,
        app: App | dict
    ) -> 'Application':
        """
        Load the application configuration from an App instance.

        Parameters
        ----------
        config : App | dict
            The App instance or dictionary containing application configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate app type
        if not isinstance(app, (App, dict)):
            raise OrionisTypeError(f"Expected App instance or dict, got {type(app).__name__}")

        # If app is a dict, convert it to App instance
        if isinstance(app, dict):
            app = App(**app)

        # Store the configuration
        self.__configurators['app'] = app

        # Return the application instance for method chaining
        return self

    def setConfigAuth(
        self,
        **auth_config
    ) -> 'Application':
        """
        Configure the authentication with various settings.

        Parameters
        ----------
        **auth_config : dict
            Configuration parameters for authentication. Must match the fields
            expected by the Auth dataclass (orionis.foundation.config.auth.entities.auth.Auth).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Auth instance with provided parameters
        auth = Auth(**auth_config)

        # Load configuration using Auth instance
        self.loadConfigAuth(auth)

        # Return the application instance for method chaining
        return self

    def loadConfigAuth(
        self,
        auth: Auth | dict
    ) -> 'Application':
        """
        Load the application authentication configuration from an Auth instance.

        Parameters
        ----------
        auth : Auth | dict
            The Auth instance or dictionary containing authentication configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate auth type
        if not isinstance(auth, (Auth, dict)):
            raise OrionisTypeError(f"Expected Auth instance or dict, got {type(auth).__name__}")

        # If auth is a dict, convert it to Auth instance
        if isinstance(auth, dict):
            auth = Auth(**auth)

        # Store the configuration
        self.__configurators['auth'] = auth

        # Return the application instance for method chaining
        return self

    def setConfigCache(
        self,
        **cache_config
    ) -> 'Application':
        """
        Configure the cache with various settings.

        Parameters
        ----------
        **cache_config : dict
            Configuration parameters for cache. Must match the fields
            expected by the Cache dataclass (orionis.foundation.config.cache.entities.cache.Cache).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Cache instance with provided parameters
        cache = Cache(**cache_config)

        # Load configuration using Cache instance
        self.loadConfigCache(cache)

        # Return the application instance for method chaining
        return self

    def loadConfigCache(
        self,
        cache: Cache | dict
    ) -> 'Application':
        """
        Load the application cache configuration from a Cache instance.

        Parameters
        ----------
        cache : Cache | dict
            The Cache instance or dictionary containing cache configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate cache type
        if not isinstance(cache, (Cache, dict)):
            raise OrionisTypeError(f"Expected Cache instance or dict, got {type(cache).__name__}")

        # If cache is a dict, convert it to Cache instance
        if isinstance(cache, dict):
            cache = Cache(**cache)

        # Store the configuration
        self.__configurators['cache'] = cache

        # Return the application instance for method chaining
        return self

    def setConfigCors(
        self,
        **cors_config
    ) -> 'Application':
        """
        Configure the CORS with various settings.

        Parameters
        ----------
        **cors_config : dict
            Configuration parameters for CORS. Must match the fields
            expected by the Cors dataclass (orionis.foundation.config.cors.entities.cors.Cors).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Cors instance with provided parameters
        cors = Cors(**cors_config)

        # Load configuration using Cors instance
        self.loadConfigCors(cors)

        # Return the application instance for method chaining
        return self

    def loadConfigCors(
        self,
        cors: Cors | dict
    ) -> 'Application':
        """
        Load the application CORS configuration from a Cors instance.

        Parameters
        ----------
        cors : Cors | dict
            The Cors instance or dictionary containing CORS configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate cors type
        if not isinstance(cors, (Cors, dict)):
            raise OrionisTypeError(f"Expected Cors instance or dict, got {type(cors).__name__}")

        # If cors is a dict, convert it to Cors instance
        if isinstance(cors, dict):
            cors = Cors(**cors)

        # Store the configuration
        self.__configurators['cors'] = cors

        # Return the application instance for method chaining
        return self

    def setConfigDatabase(
        self,
        **database_config
    ) -> 'Application':
        """
        Configure the database with various settings.

        Parameters
        ----------
        **database_config : dict
            Configuration parameters for database. Must match the fields
            expected by the Database dataclass (orionis.foundation.config.database.entities.database.Database).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Database instance with provided parameters
        database = Database(**database_config)

        # Load configuration using Database instance
        self.loadConfigDatabase(database)

        # Return the application instance for method chaining
        return self

    def loadConfigDatabase(
        self,
        database: Database | dict
    ) -> 'Application':
        """
        Load the application database configuration from a Database instance.

        Parameters
        ----------
        database : Database | dict
            The Database instance or dictionary containing database configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate database type
        if not isinstance(database, (Database, dict)):
            raise OrionisTypeError(f"Expected Database instance or dict, got {type(database).__name__}")

        # If database is a dict, convert it to Database instance
        if isinstance(database, dict):
            database = Database(**database)

        # Store the configuration
        self.__configurators['database'] = database

        # Return the application instance for method chaining
        return self

    def setConfigFilesystems(
        self,
        **filesystems_config
    ) -> 'Application':
        """
        Configure the filesystems with various settings.

        Parameters
        ----------
        **filesystems_config : dict
            Configuration parameters for filesystems. Must match the fields
            expected by the Filesystems dataclass (orionis.foundation.config.filesystems.entitites.filesystems.Filesystems).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Filesystems instance with provided parameters
        filesystems = Filesystems(**filesystems_config)

        # Load configuration using Filesystems instance
        self.loadConfigFilesystems(filesystems)

        # Return the application instance for method chaining
        return self

    def loadConfigFilesystems(
        self,
        filesystems: Filesystems | dict
    ) -> 'Application':
        """
        Load the application filesystems configuration from a Filesystems instance.

        Parameters
        ----------
        filesystems : Filesystems | dict
            The Filesystems instance or dictionary containing filesystems configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate filesystems type
        if not isinstance(filesystems, (Filesystems, dict)):
            raise OrionisTypeError(f"Expected Filesystems instance or dict, got {type(filesystems).__name__}")

        # If filesystems is a dict, convert it to Filesystems instance
        if isinstance(filesystems, dict):
            filesystems = Filesystems(**filesystems)

        # Store the configuration
        self.__configurators['filesystems'] = filesystems

        # Return the application instance for method chaining
        return self

    def setConfigLogging(
        self,
        **logging_config
    ) -> 'Application':
        """
        Configure the logging system with various channel settings.

        Parameters
        ----------
        **logging_config : dict
            Configuration parameters for logging. Must match the fields
            expected by the Logging dataclass (orionis.foundation.config.logging.entities.logging.Logging).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Logging instance with provided parameters
        logging = Logging(**logging_config)

        # Load configuration using Logging instance
        self.loadConfigLogging(logging)

        # Return the application instance for method chaining
        return self

    def loadConfigLogging(
        self,
        logging: Logging | dict
    ) -> 'Application':
        """
        Load the application logging configuration from a Logging instance.

        Parameters
        ----------
        logging : Logging | dict
            The Logging instance or dictionary containing logging configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate logging type
        if not isinstance(logging, (Logging, dict)):
            raise OrionisTypeError(f"Expected Logging instance or dict, got {type(logging).__name__}")

        # If logging is a dict, convert it to Logging instance
        if isinstance(logging, dict):
            logging = Logging(**logging)

        # Store the configuration
        self.__configurators['logging'] = logging

        # Return the application instance for method chaining
        return self

    def setConfigMail(
        self,
        **mail_config
    ) -> 'Application':
        """
        Configure the mail system with various settings.

        Parameters
        ----------
        **mail_config : dict
            Configuration parameters for mail. Must match the fields
            expected by the Mail dataclass (orionis.foundation.config.mail.entities.mail.Mail).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Mail instance with provided parameters
        mail = Mail(**mail_config)

        # Load configuration using Mail instance
        self.loadConfigMail(mail)

        # Return the application instance for method chaining
        return self

    def loadConfigMail(
        self,
        mail: Mail | dict
    ) -> 'Application':
        """
        Load the application mail configuration from a Mail instance.

        Parameters
        ----------
        mail : Mail | dict
            The Mail instance or dictionary containing mail configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate mail type
        if not isinstance(mail, (Mail, dict)):
            raise OrionisTypeError(f"Expected Mail instance or dict, got {type(mail).__name__}")

        # If mail is a dict, convert it to Mail instance
        if isinstance(mail, dict):
            mail = Mail(**mail)

        # Store the configuration
        self.__configurators['mail'] = mail

        # Return the application instance for method chaining
        return self

    def setConfigQueue(
        self,
        **queue_config
    ) -> 'Application':
        """
        Configure the queue system with various settings.

        Parameters
        ----------
        **queue_config : dict
            Configuration parameters for queue. Must match the fields
            expected by the Queue dataclass (orionis.foundation.config.queue.entities.queue.Queue).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Queue instance with provided parameters
        queue = Queue(**queue_config)

        # Load configuration using Queue instance
        self.loadConfigQueue(queue)

        # Return the application instance for method chaining
        return self

    def loadConfigQueue(
        self,
        queue: Queue | dict
    ) -> 'Application':
        """
        Load the application queue configuration from a Queue instance.

        Parameters
        ----------
        queue : Queue
            The Queue instance containing queue configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate queue type
        if not isinstance(queue, (Queue, dict)):
            raise OrionisTypeError(f"Expected Queue instance or dict, got {type(queue).__name__}")

        # If queue is a dict, convert it to Queue instance
        if isinstance(queue, dict):
            queue = Queue(**queue)

        # Store the configuration
        self.__configurators['queue'] = queue

        # Return the application instance for method chaining
        return self

    def setConfigSession(
        self,
        **session_config
    ) -> 'Application':
        """
        Configure the session with various settings.

        Parameters
        ----------
        **session_config : dict
            Configuration parameters for session. Must match the fields
            expected by the Session dataclass (orionis.foundation.config.session.entities.session.Session).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Session instance with provided parameters
        session = Session(**session_config)

        # Load configuration using Session instance
        self.loadConfigSession(session)

        # Return the application instance for method chaining
        return self

    def loadConfigSession(
        self,
        session: Session | dict
    ) -> 'Application':
        """
        Load the application session configuration from a Session instance.

        Parameters
        ----------
        session : Session | dict
            The Session instance or dictionary containing session configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate session type
        if not isinstance(session, (Session, dict)):
            raise OrionisTypeError(f"Expected Session instance or dict, got {type(session).__name__}")

        # If session is a dict, convert it to Session instance
        if isinstance(session, dict):
            session = Session(**session)

        # Store the configuration
        self.__configurators['session'] = session

        # Return the application instance for method chaining
        return self

    def setConfigTesting(
        self,
        **testing_config
    ) -> 'Application':
        """
        Configure the testing with various settings.

        Parameters
        ----------
        **testing_config : dict
            Configuration parameters for testing. Must match the fields
            expected by the Testing dataclass (orionis.foundation.config.testing.entities.testing.Testing).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Testing instance with provided parameters
        testing = Testing(**testing_config)

        # Load configuration using Testing instance
        self.loadConfigTesting(testing)

        # Return the application instance for method chaining
        return self

    def loadConfigTesting(
        self,
        testing: Testing | dict
    ) -> 'Application':
        """
        Load the application testing configuration from a Testing instance.

        Parameters
        ----------
        testing : Testing | dict
            The Testing instance or dictionary containing testing configuration.

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate testing type
        if not isinstance(testing, (Testing, dict)):
            raise OrionisTypeError(f"Expected Testing instance or dict, got {type(testing).__name__}")

        # If testing is a dict, convert it to Testing instance
        if isinstance(testing, dict):
            testing = Testing(**testing)

        # Store the configuration
        self.__configurators['testing'] = testing

        # Return the application instance for method chaining
        return self

    # << Application Lifecycle >>

    def create(
        self
    ) -> 'Application':
        """
        Bootstrap the application by loading providers and kernels.

        Returns
        -------
        Application
            The application instance for method chaining
        """
        # Check if already booted
        if not self.__booted:

            # Load configuration if not already set
            self.__loadConfig()

            # Load framework providers and register them
            self.__loadFrameworkProviders()
            self.__registerProviders()
            self.__bootProviders()

            # Load core framework kernels
            self.__loadFrameworksKernel()

            # Mark as booted
            self.__booted = True

        return self

    # << Configuration Access >>

    def config(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Retrieve a configuration value by key.

        Parameters
        ----------
        key : str
            The configuration key to retrieve using dot notation (e.g. "app.name") (default is None)
        default : Any, optional
            Default value to return if key is not found

        Returns
        -------
        Any
            The configuration value or the entire configuration if key is None
        """

        # Ensure the application is booted before accessing configuration
        if not self.__config:
            raise RuntimeError("Application must be booted before accessing configuration. Call create() first.")

        # If key is None, raise an error to prevent ambiguity
        if key is None:
            raise ValueError("Key cannot be None. Use config() without arguments to get the entire configuration.")

        # Split the key by dot notation
        parts = key.split('.')

        # Start with the full config
        config_value = self.__config

        # Traverse the config dictionary based on the key parts
        for part in parts:

            # If part is not in config_value, return default
            if isinstance(config_value, dict) and part in config_value:
                config_value = config_value[part]

            # If part is not found, return default value
            else:
                return default

        # Return the final configuration value
        return config_value

    # << Path Configuration Access >>

    def path(
        self,
        key: str,
        default: str = None
    ) -> Path:
        """
        Retrieve a path configuration value by key.

        Parameters
        ----------
        key : str
            The path key to retrieve using dot notation (e.g. "paths.storage")
        default : str, optional
            Default value to return if key is not found

        Returns
        -------
        Path
            The path value as a Path object or None if not found
        """

        # Ensure the application is booted before accessing configuration
        if not self.__booted:
            raise RuntimeError("Application must be booted before accessing configuration. Call create() first.")

        # If key is None, raise an error to prevent ambiguity
        if key is None:
            raise ValueError("Key cannot be None. Use path() without arguments to get the entire configuration.")

        # Get the configuration value for the given key
        original_paths = self.config('paths')

        # If original_paths is not a dictionary, return the default value as Path
        if not isinstance(original_paths, dict):
            return Path(default) if default is not None else None

        # Get the path value from the dictionary
        path_value = original_paths.get(key, default)

        # Return as Path object if value exists, otherwise return None
        return Path(path_value) if path_value is not None else None