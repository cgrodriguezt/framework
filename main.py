from implementacion import AbstractFakeClass, FakeClass

from orionis.container.container import Container
contenedor = Container()
contenedor.transient(FakeClass, FakeClass)

