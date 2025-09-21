from orionis.console.base.scheduler import BaseScheduler
from orionis.console.contracts.base_scheduler import IBaseScheduler
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.asynchronous import AsyncTestCase

class TestConsoleBaseScheduler(AsyncTestCase):

    def testImplementation(self):
        """
        Tests that all methods defined in the `IBaseScheduler` interface are implemented
        by the `BaseScheduler` concrete class.

        This method uses reflection to retrieve the list of method names from both the
        interface and the concrete implementation, then verifies that each interface
        method exists in the concrete class.

        Returns
        -------
        None
            This method does not return a value. It raises an assertion error if any
            interface method is not implemented in the concrete class.
        """

        # Retrieve the list of method names from the interface
        rf_abstract = ReflectionAbstract(IBaseScheduler).getMethods()

        # Retrieve the list of method names from the concrete implementation
        rf_concrete = ReflectionConcrete(BaseScheduler).getMethods()

        # Ensure that every method in the interface is implemented in the concrete class
        for method in rf_abstract:

            # Assert that the method from the interface exists in the concrete class
            self.assertIn(method, rf_concrete)
