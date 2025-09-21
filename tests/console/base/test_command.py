from orionis.console.base.command import BaseCommand
from orionis.console.contracts.base_command import IBaseCommand
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.asynchronous import AsyncTestCase

class TestConsoleBaseCommand(AsyncTestCase):

    def testImplementation(self):
        """
        Tests that all methods defined in the `IBaseCommand` interface are implemented
        by the `BaseCommand` concrete class.

        This method uses reflection to retrieve the list of method names from both
        the interface and its concrete implementation, then asserts that each method
        in the interface exists in the implementation.

        Returns
        -------
        None
            This method does not return a value. It raises an assertion error if any
            interface method is not implemented in the concrete class.
        """
        # Retrieve the list of method names from the interface
        rf_abstract = ReflectionAbstract(IBaseCommand).getMethods()

        # Retrieve the list of method names from the concrete implementation
        rf_concrete = ReflectionConcrete(BaseCommand).getMethods()

        # Ensure that every method in the interface is implemented in the concrete class
        for method in rf_abstract:
            self.assertIn(method, rf_concrete)  # Assert method presence

    def testPropierties(self):
        """
        Tests that all properties defined in the `IBaseCommand` interface are present
        in the `BaseCommand` concrete class.

        This method uses reflection to retrieve the list of property names from both
        the interface and its concrete implementation, then asserts that each property
        in the interface exists in the implementation.

        Returns
        -------
        None
            This method does not return a value. It raises an assertion error if any
            interface property is not present in the concrete class.
        """
        # Retrieve the list of property names from the interface
        rf_abstract = ReflectionAbstract(IBaseCommand).getProperties()

        # Retrieve the list of property names from the concrete implementation
        rf_concrete = ReflectionConcrete(BaseCommand).getProperties()

        # Ensure that every property in the interface is present in the concrete class
        for prop in rf_abstract:
            self.assertIn(prop, rf_concrete)  # Assert property presence