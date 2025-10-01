from orionis.console.contracts.executor import IExecutor
from orionis.console.output.executor import Executor
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.synchronous import SyncTestCase

class TestConsoleExecutor(SyncTestCase):

    def testImplementation(self):
        """
        Verifies that all methods declared in the `IExecutor` interface are implemented
        by the `Executor` concrete class.

        This method uses reflection to obtain the method names from both the interface
        and its concrete implementation. It then checks that each method defined in the
        interface exists in the implementation.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The method does not return any value. It raises an AssertionError if any
            interface method is missing from the concrete class.

        Raises
        ------
        AssertionError
            If any method declared in the interface is not implemented in the concrete class.
        """
        # Retrieve all method names from the interface using reflection
        rf_abstract = ReflectionAbstract(IExecutor).getMethods()

        # Retrieve all method names from the concrete implementation using reflection
        rf_concrete = ReflectionConcrete(Executor).getMethods()

        # Assert that every interface method is present in the concrete class
        for method in rf_abstract:
            self.assertIn(method, rf_concrete)  # Check method presence

    def testPropierties(self):
        """
        Verifies that all properties declared in the `IExecutor` interface are implemented
        by the `Executor` concrete class.

        This method uses reflection to obtain the property names from both the interface
        and its concrete implementation. It then checks that each property defined in the
        interface exists in the implementation.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The method does not return any value. It raises an AssertionError if any
            interface property is missing from the concrete class.

        Raises
        ------
        AssertionError
            If any property declared in the interface is not implemented in the concrete class.
        """
        # Retrieve all property names from the interface using reflection
        rf_abstract = ReflectionAbstract(IExecutor).getProperties()

        # Retrieve all property names from the concrete implementation using reflection
        rf_concrete = ReflectionConcrete(Executor).getProperties()

        # Assert that every interface property is present in the concrete class
        for prop in rf_abstract:
            self.assertIn(prop, rf_concrete)  # Check property presence
