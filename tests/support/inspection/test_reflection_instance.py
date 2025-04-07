from orionis.luminate.support.inspection.reflection import Reflection
from orionis.luminate.support.inspection.reflexion_instance import ReflexionInstance
from orionis.luminate.test.test_case import TestCase
from tests.support.inspection.fakes.fake_reflection_instance import BaseFakeClass, FakeClass

class TestReflection(TestCase):
    """
    Unit tests for the Reflection class.
    """

    def testReflectionInstanceExceptionValueError(self):
        """Ensure Reflection.instance raises ValueError for invalid types."""
        with self.assertRaises(ValueError):
            Reflection.instance(str)

    def testReflectionInstance(self):
        """Verify Reflection.instance returns an instance of ReflexionInstance."""
        self.assertIsInstance(Reflection.instance(FakeClass()), ReflexionInstance)

    def testReflectionInstanceGetClassName(self):
        """Check that getClassName returns the correct class name."""
        reflex = Reflection.instance(FakeClass())
        self.assertEqual(reflex.getClassName(), "FakeClass")

    def testReflectionInstanceGetClass(self):
        """Ensure getClass returns the correct class."""
        reflex = Reflection.instance(FakeClass())
        self.assertEqual(reflex.getClass(), FakeClass)

    def testReflectionInstanceGetModuleName(self):
        """Verify getModuleName returns the correct module name."""
        reflex = Reflection.instance(FakeClass())
        self.assertEqual(reflex.getModuleName(), "tests.support.inspection.fakes.fake_reflection_instance")

    def testReflectionInstanceGetAttributes(self):
        """Check that getAttributes returns all attributes of the class."""
        reflex = Reflection.instance(FakeClass())
        attributes = reflex.getAttributes()
        self.assertTrue("public_attr" in attributes)
        self.assertTrue("_private_attr" in attributes)
        self.assertTrue("dynamic_attr" in attributes)

    def testReflectionInstanceGetMethods(self):
        """Ensure getMethods returns all methods of the class."""
        reflex = Reflection.instance(FakeClass())
        methods = reflex.getMethods()
        self.assertTrue("instance_method" in methods)
        self.assertTrue("class_method" in methods)

    def testReflectionInstanceGetStaticMethods(self):
        """Verify getStaticMethods returns all static methods of the class."""
        reflex = Reflection.instance(FakeClass())
        methods = reflex.getStaticMethods()
        self.assertTrue("static_method" in methods)

    def testReflectionInstanceGetPropertyNames(self):
        """Check that getPropertyNames returns all property names."""
        reflex = Reflection.instance(FakeClass())
        properties = reflex.getPropertyNames()
        self.assertTrue("computed_property" in properties)

    def testReflectionInstanceCallMethod(self):
        """Ensure callMethod correctly invokes a method with arguments."""
        reflex = Reflection.instance(FakeClass())
        result = reflex.callMethod("instance_method", 1, 2)
        self.assertEqual(result, 3)

    def testReflectionInstanceGetMethodSignature(self):
        """Verify getMethodSignature returns the correct method signature."""
        reflex = Reflection.instance(FakeClass())
        signature = reflex.getMethodSignature("instance_method")
        self.assertEqual(str(signature), "(x: int, y: int) -> int")

    def testReflectionInstanceGetDocstring(self):
        """Check that getDocstring returns the correct class docstring."""
        reflex = Reflection.instance(FakeClass())
        docstring = reflex.getDocstring()
        self.assertIn("This is a test class for ReflexionInstance", docstring)

    def testReflectionInstanceGetBaseClasses(self):
        """Ensure getBaseClasses returns the correct base classes."""
        reflex = Reflection.instance(FakeClass())
        base_classes = reflex.getBaseClasses()
        self.assertIn(BaseFakeClass, base_classes)

    def testReflectionInstanceIsInstanceOf(self):
        """Verify isInstanceOf checks inheritance correctly."""
        reflex = Reflection.instance(FakeClass())
        self.assertTrue(reflex.isInstanceOf(BaseFakeClass))

    def testReflectionInstanceGetSourceCode(self):
        """Check that getSourceCode returns the class source code."""
        reflex = Reflection.instance(FakeClass())
        source_code = reflex.getSourceCode()
        self.assertIn("class FakeClass(BaseFakeClass):", source_code)

    def testReflectionInstanceGetFileLocation(self):
        """Ensure getFileLocation returns the correct file path."""
        reflex = Reflection.instance(FakeClass())
        file_location = reflex.getFileLocation()
        self.assertIn("fake_reflection_instance.py", file_location)

    def testReflectionInstanceGetAnnotations(self):
        """Verify getAnnotations returns the correct class annotations."""
        reflex = Reflection.instance(FakeClass())
        annotations = reflex.getAnnotations()
        self.assertEqual("{'class_attr': <class 'str'>}", str(annotations))

    def testReflectionInstanceHasAttribute(self):
        """Check that hasAttribute correctly identifies attributes."""
        reflex = Reflection.instance(FakeClass())
        self.assertTrue(reflex.hasAttribute("public_attr"))
        self.assertFalse(reflex.hasAttribute("non_existent_attr"))

    def testReflectionInstanceGetAttribute(self):
        """Ensure getAttribute retrieves the correct attribute value."""
        reflex = Reflection.instance(FakeClass())
        attr_value = reflex.getAttribute("public_attr")
        self.assertEqual(attr_value, 42)

    def testReflectionInstanceGetCallableMembers(self):
        """Verify getCallableMembers returns all callable members."""
        reflex = Reflection.instance(FakeClass())
        callable_members = reflex.getCallableMembers()
        self.assertIn("instance_method", callable_members)
        self.assertIn("class_method", callable_members)
        self.assertIn("static_method", callable_members)

    def testReflectionInstanceSetAttribute(self):
        """Check that setAttribute correctly sets a new attribute."""
        def myMacro(cls: FakeClass, num):
            return cls.instance_method(10, 12) + num

        reflex = Reflection.instance(FakeClass())
        reflex.setAttribute("myMacro", myMacro)

        self.assertTrue(reflex.hasAttribute("myMacro"))

        result = reflex.callMethod("myMacro", reflex._instance, 3)
        self.assertEqual(result, 25)

    def testReflectionInstanceGetPropertySignature(self):
        """Ensure getPropertySignature returns the correct property signature."""
        signature = Reflection.instance(FakeClass()).getPropertySignature('computed_property')
        self.assertEqual(str(signature), '(self) -> str')