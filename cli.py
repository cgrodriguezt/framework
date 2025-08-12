import sys
from main import app
from orionis.console.core.reactor import Reactor

reactor = Reactor()
reactor.call('app:inspire', sys.argv[1:])
