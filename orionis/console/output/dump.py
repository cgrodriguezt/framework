from orionis.support.patterns.final.meta import Final
from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.pretty import Pretty
from rich.theme import Theme

class Dump(metaclass=Final):

    def __init__(self, data):
        self.data = data

    def render(self):
        import pprint
        return pprint.pformat(self.data)