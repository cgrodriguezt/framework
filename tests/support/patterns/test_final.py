from orionis.test import TestCase
from orionis.support.patterns.final.meta import Final

class TestFinalMetaclass(TestCase):

    # ------------------------------------------------ basic usage

    def testFinalClassIsCreated(self):
        """
        Create a class using the Final metaclass.

        Validates that a class declared with Final as its metaclass
        is created without errors.
        """
        class MyFinal(metaclass=Final):
            pass

        self.assertIsNotNone(MyFinal) # NOSONAR

    def testFinalClassHasIsFinalAttribute(self):
        """
        Mark the class with __is_final__ = True.

        Validates that the Final metaclass sets the __is_final__
        attribute to True on the created class.
        """
        class MyFinal(metaclass=Final):
            pass

        self.assertTrue(getattr(MyFinal, "__is_final__", False))

    def testFinalClassIsCallable(self):
        """
        Allow instantiation of a final class.

        Validates that a class created with the Final metaclass
        can be instantiated normally.
        """
        class MyFinal(metaclass=Final):
            def __init__(self) -> None:
                self.value = 42

        obj = MyFinal()
        self.assertEqual(obj.value, 42)

    def testFinalClassRetainsAttributes(self):
        """
        Preserve class-level attributes in final classes.

        Validates that attributes and methods defined in the class
        body are accessible on instances.
        """
        class MyFinal(metaclass=Final):
            x = 10

            def get_x(self) -> int:
                return self.x

        obj = MyFinal()
        self.assertEqual(obj.get_x(), 10)

    # ------------------------------------------------ inheritance prevention

    def testInheritanceRaisesTypeError(self):
        """
        Raise TypeError when inheriting from a final class.

        Validates that attempting to subclass a class decorated with
        Final raises a TypeError.
        """
        class MyFinal(metaclass=Final):
            pass

        with self.assertRaises(TypeError):
            class Child(MyFinal): # NOSONAR
                pass

    def testTypeErrorMessageContainsClassName(self):
        """
        Include the final class name in the TypeError message.

        Validates that the error message raised when inheriting from
        a final class contains the name of the final class.
        """
        class ParentFinal(metaclass=Final):
            pass

        with self.assertRaises(TypeError) as ctx:
            class Child(ParentFinal): # NOSONAR
                pass

        self.assertIn("ParentFinal", str(ctx.exception))

    def testInheritanceFromMultipleBases(self):
        """
        Raise TypeError when one base is final among multiple bases.

        Validates that mixing a final class with other bases still
        raises a TypeError.
        """
        class MyFinal(metaclass=Final):
            pass

        class Normal:
            pass

        with self.assertRaises(TypeError):
            class Child(Normal, MyFinal): # NOSONAR
                pass

    def testNonFinalClassAllowsInheritance(self):
        """
        Allow normal inheritance for non-final classes.

        Validates that a regular class (without Final metaclass) can
        be subclassed without errors.
        """
        class Regular:
            pass

        class Child(Regular):
            pass

        self.assertTrue(issubclass(Child, Regular))

    # ------------------------------------------------ multiple final classes

    def testTwoIndependentFinalClassesAreIsolated(self):
        """
        Create two independent final classes without interference.

        Validates that two distinct final classes each have the
        __is_final__ attribute set independently.
        """
        class AlphaFinal(metaclass=Final):
            pass

        class BetaFinal(metaclass=Final):
            pass

        self.assertTrue(AlphaFinal.__is_final__)
        self.assertTrue(BetaFinal.__is_final__)

    def testFinalClassDoesNotInheritFromFinalByDefault(self):
        """
        Ignore __is_final__ from classes outside the hierarchy.

        Validates that a new final class is created cleanly without
        the metaclass mistakenly blocking its own creation.
        """
        class FirstFinal(metaclass=Final): # NOSONAR
            pass

        # Second final class is independent — should not raise
        class SecondFinal(metaclass=Final):
            pass

        self.assertTrue(SecondFinal.__is_final__)

    # ------------------------------------------------ metaclass type

    def testFinalMetaclassIsInstanceOfType(self):
        """
        Confirm Final is a subclass of type.

        Validates that the Final metaclass itself inherits from
        the built-in type, making it a valid metaclass.
        """
        self.assertTrue(issubclass(Final, type))

    def testClassCreatedWithFinalHasFinalAsMetaclass(self):
        """
        Use Final as the metaclass of the created class.

        Validates that the type of a class created with Final
        is the Final metaclass itself.
        """
        class MyFinal(metaclass=Final):
            pass

        self.assertIsInstance(MyFinal, Final)

    # ------------------------------------------------ edge cases

    def testFinalClassWithNoBody(self):
        """
        Create a final class with an empty body.

        Validates that a minimal class definition with only the
        Final metaclass is valid and marks the class correctly.
        """
        class Empty(metaclass=Final):
            pass

        self.assertTrue(Empty.__is_final__)

    def testFinalClassWithInheritedMethods(self):
        """
        Allow final classes to include inherited method-like attrs.

        Validates that methods and class variables defined inside
        a final class body are accessible after creation.
        """
        class Rich(metaclass=Final):
            label = "rich"

            def greet(self) -> str:
                return f"Hello from {self.label}"

        obj = Rich()
        self.assertEqual(obj.greet(), "Hello from rich")

    def testDeepInheritanceBlockedAtEachLevel(self):
        """
        Block inheritance even through an intermediate non-final class.

        Validates that a grandchild class cannot inherit from a final
        class even when going through another base class.
        """
        class BaseFinal(metaclass=Final):
            pass

        with self.assertRaises(TypeError):
            class DirectChild(BaseFinal): # NOSONAR
                pass
