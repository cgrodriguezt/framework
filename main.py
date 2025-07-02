from implementacion import AbstractFakeClass, FakeClass
from implementacion2 import Car, ICar
from orionis.container.container import Container
from orionis.container.contracts.container import IContainer

def ejemplo():
    return 1

contenedor = Container()
# contenedor.function('algo', ejemplo, lifetime='singleton')
# contenedor.transient(AbstractFakeClass, FakeClass)
contenedor.transient(ICar, Car)
# contenedor.singleton(AbstractFakeClass, FakeClass)
# contenedor.scoped(AbstractFakeClass, FakeClass)
# contenedor.instance(AbstractFakeClass, FakeClass())
# contenedor.function('esto', lambda x,y: x+y, lifetime='transient')

# contenedor.make(AbstractFakeClass, (Car(), 1))
# inst = contenedor.make(AbstractFakeClass, Car(1,2), edad=10, callback=1)
inst = contenedor.make(IContainer)
inst.singleton(AbstractFakeClass, FakeClass)
print(inst.make(AbstractFakeClass))