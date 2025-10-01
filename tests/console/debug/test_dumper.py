from orionis.console.contracts.dumper import IDumper
from orionis.console.debug.dumper import Dumper
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.synchronous import SyncTestCase

class TestConsoleDumper(SyncTestCase):

    def testImplementation(self):
        """
        Checks that all methods declared in the `IDumper` interface are implemented
        by the `Dumper` concrete class.

        This method uses reflection to obtain the method names from both the interface
        and its concrete implementation, then verifies that each interface method is
        present in the implementation.

        Parameters
        ----------
        None

        Returns
        -------
        None
            Raises an AssertionError if any interface method is missing from the concrete class.
        """

        # Get all method names from the interface
        rf_abstract = ReflectionAbstract(IDumper).getMethods()

        # Get all method names from the concrete implementation
        rf_concrete = ReflectionConcrete(Dumper).getMethods()

        # Assert that every interface method is implemented in the concrete class
        for method in rf_abstract:
            self.assertIn(method, rf_concrete)  # Check method presence

    def testPropierties(self):
        """
        Checks that all properties declared in the `IDumper` interface are present
        in the `Dumper` concrete class.

        This method uses reflection to obtain the property names from both the interface
        and its concrete implementation, then verifies that each interface property is
        present in the implementation.

        Parameters
        ----------
        None

        Returns
        -------
        None
            Raises an AssertionError if any interface property is missing from the concrete class.
        """

        # Get all property names from the interface
        rf_abstract = ReflectionAbstract(IDumper).getProperties()

        # Get all property names from the concrete implementation
        rf_concrete = ReflectionConcrete(Dumper).getProperties()

        # Assert that every interface property is present in the concrete class
        for prop in rf_abstract:
            self.assertIn(prop, rf_concrete)  # Check property presence