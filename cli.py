# import sys
# from main import app
# from orionis.console.core.reactor import Reactor

# reactor = Reactor()
# reactor.call('app:inspire', sys.argv[1:])

from orionis.services.introspection.dependencies.reflection import ReflectDependencies


class Mafe:
    def __init__(self):
        pass

class Raul:

    def __init__(self, apto,  esposa: Mafe, edad: int = 30):
        self.esposa = esposa

    def metodo(self, a: int, c: Mafe, b: str = 'hola'):
        pass

rf = ReflectDependencies(Raul)
print(rf.getMethodDependencies('metodo').toDict())