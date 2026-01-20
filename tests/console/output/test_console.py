from orionis.console.contracts.console import IConsole
from orionis.console.output.console import Console
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.synchronous import SyncTestCase

class TestConsoleOutput(SyncTestCase):

    def testImplementation(self):
        """
        Checks that all methods declared in the `IConsole` interface are implemented
        by the `Console` concrete class.

        This method uses reflection to obtain the method names from both the interface
        and its concrete implementation. It then verifies that each method defined in the
        interface exists in the implementation.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
            AssertionError
                If any interface method is missing from the concrete class.
        """
        # Retrieve all method names from the interface using reflection
        rf_abstract = ReflectionAbstract(IConsole).getMethods()

        # Retrieve all method names from the concrete implementation using reflection
        rf_concrete = ReflectionConcrete(Console).getMethods()

        # Check that every interface method is implemented in the concrete class
        for method in rf_abstract:
            self.assertIn(method, rf_concrete)  # Assert method presence in implementation

    def testPropierties(self):
        """
        Checks that all properties declared in the `IConsole` interface are implemented
        by the `Console` concrete class.

        This method uses reflection to obtain the property names from both the interface
        and its concrete implementation. It then verifies that each property defined in the
        interface exists in the implementation.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
            AssertionError
                If any interface property is missing from the concrete class.
        """
        # Retrieve all property names from the interface using reflection
        rf_abstract = ReflectionAbstract(IConsole).getProperties()

        # Retrieve all property names from the concrete implementation using reflection
        rf_concrete = ReflectionConcrete(Console).getProperties()

        # Check that every interface property is implemented in the concrete class
        for prop in rf_abstract:
            self.assertIn(prop, rf_concrete)  # Assert property presence in implementation
