from orionis.console.contracts.schedule import ISchedule
from orionis.console.tasks.schedule import Schedule
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.asynchronous import AsyncTestCase

class TestConsoleTasks(AsyncTestCase):

    def testImplementation(self):
        """
        Verifies that all methods declared in the `ISchedule` interface are implemented
        by the `Schedule` concrete class.

        This method uses reflection to retrieve the method names from both the interface
        and its concrete implementation, then checks that each interface method exists
        in the implementation.

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
        # Retrieve all method names from the interface
        rf_abstract = ReflectionAbstract(ISchedule).getMethods()

        # Retrieve all method names from the concrete implementation
        rf_concrete = ReflectionConcrete(Schedule).getMethods()

        # Check that every interface method is implemented in the concrete class
        for method in rf_abstract:
            self.assertIn(method, rf_concrete)  # Assert method presence

    def testPropierties(self):
        """
        Verifies that all properties declared in the `ISchedule` interface are present
        in the `Schedule` concrete class.

        This method uses reflection to retrieve the property names from both the interface
        and its concrete implementation, then checks that each interface property exists
        in the implementation.

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
        # Retrieve all property names from the interface
        rf_abstract = ReflectionAbstract(ISchedule).getProperties()

        # Retrieve all property names from the concrete implementation
        rf_concrete = ReflectionConcrete(Schedule).getProperties()

        # Check that every interface property is present in the concrete class
        for prop in rf_abstract:
            self.assertIn(prop, rf_concrete)  # Assert property presence