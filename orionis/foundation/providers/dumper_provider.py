from orionis.console.dumper.dump import Debug
from orionis.console.dumper.contracts.dump import IDebug
from orionis.container.providers.service_provider import ServiceProvider

class DumperProvider(ServiceProvider):
    """
    This provider is responsible for printing debug messages to the console.
    It offers methods to print debug messages, errors, and other types of information.
    """

    def register(self) -> None:
        """
        Register services into the application container.
        """
        self.app.transient(IDebug, Debug, alias="core.orionis.dumper")

    def boot(self) -> None:
        """
        Perform any post-registration bootstrapping or initialization.
        """
        pass