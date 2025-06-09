from orionis.services.introspection.instances.reflection_instance import ReflectionInstance
from tests.support.inspection.fakes.fake_reflect_instance import FakeClass

async def getAlgo(num: int = 3) -> int:
    import asyncio
    await asyncio.sleep(3)
    return 123456789

reflec = ReflectionInstance(FakeClass())

reflec.setMethod('__getAlgos', getAlgo)
print(reflec.getMethodSignature('__getAlgos'))





