from implementacion import AbstractFakeClass, FakeClass
from implementacion2 import Car, ICar
from orionis.container.container import Container


container = Container()

with container.createContext():
    container.singleton(ICar, Car)
    container.scoped(AbstractFakeClass, FakeClass)
    print(container.make(AbstractFakeClass) is container.make(AbstractFakeClass))

with container.createContext():
    # container.scoped(ICar, Car)
    print(container.make(ICar) is container.make(ICar))