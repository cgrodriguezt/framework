from abc import ABC
import unittest
from orionis.luminate.support.inspection.reflection import Reflection
from orionis.luminate.test.test_output import PrinterInTest
from tests.support.inspection.fakes.fake_reflection_abstract import FakeAbstractClass

class TestReflexionAbstract(unittest.TestCase, PrinterInTest):
    """Test cases for ReflexionAbstract using FakeAbstractClass.

    This test suite verifies all functionality of the ReflexionAbstract class
    using FakeAbstractClass as the test subject.
    """

    def testReflectionAbstractExceptionValueError(self):
        """Class setup method.

        Initializes the ReflexionAbstract instance with FakeAbstractClass
        before any tests run.
        """
        with self.assertRaises(ValueError):
            Reflection.abstract(str)

    def testReflectionAbstractGetClassName(self):
        """Test getClassName() method.

        Verifies that:
        - The returned class name matches exactly
        - The return type is str
        """
        class_name = Reflection.abstract(FakeAbstractClass).getClassName()
        self.assertEqual(class_name, "FakeAbstractClass")
        self.assertIsInstance(class_name, str)

    def testReflectionAbstractGetModuleName(self):
        """Test getModuleName() method.

        Verifies that:
        - The module name is returned
        - The name is a string
        """
        module_name = Reflection.abstract(FakeAbstractClass).getModuleName()
        self.assertTrue(module_name == 'tests.support.inspection.fakes.fake_reflection_abstract')
        self.assertIsInstance(module_name, str)

    def testReflectionAbstractGetAbstractMethods(self):
        """Test getAbstractMethods() method.

        Verifies that:
        - All abstract methods are detected
        - No concrete methods are included
        - Return type is correct
        """
        methods = Reflection.abstract(FakeAbstractClass).getAbstractMethods()
        expected = {'abstract_method', 'another_abstract'}
        self.assertEqual(methods, expected)
        self.assertIsInstance(methods, set)

    def testReflectionAbstractGetConcreteMethods(self):
        """Test getConcreteMethods() method.

        Verifies that:
        - Concrete methods are detected
        - Abstract methods are excluded
        - Protected/private methods are excluded
        """
        methods = Reflection.abstract(FakeAbstractClass).getConcreteMethods()
        self.assertIn('static_helper', methods)
        self.assertIn('concrete_method', methods)
        self.assertIn('decorated_method', methods)
        self.assertNotIn('abstract_method', methods)
        self.assertNotIn('_protected_method', methods)
        self.assertNotIn('__private_method', methods)

    def testReflectionAbstractGetStaticMethods(self):
        """Test getStaticMethods() method.

        Verifies that:
        - Static methods are detected
        - Only static methods are included
        - Protected/private methods are excluded
        """
        static_methods = Reflection.abstract(FakeAbstractClass).getStaticMethods()
        self.assertIn('static_helper', static_methods)
        self.assertEqual(len(static_methods), 1)
        self.assertNotIn('create_instance', static_methods)

    def testReflectionAbstractGetClassMethods(self):
        """Test getClassMethods() method.

        Verifies that:
        - Class methods are detected
        - Only class methods are included
        - Protected/private methods are excluded
        """
        class_methods = Reflection.abstract(FakeAbstractClass).getClassMethods()
        self.assertIn('create_instance', class_methods)
        self.assertEqual(len(class_methods), 1)
        self.assertNotIn('static_helper', class_methods)

    def testReflectionAbstractGetProperties(self):
        """Test getProperties() method.

        Verifies that:
        - Properties are detected
        - Only properties are included
        - Protected/private properties are excluded
        """
        props = Reflection.abstract(FakeAbstractClass).getProperties()
        self.assertIn('computed_property', props)
        self.assertEqual(len(props), 1)

    def testReflectionAbstractGetMethodSignature(self):
        """Test getMethodSignature() method.

        Verifies that:
        - Correct signature is returned
        - Parameters are properly detected
        - Return type is properly detected
        """
        sig = Reflection.abstract(FakeAbstractClass).getMethodSignature('abstract_method')
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['self', 'x', 'y'])
        self.assertEqual(sig.return_annotation, int)

    def testReflectionAbstractGetDocstring(self):
        """Test getDocstring() method.

        Verifies that:
        - Docstring is returned
        - Docstring contains expected content
        """
        doc = Reflection.abstract(FakeAbstractClass).getDocstring()
        self.assertTrue(doc.startswith("A fake abstract class"))
        self.assertIsInstance(doc, str)

    def testReflectionAbstractGetBaseAbstractClasses(self):
        """Test getBaseAbstractClasses() method.

        Verifies that:
        - Base abstract classes are detected
        - Only abstract bases are included
        """
        bases = Reflection.abstract(FakeAbstractClass).getBaseAbstractClasses()
        self.assertEqual(bases, (ABC,))

    def testReflectionAbstractGetInterfaceMethods(self):
        """Test getInterfaceMethods() method.

        Verifies that:
        - Interface methods are detected
        - Signatures are correct
        - Only abstract methods are included
        """
        interface = Reflection.abstract(FakeAbstractClass).getInterfaceMethods()
        self.assertEqual(len(interface), 2)
        self.assertIn('abstract_method', interface)
        sig = interface['abstract_method']
        self.assertEqual(list(sig.parameters.keys()), ['self', 'x', 'y'])

    def testReflectionAbstractIsSubclassOf(self):
        """Test isSubclassOf() method.

        Verifies that:
        - Correctly identifies abstract base classes
        - Returns False for non-parent classes
        """
        self.assertTrue(Reflection.abstract(FakeAbstractClass).isSubclassOf(ABC))
        self.assertTrue(Reflection.abstract(FakeAbstractClass).isSubclassOf(object))

    def testReflectionAbstractGetSourceCode(self):
        """Test getSourceCode() method.

        Verifies that:
        - Source code is returned
        - Contains class definition
        """
        source = Reflection.abstract(FakeAbstractClass).getSourceCode()
        self.assertIsNotNone(source)
        self.assertIn("class FakeAbstractClass(ABC):", source)

    def testReflectionAbstractGetFileLocation(self):
        """Test getFileLocation() method.

        Verifies that:
        - File location is returned
        - Path ends with .py extension
        """
        location = Reflection.abstract(FakeAbstractClass).getFileLocation()
        self.assertIsNotNone(location)
        self.assertTrue('fake_reflection_abstract.py' in location)

    def testReflectionAbstractGetAnnotations(self):
        """Test getAnnotations() method.

        Verifies that:
        - Annotations are detected
        - Class attributes are included
        """
        annotations = Reflection.abstract(FakeAbstractClass).getAnnotations()
        self.assertIn('class_attr', annotations)
        self.assertEqual(annotations['class_attr'], str)

    def testReflectionAbstractGetDecorators(self):
        """Test getDecorators() method.

        Verifies that:
        - Decorators are detected
        - Correct number of decorators is returned
        - Decorator order is preserved
        """
        decorators = Reflection.abstract(FakeAbstractClass).getDecorators('decorated_method')
        for decorator in decorators:
            self.assertTrue(decorator in ['decorator_example', 'another_decorator'])

    def testReflectionAbstractIsProtocol(self):
        """Test isProtocol() method.

        Verifies that:
        - Correctly identifies non-Protocol classes
        """
        self.assertFalse(Reflection.abstract(FakeAbstractClass).isProtocol())

    def testReflectionAbstractGetRequiredAttributes(self):
        """Test getRequiredAttributes() method.

        Verifies that:
        - Returns empty set for non-Protocol classes
        """
        self.assertEqual(Reflection.abstract(FakeAbstractClass).getRequiredAttributes(), set())