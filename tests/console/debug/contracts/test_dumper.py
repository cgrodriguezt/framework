from __future__ import annotations
import inspect
from orionis.console.debug.contracts.dumper import IDumper
from orionis.test import TestCase

class TestIDumper(TestCase):

    def testIsAbstractClass(self) -> None:
        """
        Verify that IDumper is an abstract class.

        Ensures that the interface defines abstract methods and cannot be
        used directly without a concrete implementation.
        """
        self.assertTrue(inspect.isabstract(IDumper))

    def testCannotBeInstantiatedDirectly(self) -> None:
        """
        Ensure IDumper cannot be instantiated directly.

        Attempts to create an instance of the abstract class and expects a
        TypeError because abstract methods have not been implemented.
        """
        with self.assertRaises(TypeError):
            IDumper()

    def testHasRequiredAbstractMethods(self) -> None:
        """
        Verify that IDumper declares the expected abstract methods.

        Checks that exactly the methods dd and dump are abstract,
        matching the contract required by all concrete implementations.
        """
        abstract_methods = IDumper.__abstractmethods__
        self.assertEqual(abstract_methods, {"dd", "dump"})

    def testDdMethodSignature(self) -> None:
        """
        Verify the parameter list of the abstract dd method.

        Ensures dd accepts *args plus the eight keyword-only configuration
        parameters defined in the interface docstring.
        """
        sig = inspect.signature(IDumper.dd)
        params = sig.parameters
        for name in (
            "show_types",
            "show_index",
            "expand_all",
            "max_depth",
            "module_path",
            "line_number",
            "redirect_output",
            "insert_line",
        ):
            self.assertIn(name, params)

    def testDumpMethodSignature(self) -> None:
        """
        Verify the parameter list of the abstract dump method.

        Ensures dump accepts *args plus the same eight keyword-only
        configuration parameters as dd.
        """
        sig = inspect.signature(IDumper.dump)
        params = sig.parameters
        for name in (
            "show_types",
            "show_index",
            "expand_all",
            "max_depth",
            "module_path",
            "line_number",
            "redirect_output",
            "insert_line",
        ):
            self.assertIn(name, params)

    def testDdAndDumpDefaultValues(self) -> None:
        """
        Verify that dd and dump declare consistent default parameter values.

        Ensures all keyword parameters share the same defaults across both
        methods, keeping the interface contract coherent.
        """
        defaults = {
            "show_types": False,
            "show_index": False,
            "expand_all": True,
            "max_depth": None,
            "module_path": None,
            "line_number": None,
            "redirect_output": False,
            "insert_line": False,
        }
        for method_name in ("dd", "dump"):
            sig = inspect.signature(getattr(IDumper, method_name))
            for param_name, expected in defaults.items():
                actual = sig.parameters[param_name].default
                self.assertEqual(
                    actual,
                    expected,
                    msg=f"{method_name}.{param_name}: expected {expected!r}, got {actual!r}",
                )

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Verify that a subclass implementing only one method cannot be instantiated.

        Ensures that any concrete class must implement all abstract methods
        before it can be instantiated.
        """
        class PartialDumper(IDumper):
            @staticmethod
            def dd(*args, **kwargs):
                pass

        with self.assertRaises(TypeError):
            PartialDumper()

    def testFullConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Verify that a fully implemented subclass can be instantiated.

        Ensures that providing implementations for both dd and dump is
        sufficient to create a valid concrete instance.
        """
        class ConcreteDumper(IDumper):
            @staticmethod
            def dd(*args, **kwargs):
                pass

            @staticmethod
            def dump(*args, **kwargs):
                pass

        instance = ConcreteDumper()
        self.assertIsInstance(instance, IDumper)

    def testBothMethodsAreNotCoroutines(self) -> None:
        """
        Verify that dd and dump are defined as synchronous methods.

        Ensures neither method is declared as a coroutine function,
        since variable dumping is an inherently synchronous operation.
        """
        self.assertFalse(inspect.iscoroutinefunction(IDumper.dd))
        self.assertFalse(inspect.iscoroutinefunction(IDumper.dump))
