from app.services.welcome_service import WelcomeService
from orionis.console.args.argument import CLIArgument
from orionis.support.facades.reactor import Reactor

# Example console command definition
Reactor.command("app:test", [WelcomeService, "greetUser"]).timestamp().description("Command Test Defined as Route").arguments([
    CLIArgument(flags=["--name", "-n"], type=str, required=False),
])
