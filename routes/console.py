from app.services.welcome_service import WelcomeService
from orionis.console.args.argument import CLIArgument
from orionis.support.facades.reactor import Reactor

# Example route for console commands
Reactor.command('app:test', [WelcomeService, 'helloWorld']).timestamp().description('Command Test Defined as Route').arguments([
    CLIArgument(flags=["--name", "-n"], type=str, required=False)
])