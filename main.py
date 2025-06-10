from orionis.services.introspection.instances.reflection_instance import ReflectionInstance
from tests.support.inspection.fakes.fake_reflect_instance import FakeClass

def getAlgo(num1, num2) -> int:
    return num1 + num2

reflec = ReflectionInstance(FakeClass())
print(reflec.getMethodSignature('__staticMethodSYNC'))
