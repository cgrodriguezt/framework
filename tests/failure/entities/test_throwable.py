from orionis.test.cases.synchronous import SyncTestCase
from orionis.failure.entities.throwable import Throwable
from dataclasses import FrozenInstanceError

class TestThrowable(SyncTestCase):

    def testInstantiationWithRequiredParameters(self):
        """
        Tests the instantiation of Throwable with only required parameters.

        This test verifies that a Throwable instance can be created with the minimum
        required parameters: classtype, message, and args. The traceback parameter
        should default to None.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """
        # Create a Throwable instance with required parameters
        throwable = Throwable(
            classtype=ValueError,
            message="Test error message",
            args=("arg1", "arg2")
        )

        # Assert the instance was created correctly
        self.assertIsInstance(throwable, Throwable)
        self.assertEqual(throwable.classtype, ValueError)
        self.assertEqual(throwable.message, "Test error message")
        self.assertEqual(throwable.args, ("arg1", "arg2"))
        self.assertIsNone(throwable.traceback)

    def testInstantiationWithAllParameters(self):
        """
        Tests the instantiation of Throwable with all parameters including traceback.

        This test verifies that a Throwable instance can be created with all parameters
        provided, including the optional traceback parameter.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """
        # Sample traceback string
        traceback_info = "Traceback (most recent call last):\n  File \"test.py\", line 1, in <module>"

        # Create a Throwable instance with all parameters
        throwable = Throwable(
            classtype=RuntimeError,
            message="Runtime error occurred",
            args=("error", 500),
            traceback=traceback_info
        )

        # Assert all parameters were set correctly
        self.assertEqual(throwable.classtype, RuntimeError)
        self.assertEqual(throwable.message, "Runtime error occurred")
        self.assertEqual(throwable.args, ("error", 500))
        self.assertEqual(throwable.traceback, traceback_info)

    def testInstantiationWithEmptyArgs(self):
        """
        Tests the instantiation of Throwable with empty args tuple.

        This test verifies that a Throwable instance can be created with an empty
        args tuple, which is a valid scenario for exceptions without arguments.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """
        # Create a Throwable instance with empty args
        throwable = Throwable(
            classtype=Exception,
            message="Simple exception",
            args=()
        )

        # Assert the instance was created correctly
        self.assertEqual(throwable.classtype, Exception)
        self.assertEqual(throwable.message, "Simple exception")
        self.assertEqual(throwable.args, ())
        self.assertIsNone(throwable.traceback)

    def testInstantiationWithEmptyMessage(self):
        """
        Tests the instantiation of Throwable with an empty message string.

        This test verifies that a Throwable instance can be created with an empty
        message string, which might occur in some edge cases.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """
        # Create a Throwable instance with empty message
        throwable = Throwable(
            classtype=Exception,
            message="",
            args=("some", "args")
        )

        # Assert the instance was created correctly
        self.assertEqual(throwable.classtype, Exception)
        self.assertEqual(throwable.message, "")
        self.assertEqual(throwable.args, ("some", "args"))

    def testInstantiationWithDifferentExceptionTypes(self):
        """
        Tests the instantiation of Throwable with various exception types.

        This test verifies that a Throwable instance can be created with different
        exception class types, ensuring the classtype field accepts various exception classes.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """
        # Test with different exception types
        exception_types = [
            (ValueError, "Value error"),
            (TypeError, "Type error"),
            (KeyError, "Key error"),
            (AttributeError, "Attribute error"),
            (IndexError, "Index error")
        ]

        for exc_type, message in exception_types:
            with self.subTest(exception_type=exc_type):
                throwable = Throwable(
                    classtype=exc_type,
                    message=message,
                    args=(message,)
                )

                self.assertEqual(throwable.classtype, exc_type)
                self.assertEqual(throwable.message, message)
                self.assertEqual(throwable.args, (message,))

    def testInstantiationWithCustomExceptionClass(self):
        """
        Tests the instantiation of Throwable with a custom exception class.

        This test verifies that a Throwable instance can be created with custom
        exception classes, not just built-in Python exceptions.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """
        # Define a custom exception class
        class CustomException(Exception):
            pass

        # Create a Throwable instance with custom exception
        throwable = Throwable(
            classtype=CustomException,
            message="Custom exception occurred",
            args=("custom", "error")
        )

        # Assert the instance was created correctly
        self.assertEqual(throwable.classtype, CustomException)
        self.assertEqual(throwable.message, "Custom exception occurred")
        self.assertEqual(throwable.args, ("custom", "error"))

    def testDataclassFrozenBehavior(self):
        """
        Tests that Throwable instances are immutable due to frozen=True.

        This test verifies that once a Throwable instance is created, its attributes
        cannot be modified, ensuring immutability as specified by the frozen=True parameter.

        Returns
        -------
        None
            This method does not return anything. It asserts that FrozenInstanceError is raised.
        """
        # Create a Throwable instance
        throwable = Throwable(
            classtype=ValueError,
            message="Test message",
            args=("test",)
        )

        # Attempt to modify attributes should raise FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            throwable.classtype = TypeError

        with self.assertRaises(FrozenInstanceError):
            throwable.message = "Modified message"

        with self.assertRaises(FrozenInstanceError):
            throwable.args = ("modified",)

        with self.assertRaises(FrozenInstanceError):
            throwable.traceback = "Modified traceback"

    def testDataclassKeywordOnlyParameters(self):
        """
        Tests that Throwable requires keyword-only parameters due to kw_only=True.

        This test verifies that all parameters must be passed as keyword arguments
        when creating a Throwable instance, as specified by the kw_only=True parameter.

        Returns
        -------
        None
            This method does not return anything. It asserts that TypeError is raised for positional args.
        """
        # Attempt to create Throwable with positional arguments should raise TypeError
        with self.assertRaises(TypeError):
            Throwable(ValueError, "Test message", ("test",))

        # Creating with keyword arguments should work
        throwable = Throwable(
            classtype=ValueError,
            message="Test message",
            args=("test",)
        )

        self.assertIsInstance(throwable, Throwable)

    def testEqualityComparison(self):
        """
        Tests the equality comparison between Throwable instances.

        This test verifies that two Throwable instances with the same attribute values
        are considered equal, and instances with different values are not equal.

        Returns
        -------
        None
            This method does not return anything. It asserts the equality behavior.
        """
        # Create two identical Throwable instances
        throwable1 = Throwable(
            classtype=ValueError,
            message="Test error",
            args=("arg1", "arg2"),
            traceback="Test traceback"
        )

        throwable2 = Throwable(
            classtype=ValueError,
            message="Test error",
            args=("arg1", "arg2"),
            traceback="Test traceback"
        )

        # Assert they are equal
        self.assertEqual(throwable1, throwable2)

        # Create a different Throwable instance
        throwable3 = Throwable(
            classtype=TypeError,
            message="Different error",
            args=("arg1", "arg2"),
            traceback="Test traceback"
        )

        # Assert they are not equal
        self.assertNotEqual(throwable1, throwable3)

    def testHashability(self):
        """
        Tests that Throwable instances are hashable and can be used in sets and as dict keys.

        This test verifies that Throwable instances can be hashed, which is enabled
        by the frozen=True parameter of the dataclass.

        Returns
        -------
        None
            This method does not return anything. It asserts the hashability behavior.
        """
        # Create Throwable instances
        throwable1 = Throwable(
            classtype=ValueError,
            message="Test error",
            args=("arg1",)
        )

        throwable2 = Throwable(
            classtype=TypeError,
            message="Another error",
            args=("arg2",)
        )

        # Test that instances can be hashed
        hash1 = hash(throwable1)
        hash2 = hash(throwable2)

        self.assertIsInstance(hash1, int)
        self.assertIsInstance(hash2, int)

        # Test that instances can be used in sets
        throwable_set = {throwable1, throwable2}
        self.assertEqual(len(throwable_set), 2)
        self.assertIn(throwable1, throwable_set)
        self.assertIn(throwable2, throwable_set)

        # Test that instances can be used as dictionary keys
        throwable_dict = {throwable1: "error1", throwable2: "error2"}
        self.assertEqual(throwable_dict[throwable1], "error1")
        self.assertEqual(throwable_dict[throwable2], "error2")

    def testStringRepresentation(self):
        """
        Tests the string representation of Throwable instances.

        This test verifies that Throwable instances have a meaningful string
        representation that includes all attribute values.

        Returns
        -------
        None
            This method does not return anything. It asserts the string representation.
        """
        # Create a Throwable instance
        throwable = Throwable(
            classtype=ValueError,
            message="Test error message",
            args=("arg1", "arg2"),
            traceback="Test traceback"
        )

        # Get string representation
        str_repr = str(throwable)

        # Assert that the string representation contains key information
        self.assertIn("Throwable", str_repr)
        self.assertIn("ValueError", str_repr)
        self.assertIn("Test error message", str_repr)
        self.assertIn("arg1", str_repr)
        self.assertIn("arg2", str_repr)
        self.assertIn("Test traceback", str_repr)

    def testRepr(self):
        """
        Tests the repr representation of Throwable instances.

        This test verifies that Throwable instances have a proper repr
        that can be used to recreate the instance.

        Returns
        -------
        None
            This method does not return anything. It asserts the repr behavior.
        """
        # Create a Throwable instance
        throwable = Throwable(
            classtype=ValueError,
            message="Test error",
            args=("test",),
            traceback=None
        )

        # Get repr representation
        repr_str = repr(throwable)

        # Assert that repr contains the class name and field information
        self.assertIn("Throwable", repr_str)
        self.assertIn("classtype", repr_str)
        self.assertIn("message", repr_str)
        self.assertIn("args", repr_str)
        self.assertIn("traceback", repr_str)

    def testTracebackOptionalBehavior(self):
        """
        Tests the optional behavior of the traceback parameter.

        This test verifies that the traceback parameter can be None, an empty string,
        or contain actual traceback information.

        Returns
        -------
        None
            This method does not return anything. It asserts the traceback handling.
        """
        # Test with None traceback (default)
        throwable_none = Throwable(
            classtype=Exception,
            message="Test",
            args=()
        )
        self.assertIsNone(throwable_none.traceback)

        # Test with empty string traceback
        throwable_empty = Throwable(
            classtype=Exception,
            message="Test",
            args=(),
            traceback=""
        )
        self.assertEqual(throwable_empty.traceback, "")

        # Test with actual traceback string
        traceback_str = "Traceback (most recent call last):\n  File \"<stdin>\", line 1, in <module>"
        throwable_with_tb = Throwable(
            classtype=Exception,
            message="Test",
            args=(),
            traceback=traceback_str
        )
        self.assertEqual(throwable_with_tb.traceback, traceback_str)

    def testArgumentsVariedTypes(self):
        """
        Tests that the args parameter can contain various types of data.

        This test verifies that the args tuple can contain different types of
        objects, similar to how exception arguments work in Python.

        Returns
        -------
        None
            This method does not return anything. It asserts the args flexibility.
        """
        # Test with mixed argument types
        mixed_args = ("string", 42, 3.14, True, None, ["list"], {"dict": "value"})

        throwable = Throwable(
            classtype=Exception,
            message="Mixed args test",
            args=mixed_args
        )

        # Assert all arguments are preserved correctly
        self.assertEqual(throwable.args, mixed_args)
        self.assertEqual(len(throwable.args), 7)
        self.assertEqual(throwable.args[0], "string")
        self.assertEqual(throwable.args[1], 42)
        self.assertEqual(throwable.args[2], 3.14)
        self.assertEqual(throwable.args[3], True) # NOSONAR
        self.assertIsNone(throwable.args[4])
        self.assertEqual(throwable.args[5], ["list"])
        self.assertEqual(throwable.args[6], {"dict": "value"})
