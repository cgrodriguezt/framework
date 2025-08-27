from app.services.welcome_service import WelcomeService
from orionis.console.args.argument import CLIArgument
from orionis.support.facades.reactor import Reactor

Reactor.command('app:test', [WelcomeService, 'simplePrint']).timestamp().description('Test command').arguments([
    CLIArgument(flags=["--name", "-n"], type=str, required=False)
])