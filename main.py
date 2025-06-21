# from orionis.container.enums.lifetimes import Lifetime

# for member in Lifetime:
#     print(member.name)

class Lifetime:
    pass

from orionis.container.container import Container
contenedor = Container()
contenedor.transient(Lifetime, Lifetime)

