import unittest
from orionis.luminate.support.inspection.reflection import Reflection
from orionis.luminate.support.inspection.reflexion_instance import ReflexionInstance
from orionis.luminate.test.test_output import PrinterInTest
from tests.support.inspection.fakes.fake_reflection import BaseFakeClass, FakeClass

class TestReflection(unittest.TestCase, PrinterInTest):
    """
    Unit tests for the Reflection class.
    This class tests the functionality of the Reflection class, ensuring that it correctly handles
    """

    def testReflectionInstanceExceptionValueError(self):
        """Test that Reflection.instance raises ValueError for invalid types."""
        with self.assertRaises(ValueError):
            Reflection.instance(str)

    def testReflectionInstance(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        self.assertIsInstance(Reflection.instance(FakeClass()), ReflexionInstance)

    def testReflectionInstanceGetClassName(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        self.assertEqual(reflex.getClassName(), "FakeClass")

    def testReflectionInstanceGetClass(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        self.assertEqual(reflex.getClass(), FakeClass)

    def testReflectionInstanceGetModuleName(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        self.assertEqual(reflex.getModuleName(), "tests.support.inspection.fakes.fake_reflection")

    def testReflectionInstanceGetAttributes(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        attributes = reflex.getAttributes()
        self.assertTrue("public_attr" in attributes)
        self.assertTrue("_private_attr" in attributes)
        self.assertTrue("dynamic_attr" in attributes)

    def testReflectionInstanceGetMethods(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        methods = reflex.getMethods()
        self.assertTrue("instance_method" in methods)
        self.assertTrue("class_method" in methods)

    def testReflectionInstanceGetStaticMethods(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        methods = reflex.getStaticMethods()
        self.assertTrue("static_method" in methods)

    def testReflectionInstanceGetPropertyNames(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        properties = reflex.getPropertyNames()
        self.assertTrue("computed_property" in properties)

    def testReflectionInstanceCallMethod(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        result = reflex.callMethod("instance_method", 1, 2)
        self.assertEqual(result, 3)

    def testReflectionInstanceGetMethodSignature(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        signature = reflex.getMethodSignature("instance_method")
        self.assertEqual(str(signature), "(x: int, y: int) -> int")

    def testReflectionInstanceGetDocstring(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        docstring = reflex.getDocstring()
        self.assertIn("This is a test class for ReflexionInstance", docstring)

    def testReflectionInstanceGetBaseClasses(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        base_classes = reflex.getBaseClasses()
        self.assertIn(BaseFakeClass, base_classes)

    def testReflectionInstanceIsInstanceOf(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        self.assertTrue(reflex.isInstanceOf(BaseFakeClass))

    def testReflectionInstanceGetSourceCode(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        source_code = reflex.getSourceCode()
        self.assertIn("class FakeClass(BaseFakeClass):", source_code)

    def testReflectionInstanceGetFileLocation(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        file_location = reflex.getFileLocation()
        self.assertIn("fake_reflection.py", file_location)

    def testReflectionInstanceGetAnnotations(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        annotations = reflex.getAnnotations()
        self.assertEqual("{'class_attr': <class 'str'>}", str(annotations))

    def testReflectionInstanceHasAttribute(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        self.assertTrue(reflex.hasAttribute("public_attr"))
        self.assertFalse(reflex.hasAttribute("non_existent_attr"))

    def testReflectionInstanceGetAttribute(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        attr_value = reflex.getAttribute("public_attr")
        self.assertEqual(attr_value, 42)

    def testReflectionInstanceGetCallableMembers(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""
        reflex = Reflection.instance(FakeClass())
        callable_members = reflex.getCallableMembers()
        self.assertIn("instance_method", callable_members)
        self.assertIn("class_method", callable_members)
        self.assertIn("static_method", callable_members)

    def testReflectionInstanceSetAttribute(self):
        """Test that Reflection.instance returns an instance of ReflexionInstance."""

        # Create a new macro function
        def myMacro(cls:FakeClass, num):
            return cls.instance_method(10, 12) + num

        # Create an instance of FakeClass and set the macro as an attribute
        reflex = Reflection.instance(FakeClass())
        reflex.setAttribute("myMacro", myMacro)

        # Check if the macro was set correctly
        self.assertTrue(reflex.hasAttribute("myMacro"))

        # Call the macro method and check the result
        result = reflex.callMethod("myMacro", reflex._instance, 3)
        self.assertEqual(result, 25)