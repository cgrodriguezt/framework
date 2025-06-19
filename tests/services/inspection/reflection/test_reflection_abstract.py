from orionis.services.introspection.abstract.reflection_abstract import ReflectionAbstract
from orionis.services.introspection.dependencies.entities.class_dependencies import ClassDependency
from tests.services.inspection.reflection.mock.fake_reflect_instance import AbstractFakeClass
from orionis.unittesting import TestCase

class TestServiceReflectionAbstract(TestCase):

    async def testGetClass(self):
        """
        Verifica que getClass retorna la clase correcta.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        cls = reflect.getClass()
        self.assertEqual(cls, AbstractFakeClass)

    async def testGetClassName(self):
        """
        Verifica que getClassName retorna el nombre de la clase.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        class_name = reflect.getClassName()
        self.assertEqual(class_name, 'AbstractFakeClass')

    async def testGetModuleName(self):
        """
        Verifica que getModuleName retorna el nombre del módulo.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        module_name = reflect.getModuleName()
        self.assertEqual(module_name, 'tests.services.inspection.reflection.mock.fake_reflect_instance')

    async def testGetModuleWithClassName(self):
        """
        Verifica que getModuleWithClassName retorna el módulo y nombre de la clase.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        module_with_class_name = reflect.getModuleWithClassName()
        self.assertEqual(module_with_class_name, 'tests.services.inspection.reflection.mock.fake_reflect_instance.AbstractFakeClass')

    async def testGetDocstring(self):
        """
        Verifica que getDocstring retorna el docstring de la clase.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        docstring = reflect.getDocstring()
        self.assertEqual(docstring, AbstractFakeClass.__doc__)

    async def testGetBaseClasses(self):
        """
        Verifica que getBaseClasses retorna las clases base.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        base_classes = reflect.getBaseClasses()
        self.assertIn(AbstractFakeClass.__base__, base_classes)

    async def testGetSourceCode(self):
        """
        Verifica que getSourceCode retorna el código fuente de la clase.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        source_code = reflect.getSourceCode()
        self.assertTrue(source_code.startswith('class AbstractFakeClass'))

    async def testGetFile(self):
        """
        Verifica que getFile retorna la ruta del archivo de la clase.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        file_path = reflect.getFile()
        self.assertTrue(file_path.endswith('fake_reflect_instance.py'))

    async def testGetAnnotations(self):
        """
        Verifica que getAnnotations retorna las anotaciones de la clase.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        annotations = reflect.getAnnotations()
        self.assertIn('public_attr', annotations)

    async def testHasAttribute(self):
        """
        Verifica que hasAttribute identifica atributos existentes.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        self.assertTrue(reflect.hasAttribute('public_attr'))
        self.assertFalse(reflect.hasAttribute('non_existent_attr'))

    async def testGetAttribute(self):
        """
        Verifica que getAttribute obtiene el valor correcto de un atributo.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        self.assertEqual(reflect.getAttribute('public_attr'), 42)
        self.assertIsNone(reflect.getAttribute('non_existent_attr'))

    async def testSetAttribute(self):
        """
        Verifica que setAttribute modifica atributos correctamente.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        self.assertTrue(reflect.setAttribute('name', 'Orionis Framework'))
        self.assertEqual(reflect.getAttribute('name'), 'Orionis Framework')
        self.assertTrue(reflect.setAttribute('_version', '1.x'))
        self.assertEqual(reflect.getAttribute('_version'), '1.x')
        self.assertTrue(reflect.setAttribute('__python', '3.13+'))
        self.assertEqual(reflect.getAttribute('__python'), '3.13+')

    async def testRemoveAttribute(self):
        """
        Verifica que removeAttribute elimina atributos correctamente.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        reflect.setAttribute('new_attr', 100)
        self.assertTrue(reflect.removeAttribute('new_attr'))
        self.assertFalse(reflect.hasAttribute('new_attr'))

    async def testGetAttributes(self):
        """
        Verifica que getAttributes retorna todos los atributos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        attributes = reflect.getAttributes()
        self.assertIn('public_attr', attributes)
        self.assertIn('_protected_attr', attributes)
        self.assertIn('__private_attr', attributes)

    async def testGetPublicAttributes(self):
        """
        Verifica que getPublicAttributes retorna solo los atributos públicos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_attributes = reflect.getPublicAttributes()
        self.assertIn('public_attr', public_attributes)
        self.assertNotIn('_protected_attr', public_attributes)
        self.assertNotIn('__private_attr', public_attributes)

    async def testGetProtectedAttributes(self):
        """
        Verifica que getProtectedAttributes retorna solo los atributos protegidos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_attributes = reflect.getProtectedAttributes()
        self.assertIn('_protected_attr', protected_attributes)
        self.assertNotIn('public_attr', protected_attributes)
        self.assertNotIn('__private_attr', protected_attributes)

    async def testGetPrivateAttributes(self):
        """
        Verifica que getPrivateAttributes retorna solo los atributos privados.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_attributes = reflect.getPrivateAttributes()
        self.assertIn('__private_attr', private_attributes)
        self.assertNotIn('public_attr', private_attributes)
        self.assertNotIn('_protected_attr', private_attributes)

    async def testGetDunderAttributes(self):
        """
        Verifica que getDunderAttributes retorna los atributos dunder.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        dunder_attributes = reflect.getDunderAttributes()
        self.assertIn('__dd__', dunder_attributes)

    async def testGetMagicAttributes(self):
        """
        Verifica que getMagicAttributes retorna los atributos mágicos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        magic_attributes = reflect.getMagicAttributes()
        self.assertIn('__dd__', magic_attributes)

    async def testHasMethod(self):
        """
        Verifica que hasMethod identifica métodos existentes.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        self.assertTrue(reflect.hasMethod('instanceSyncMethod'))
        self.assertFalse(reflect.hasMethod('non_existent_method'))

    async def testCallMethod(self):
        """
        Verifica que callMethod ejecuta métodos correctamente.
        """
        # No aplica para ReflectionAbstract, se omite

    async def testCallAsyncMethod(self):
        """
        Verifica que callMethod ejecuta métodos asíncronos correctamente.
        """
        # No aplica para ReflectionAbstract, se omite

    async def testSetMethod(self):
        """
        Verifica que setMethod asigna métodos correctamente.
        """
        # No aplica para ReflectionAbstract, se omite

    async def testRemoveMethod(self):
        """
        Verifica que removeMethod elimina métodos correctamente.
        """
        # No aplica para ReflectionAbstract, se omite

    async def testGetMethodSignature(self):
        """
        Verifica que getMethodSignature retorna la firma del método.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        signature = reflect.getMethodSignature('instanceSyncMethod')
        self.assertEqual(str(signature), '(self, x: int, y: int) -> int')

    async def testGetMethods(self):
        """
        Verifica que getMethods retorna los métodos de la clase.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        methods = reflect.getMethods()
        self.assertIn('instanceSyncMethod', methods)
        self.assertIn('instanceAsyncMethod', methods)

    async def testGetPublicMethods(self):
        """
        Verifica que getPublicMethods retorna solo los métodos públicos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_methods = reflect.getPublicMethods()
        self.assertIn('instanceSyncMethod', public_methods)
        self.assertNotIn('_protected_method', public_methods)
        self.assertNotIn('__private_method', public_methods)

    async def testGetPublicSyncMethods(self):
        """
        Verifica que getPublicSyncMethods retorna solo los métodos públicos síncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_sync_methods = reflect.getPublicSyncMethods()
        self.assertIn('instanceSyncMethod', public_sync_methods)
        self.assertNotIn('_protected_method', public_sync_methods)
        self.assertNotIn('__private_method', public_sync_methods)

    async def testGetPublicAsyncMethods(self):
        """
        Verifica que getPublicAsyncMethods retorna solo los métodos públicos asíncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_async_methods = reflect.getPublicAsyncMethods()
        self.assertIn('instanceAsyncMethod', public_async_methods)
        self.assertNotIn('_protected_async_method', public_async_methods)
        self.assertNotIn('__private_async_method', public_async_methods)

    async def testGetProtectedMethods(self):
        """
        Verifica que getProtectedMethods retorna solo los métodos protegidos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_methods = reflect.getProtectedMethods()
        self.assertIn('_protectedAsyncMethod', protected_methods)
        self.assertNotIn('instanceSyncMethod', protected_methods)
        self.assertNotIn('__privateSyncMethod', protected_methods)

    async def testGetProtectedSyncMethods(self):
        """
        Verifica que getProtectedSyncMethods retorna solo los métodos protegidos síncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_sync_methods = reflect.getProtectedSyncMethods()
        self.assertIn('_protectedsyncMethod', protected_sync_methods)
        self.assertNotIn('instanceAsyncMethod', protected_sync_methods)
        self.assertNotIn('__privateSyncMethod', protected_sync_methods)

    async def testGetProtectedAsyncMethods(self):
        """
        Verifica que getProtectedAsyncMethods retorna solo los métodos protegidos asíncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_async_methods = reflect.getProtectedAsyncMethods()
        self.assertIn('_protectedAsyncMethod', protected_async_methods)
        self.assertNotIn('instanceSyncMethod', protected_async_methods)
        self.assertNotIn('__privateSyncMethod', protected_async_methods)

    async def testGetPrivateMethods(self):
        """
        Verifica que getPrivateMethods retorna solo los métodos privados.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_methods = reflect.getPrivateMethods()
        self.assertIn('__privateSyncMethod', private_methods)
        self.assertNotIn('instanceSyncMethod', private_methods)
        self.assertNotIn('_protectedAsyncMethod', private_methods)

    async def testGetPrivateSyncMethods(self):
        """
        Verifica que getPrivateSyncMethods retorna solo los métodos privados síncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_sync_methods = reflect.getPrivateSyncMethods()
        self.assertIn('__privateSyncMethod', private_sync_methods)
        self.assertNotIn('instanceAsyncMethod', private_sync_methods)
        self.assertNotIn('_protectedAsyncMethod', private_sync_methods)

    async def testGetPrivateAsyncMethods(self):
        """
        Verifica que getPrivateAsyncMethods retorna solo los métodos privados asíncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_async_methods = reflect.getPrivateAsyncMethods()
        self.assertIn('__privateAsyncMethod', private_async_methods)
        self.assertNotIn('instanceSyncMethod', private_async_methods)
        self.assertNotIn('_protectedAsyncMethod', private_async_methods)

    async def testGetPublicClassMethods(self):
        """
        Verifica que getPublicClassMethods retorna solo los métodos de clase públicos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_class_methods = reflect.getPublicClassMethods()
        self.assertIn('classSyncMethod', public_class_methods)
        self.assertNotIn('_protected_class_method', public_class_methods)
        self.assertNotIn('__private_class_method', public_class_methods)

    async def testGetPublicClassSyncMethods(self):
        """
        Verifica que getPublicClassSyncMethods retorna solo los métodos de clase públicos síncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_class_sync_methods = reflect.getPublicClassSyncMethods()
        self.assertIn('classSyncMethod', public_class_sync_methods)
        self.assertNotIn('_protected_class_method', public_class_sync_methods)
        self.assertNotIn('__private_class_method', public_class_sync_methods)

    async def testGetPublicClassAsyncMethods(self):
        """
        Verifica que getPublicClassAsyncMethods retorna solo los métodos de clase públicos asíncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_class_async_methods = reflect.getPublicClassAsyncMethods()
        self.assertIn('classAsyncMethod', public_class_async_methods)
        self.assertNotIn('_protected_class_async_method', public_class_async_methods)
        self.assertNotIn('__private_class_async_method', public_class_async_methods)

    async def testGetProtectedClassMethods(self):
        """
        Verifica que getProtectedClassMethods retorna solo los métodos de clase protegidos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_class_methods = reflect.getProtectedClassMethods()
        self.assertIn('_classMethodProtected', protected_class_methods)
        self.assertNotIn('classSyncMethod', protected_class_methods)
        self.assertNotIn('__classMethodPrivate', protected_class_methods)

    async def testGetProtectedClassSyncMethods(self):
        """
        Verifica que getProtectedClassSyncMethods retorna solo los métodos de clase protegidos síncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_class_sync_methods = reflect.getProtectedClassSyncMethods()
        self.assertIn('_classMethodProtected', protected_class_sync_methods)
        self.assertNotIn('classSyncMethod', protected_class_sync_methods)
        self.assertNotIn('__classSyncMethodPrivate', protected_class_sync_methods)

    async def testGetProtectedClassAsyncMethods(self):
        """
        Verifica que getProtectedClassAsyncMethods retorna solo los métodos de clase protegidos asíncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_class_async_methods = reflect.getProtectedClassAsyncMethods()
        self.assertIn('_classAsyncMethodProtected', protected_class_async_methods)
        self.assertNotIn('classAsyncMethod', protected_class_async_methods)
        self.assertNotIn('__classAsyncMethodPrivate', protected_class_async_methods)

    async def testGetPrivateClassMethods(self):
        """
        Verifica que getPrivateClassMethods retorna solo los métodos de clase privados.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_class_methods = reflect.getPrivateClassMethods()
        self.assertIn('__classMethodPrivate', private_class_methods)
        self.assertNotIn('classSyncMethod', private_class_methods)
        self.assertNotIn('_classMethodProtected', private_class_methods)

    async def testGetPrivateClassSyncMethods(self):
        """
        Verifica que getPrivateClassSyncMethods retorna solo los métodos de clase privados síncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_class_methods = reflect.getPrivateClassSyncMethods()
        self.assertIn('__classMethodPrivate', private_class_methods)
        self.assertNotIn('classSyncMethod', private_class_methods)
        self.assertNotIn('_classMethodProtected', private_class_methods)

    async def testGetPrivateClassAsyncMethods(self):
        """
        Verifica que getPrivateClassAsyncMethods retorna solo los métodos de clase privados asíncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_class_async_methods = reflect.getPrivateClassAsyncMethods()
        self.assertIn('__classAsyncMethodPrivate', private_class_async_methods)
        self.assertNotIn('classAsyncMethod', private_class_async_methods)
        self.assertNotIn('_classAsyncMethodProtected', private_class_async_methods)

    async def testGetPublicStaticMethods(self):
        """
        Verifica que getPublicStaticMethods retorna solo los métodos estáticos públicos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_static_methods = reflect.getPublicStaticMethods()
        self.assertIn('staticMethod', public_static_methods)
        self.assertIn('staticAsyncMethod', public_static_methods)
        self.assertNotIn('static_async_method', public_static_methods)

    async def testGetPublicStaticSyncMethods(self):
        """
        Verifica que getPublicStaticSyncMethods retorna solo los métodos estáticos públicos síncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_static_sync_methods = reflect.getPublicStaticSyncMethods()
        self.assertIn('staticMethod', public_static_sync_methods)
        self.assertNotIn('staticAsyncMethod', public_static_sync_methods)
        self.assertNotIn('static_async_method', public_static_sync_methods)

    async def testGetPublicStaticAsyncMethods(self):
        """
        Verifica que getPublicStaticAsyncMethods retorna solo los métodos estáticos públicos asíncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_static_async_methods = reflect.getPublicStaticAsyncMethods()
        self.assertIn('staticAsyncMethod', public_static_async_methods)
        self.assertNotIn('staticMethod', public_static_async_methods)
        self.assertNotIn('static_async_method', public_static_async_methods)

    async def testGetProtectedStaticMethods(self):
        """
        Verifica que getProtectedStaticMethods retorna solo los métodos estáticos protegidos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_static_methods = reflect.getProtectedStaticMethods()
        self.assertIn('_staticMethodProtected', protected_static_methods)
        self.assertNotIn('staticMethod', protected_static_methods)
        self.assertNotIn('__staticMethodPrivate', protected_static_methods)

    async def testGetProtectedStaticSyncMethods(self):
        """
        Verifica que getProtectedStaticSyncMethods retorna solo los métodos estáticos protegidos síncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_static_sync_methods = reflect.getProtectedStaticSyncMethods()
        self.assertIn('_staticMethodProtected', protected_static_sync_methods)
        self.assertNotIn('staticAsyncMethod', protected_static_sync_methods)
        self.assertNotIn('__staticMethodPrivate', protected_static_sync_methods)

    async def testGetProtectedStaticAsyncMethods(self):
        """
        Verifica que getProtectedStaticAsyncMethods retorna solo los métodos estáticos protegidos asíncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_static_async_methods = reflect.getProtectedStaticAsyncMethods()
        self.assertIn('_staticAsyncMethodProtected', protected_static_async_methods)
        self.assertNotIn('staticMethod', protected_static_async_methods)
        self.assertNotIn('__staticMethodPrivate', protected_static_async_methods)

    async def testGetPrivateStaticMethods(self):
        """
        Verifica que getPrivateStaticMethods retorna solo los métodos estáticos privados.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_static_methods = reflect.getPrivateStaticMethods()
        self.assertIn('__staticMethodPrivate', private_static_methods)
        self.assertNotIn('staticMethod', private_static_methods)
        self.assertNotIn('_staticMethodProtected', private_static_methods)

    async def testGetPrivateStaticSyncMethods(self):
        """
        Verifica que getPrivateStaticSyncMethods retorna solo los métodos estáticos privados síncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_static_sync_methods = reflect.getPrivateStaticSyncMethods()
        self.assertIn('__staticMethodPrivate', private_static_sync_methods)
        self.assertNotIn('staticMethod', private_static_sync_methods)
        self.assertNotIn('_staticMethodProtected', private_static_sync_methods)

    async def testGetPrivateStaticAsyncMethods(self):
        """
        Verifica que getPrivateStaticAsyncMethods retorna solo los métodos estáticos privados asíncronos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_static_async_methods = reflect.getPrivateStaticAsyncMethods()
        self.assertIn('__staticAsyncMethodPrivate', private_static_async_methods)
        self.assertNotIn('staticAsyncMethod', private_static_async_methods)
        self.assertNotIn('_staticAsyncMethodProtected', private_static_async_methods)

    async def testGetDunderMethods(self):
        """
        Verifica que getDunderMethods retorna los métodos dunder.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        dunder_methods = reflect.getDunderMethods()
        self.assertIn('__init__', dunder_methods)

    async def testGetMagicMethods(self):
        """
        Verifica que getMagicMethods retorna los métodos mágicos.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        magic_methods = reflect.getMagicMethods()
        self.assertIn('__init__', magic_methods)

    async def testGetProperties(self):
        """
        Verifica que getProperties retorna las propiedades de la clase.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        properties = reflect.getProperties()
        self.assertIn('computed_public_property', properties)
        self.assertIn('_computed_property_protected', properties)
        self.assertIn('__computed_property_private', properties)

    async def testGetPublicProperties(self):
        """
        Verifica que getPublicProperties retorna solo las propiedades públicas.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        public_properties = reflect.getPublicProperties()
        self.assertIn('computed_public_property', public_properties)
        self.assertNotIn('_computed_property_protected', public_properties)
        self.assertNotIn('__computed_property_private', public_properties)

    async def testGetProtectedProperties(self):
        """
        Verifica que getProtectedProperties retorna solo las propiedades protegidas.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        protected_properties = reflect.getProtectedProperties()
        self.assertIn('_computed_property_protected', protected_properties)
        self.assertNotIn('computed_public_property', protected_properties)
        self.assertNotIn('__computed_property_private', protected_properties)

    async def testGetPrivateProperties(self):
        """
        Verifica que getPrivateProperties retorna solo las propiedades privadas.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        private_properties = reflect.getPrivateProperties()
        self.assertIn('__computed_property_private', private_properties)
        self.assertNotIn('computed_public_property', private_properties)
        self.assertNotIn('_computed_property_protected', private_properties)

    async def testGetPropertySignature(self):
        """
        Verifica que getPropertySignature retorna la firma de la propiedad.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        signature = reflect.getPropertySignature('computed_public_property')
        self.assertEqual(str(signature), '(self) -> str')

    async def testGetPropertyDocstring(self):
        """
        Verifica que getPropertyDocstring retorna el docstring de la propiedad.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        docstring = reflect.getPropertyDocstring('computed_public_property')
        self.assertIn('Computes and returns the valu', docstring)

    async def testGetConstructorDependencies(self):
        """
        Verifica que getConstructorDependencies retorna las dependencias del constructor.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        dependencies = reflect.getConstructorDependencies()
        self.assertIsInstance(dependencies, ClassDependency)

    async def testGetMethodDependencies(self):
        """
        Verifica que getMethodDependencies retorna las dependencias del método.
        """
        reflect = ReflectionAbstract(AbstractFakeClass)
        method_deps = reflect.getMethodDependencies('instanceSyncMethod')
        self.assertIn('x', method_deps.resolved)
        self.assertIn('y', method_deps.resolved)
        self.assertEqual(method_deps.resolved['x'].class_name, 'int')
        self.assertEqual(method_deps.resolved['y'].class_name, 'int')
        self.assertEqual(method_deps.resolved['x'].module_name, 'builtins')
        self.assertEqual(method_deps.resolved['y'].module_name, 'builtins')
        self.assertEqual(method_deps.resolved['x'].type, int)
        self.assertEqual(method_deps.resolved['y'].type, int)
        self.assertEqual(method_deps.resolved['x'].full_class_path, 'builtins.int')
        self.assertEqual(method_deps.resolved['y'].full_class_path, 'builtins.int')
        self.assertEqual(method_deps.unresolved, [])
