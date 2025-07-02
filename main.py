from implementacion import AbstractFakeClass, FakeClass
from implementacion2 import Car, ICar
from orionis.container.container import Container
from orionis.container.facades.facade import Facade


container = Container()
with container.createContext():
    container.transient(ICar, Car)
    container.scoped(AbstractFakeClass, FakeClass)
    print(container.make(AbstractFakeClass) is container.make(AbstractFakeClass))

    class FacadeCar(Facade):
        """
        Log Facade class. This is the friendly interface for interacting with the logging service.
        It's like the concierge of your application's logging system—always ready to help!
        """

        @classmethod
        def getFacadeAccessor(cls):
            """
            Returns the service accessor for the logging system. In this case, it's the `ILogguerService`.
            This is where the magic of the Facade pattern comes alive—connecting the interface to the actual service.
            """
            return ICar


    print(FacadeCar.resolve() is FacadeCar.resolve())