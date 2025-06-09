from orionis.services.introspection.instances.reflection_instance import ReflectionInstance
from tests.support.inspection.fakes.fake_reflect_instance import FakeClass

reflec = ReflectionInstance(FakeClass())
# print(reflec.getClassName())
# print(reflec.getClass())
# print(reflec.getModuleName())
# print(reflec.getModuleWithClassName())
# print(reflec.getPublicAttributes())
# print(reflec.getPrivateAttributes())
# print(reflec.getProtectedAttributes())
# print(reflec.getDunderAttributes())
# print(reflec.getAttributes())
# print(reflec.getPublicMethods())
# print(reflec.getPrivateMethods())
# print(reflec.getProtectedMethods())
# print(reflec.getDunderMethods())
# print(reflec.getClassMethods())
# print(reflec.getStaticMethods())
# print(reflec.getStaticSyncMethods())
# print(reflec.getStaticAsyncMethods())
# print(reflec.getPublicSyncMethods())
# print(reflec.getPublicAsyncMethods())
# print(reflec.getPrivateSyncMethods())
print(reflec.getProtectedClassMethods())










