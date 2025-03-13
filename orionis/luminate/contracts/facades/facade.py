from orionis.luminate.container.container import Container

class Facade:

    _container = Container()

    @classmethod
    def resolve(cls):
        if not hasattr(cls, "_service"):
            raise ValueError(f"Facade class {cls.__name__} does not define _service attribute.")
        return cls._container.make(cls._service)

    @classmethod
    def __getattr__(cls, name):
        service = cls.resolve()
        if hasattr(service, name):
            return getattr(service, name)
        raise AttributeError(f"'{cls.__name__}' object has no method '{name}'")