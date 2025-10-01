from orionis.console.base.scheduler_event_listener import BaseScheduleEventListener
from orionis.console.contracts.schedule_event_listener import IScheduleEventListener
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.synchronous import SyncTestCase

class TestConsoleBaseBaseScheduleEventListener(SyncTestCase):

    def testImplementation(self):
        """
        Test that all methods defined in the IScheduleEventListener interface
        are implemented by the BaseScheduleEventListener class.

        This method uses reflection to retrieve the list of method names from
        both the interface and the concrete implementation, and asserts that
        each interface method is present in the implementation.

        Returns
        -------
        None
            This method does not return a value. It raises an assertion error
            if any interface method is not implemented in the concrete class.
        """

        # Retrieve the list of method names from the interface
        rf_abstract = ReflectionAbstract(IScheduleEventListener).getMethods()

        # Retrieve the list of method names from the concrete implementation
        rf_concrete = ReflectionConcrete(BaseScheduleEventListener).getMethods()

        # Ensure that every method in the interface is implemented in the concrete class
        for method in rf_abstract:

            # Assert that the method from the interface exists in the implementation
            self.assertIn(method, rf_concrete)
