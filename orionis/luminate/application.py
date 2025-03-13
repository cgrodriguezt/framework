from typing import Dict, List, Type
from orionis.luminate.contracts.application import IApplication
from orionis.luminate.contracts.container.container import IContainer
from orionis.luminate.contracts.foundation.bootstraper import IBootstrapper
from orionis.luminate.contracts.providers.service_provider import IServiceProvider
from orionis.luminate.container.container import Container
from orionis.luminate.foundation.config.config_bootstrapper import ConfigBootstrapper
from orionis.luminate.foundation.console.command_bootstrapper import CommandsBootstrapper
from orionis.luminate.foundation.environment.environment_bootstrapper import EnvironmentBootstrapper
from orionis.luminate.foundation.exceptions.exception_bootstrapper import BootstrapRuntimeError
from orionis.luminate.foundation.providers.service_providers_bootstrapper import ServiceProvidersBootstrapper
from orionis.luminate.patterns.singleton import SingletonMeta
from orionis.luminate.support.asyn_run import AsyncExecutor

class Application(metaclass=SingletonMeta):
    """
    Main application class that follows the Singleton pattern.

    This class manages service providers, environment variables, configurations,
    and commands for the application lifecycle.

    Attributes
    ----------
    _booted : bool
        Indicates whether the application has been booted.
    _custom_providers : List[Type[ServiceProvider]]
        Custom service providers defined by the developer.
    _service_providers : List[Type[ServiceProvider]]
        Core application service providers.
    _config : dict
        Configuration settings of the application.
    _commands : dict
        Registered console commands.
    _env : dict
        Environment variables.
    _container : IContainer
        The service container instance.
    """

    _booted: bool = False

    def __init__(self):
        """
        Initializes the application by setting up service providers, environment variables,
        configuration, and the service container.
        """
        self._custom_providers: List[Type[IServiceProvider]] = []
        self._service_providers: List[Type[IServiceProvider]] = []
        self._config: Dict = {}
        self._commands: Dict = {}
        self._env: Dict = {}
        self._container: IContainer = Container()

        # Register the application instance in the service container
        self._container.instance(IApplication, self)

    @classmethod
    def boot(cls) -> None:
        """
        Marks the application as booted.
        """
        cls._booted = True

    @classmethod
    def isRunning(cls) -> bool:
        """
        Checks if the application has been booted.

        Returns
        -------
        bool
            True if the application is running, otherwise False.
        """
        return cls._booted

    @classmethod
    def getInstance(cls) -> "Application":
        """
        Retrieves the singleton instance of the Application.

        Returns
        -------
        Application
            The current application instance.

        Raises
        ------
        RuntimeError
            If the application has not been initialized yet.
        """
        if cls not in SingletonMeta._instances:
            raise RuntimeError("Application has not been initialized yet. Please create an instance first.")
        return SingletonMeta._instances[cls]

    @classmethod
    def destroy(cls) -> None:
        """
        Destroys the singleton instance of the Application.
        """
        if cls in SingletonMeta._instances:
            del SingletonMeta._instances[cls]

    def withProviders(self, providers: List[Type[IServiceProvider]] = None) -> None:
        """
        Sets custom service providers.

        Parameters
        ----------
        providers : List[Type[IServiceProvider]], optional
            List of service providers, by default None.
        """
        self._custom_providers = providers or []

    def container(self) -> IContainer:
        """
        Returns the service container instance.

        Returns
        -------
        IContainer
            The service container.
        """
        return self._container

    def create(self) -> None:
        """
        Initializes and boots the application, including loading commands
        and service providers.
        """

        # Boot the application
        self._bootstrapping()

        # Load commands and service providers
        self._loadCommands()

        # Boot service providers
        AsyncExecutor.run(self._bootServiceProviders())

        # Change the application status to booted
        Application.boot()

    async def _bootServiceProviders(self) -> None:
        """
        Boots all registered service providers.
        """
        for service in self._service_providers:
            provider: IServiceProvider = service(app=self._container)
            provider.register()

            if hasattr(provider, 'boot') and callable(provider.boot):
                try:
                    await provider.boot()
                except Exception as e:
                    raise RuntimeError(f"Error booting service provider {service.__name__}: {e}") from e

    def _bootstrapping(self) -> None:
        """
        Loads essential components such as environment variables,
        configurations, commands, and service providers.
        """
        bootstrappers = [
            {'property': self._env, 'instance': EnvironmentBootstrapper()},
            {'property': self._config, 'instance': ConfigBootstrapper()},
            {'property': self._commands, 'instance': CommandsBootstrapper()},
            {'property': self._service_providers, 'instance': ServiceProvidersBootstrapper(self._custom_providers)},
        ]

        for bootstrapper in bootstrappers:
            try:
                property_ref: Dict = bootstrapper["property"]
                bootstrapper_instance: IBootstrapper = bootstrapper["instance"]
                if isinstance(property_ref, dict):
                    property_ref.update(bootstrapper_instance.get())
                elif isinstance(property_ref, list):
                    property_ref.extend(bootstrapper_instance.get())
                else:
                    property_ref = bootstrapper_instance.get()
            except Exception as e:
                raise BootstrapRuntimeError(f"Error bootstrapping {type(bootstrapper_instance).__name__}: {str(e)}") from e

    def _loadCommands(self) -> None:
        """
        Registers application commands in the service container.
        """
        for command, data_command in self._commands.items():
            self._container.transient(data_command.get('signature'), data_command.get('concrete'))