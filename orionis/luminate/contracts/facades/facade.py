from orionis.luminate.container.container import Container
from orionis.luminate.support.asyn_run import AsyncExecutor

class FacadeMeta(type):
    def __getattr__(cls, name):
        service = cls.resolve()
        return getattr(service, name)


# Clase base para las fachadas usando la metaclase
class Facade(metaclass=FacadeMeta):

    _container = Container()

    @classmethod
    def getFacadeAccessor(cls):
        raise NotImplementedError("Debes definir el nombre del servicio")

    @classmethod
    def resolve(cls):
        return AsyncExecutor.run(cls._container.make(cls.getFacadeAccessor()))