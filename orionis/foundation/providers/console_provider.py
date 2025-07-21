from orionis.console.output.console import Console
from orionis.console.output.contracts.console import IConsole
from orionis.container.providers.service_provider import ServiceProvider

class ConsoleProvider(ServiceProvider):
    """
    This provider is responsible for printing messages to the console.
    It supplies various methods to print messages of different types, such as information, warnings, errors, and debug messages.
    It also supports tables, confirmation data, passwords, and more at the console level.
    """

    def register(self) -> None:
        """
        Register services into the application container.
        """
        self.app.transient(IConsole, Console, alias="core.orionis.console")

    def boot(self) -> None:
        """
        Perform any post-registration bootstrapping or initialization.
        """
        pass