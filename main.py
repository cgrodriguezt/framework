# from implementacion import AbstractFakeClass, FakeClass
# from orionis.container.container import Container

# contenedor = Container()
# contenedor.transient(AbstractFakeClass, FakeClass)
# # contenedor.singleton(AbstractFakeClass, FakeClass)
# # contenedor.scoped(AbstractFakeClass, FakeClass)
# # contenedor.instance(AbstractFakeClass, FakeClass())
# contenedor.function('esto', lambda x,y: x+y, lifetime='transient')

# contenedor.make(AbstractFakeClass)


from orionis.services.introspection.callables.reflection_callable import ReflectionCallable
import asyncio


async def fake_function(x: int = 3, y: int = 4) -> int:
    """Asynchronously adds two integers with a short delay."""
    await asyncio.sleep(0.1)
    return x + y

def fake_function_sync(x: int, y: int) -> int:
    """Synchronously adds two integers."""
    return x + y

def fake_function_sync2(x: int, y: int) -> int:
    """Synchronously multiplies two integers."""
    return x * y

rf_call = ReflectionCallable(fake_function)
print(rf_call.getDependencies())