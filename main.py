from implementacion import AbstractFakeClass, FakeClass

from orionis.container.container import Container
contenedor = Container()
contenedor.bind(abstract=AbstractFakeClass, concrete=FakeClass)

