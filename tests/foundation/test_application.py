from orionis.foundation.application import Application
from orionis.foundation.contracts.application import IApplication
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationApplication(AsyncTestCase):

    def testImplementation(self):
        """
        Verifies that the `Application` class provides concrete implementations for all methods defined in the `IApplication` interface.

        This test uses reflection to obtain the list of method names from both the interface (`IApplication`) and the concrete class (`Application`).
        It asserts that every method defined in the interface is present in the concrete implementation, ensuring that the contract specified by the interface is fully honored.

        Returns
        -------
        None
            This method does not return a value. It raises an assertion error if any interface method is not implemented by the concrete class.
        """

        # Retrieve the list of method names from the interface
        rf_abstract = ReflectionAbstract(IApplication).getMethods()

        # Retrieve the list of method names from the concrete implementation
        rf_concrete = ReflectionConcrete(Application).getMethods()

        # Ensure that every method in the interface is implemented in the concrete class
        for method in rf_abstract:
            self.assertIn(method, rf_concrete)