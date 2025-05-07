from orionis.luminate.support.introspection.dependencies import ReflectDependencies
from orionis.luminate.support.introspection.dependencies.entities.class_dependencies import ClassDependency
from orionis.luminate.support.introspection.dependencies.entities.method_dependencies import MethodDependency
from orionis.luminate.support.introspection.dependencies.entities.resolved_dependencies import ResolvedDependency
from orionis.luminate.test import TestCase
from tests.support.inspection.fakes.fake_reflect_dependencies import FakeUser, FakeUserWithPermissions, UserController

class TestReflectDependencies(TestCase):
    """
    Unit tests for the Reflection class.
    """

    async def testReflectionDependenciesGetConstructorDependencies(self):
        """
        Test the reflection of dependencies in a class.
        """
        depend = ReflectDependencies(UserController)
        constructor_dependencies = depend.getConstructorDependencies()

        # Check Instance of ClassDependency
        self.assertIsInstance(constructor_dependencies, ClassDependency)

        # Check unresolved dependencies
        self.assertEqual(constructor_dependencies.unresolved, [])

        # Check Instance of ResolvedDependency
        dep_user_repository:ResolvedDependency = constructor_dependencies.resolved.get('user_repository')
        self.assertIsInstance(dep_user_repository, ResolvedDependency)

        # Check resolved dependencies
        self.assertEqual(dep_user_repository.module_name, 'tests.support.inspection.fakes.fake_reflect_dependencies')
        self.assertEqual(dep_user_repository.class_name, 'FakeUser')
        self.assertEqual(dep_user_repository.full_class_path, 'tests.support.inspection.fakes.fake_reflect_dependencies.FakeUser')
        self.assertEqual(dep_user_repository.type, FakeUser)

    async def testReflectionDependenciesGetMethodDependencies(self):
        """
        Test the reflection of dependencies in a class method.
        """
        depend = ReflectDependencies(UserController)
        method_dependencies = depend.getMethodDependencies('create_user_with_permissions')

        # Check Instance of MethodDependency
        self.assertIsInstance(method_dependencies, MethodDependency)

        # Check unresolved dependencies
        self.assertEqual(method_dependencies.unresolved, [])

        # Check Instance of ResolvedDependency for 'user_permissions'
        dep_user_permissions:ResolvedDependency = method_dependencies.resolved.get('user_permissions')
        self.assertIsInstance(dep_user_permissions, ResolvedDependency)

        # Check resolved dependencies for 'user_permissions'
        self.assertEqual(dep_user_permissions.module_name, 'tests.support.inspection.fakes.fake_reflect_dependencies')
        self.assertEqual(dep_user_permissions.class_name, 'FakeUserWithPermissions')
        self.assertEqual(dep_user_permissions.full_class_path, 'tests.support.inspection.fakes.fake_reflect_dependencies.FakeUserWithPermissions')
        self.assertEqual(dep_user_permissions.type, FakeUserWithPermissions)

        # Check Instance of ResolvedDependency for 'permissions'
        dep_permissions:ResolvedDependency = method_dependencies.resolved.get('permissions')
        self.assertIsInstance(dep_permissions, ResolvedDependency)

        # Check resolved dependencies for 'permissions'
        self.assertEqual(dep_permissions.module_name, 'builtins')
        self.assertEqual(dep_permissions.class_name, 'list')
        self.assertEqual(dep_permissions.full_class_path, 'builtins.list')
        self.assertEqual(dep_permissions.type, list[str])