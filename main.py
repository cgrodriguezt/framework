from orionis.services.introspection.concretes.reflection_concrete import ReflectionConcrete
from orionis.services.introspection.instances.reflection_instance import ReflectionInstance
from tests.support.inspection.fakes.fake_reflect_instance import FakeClass

def sum(cls:FakeClass, a, b):
    return cls.instanceSyncMethod(a, b)

print("------------------------------------------------------------")

rf1 = ReflectionInstance(FakeClass())
print(rf1.getMethodDependencies('instanceSyncMethod'))

print("------------------------------------------------------------")

rf = ReflectionConcrete(FakeClass)
print(rf.getMethodDependencies('instanceSyncMethod'))

print("------------------------------------------------------------")
