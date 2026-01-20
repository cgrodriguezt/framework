from orionis.foundation.config.auth.entities.auth import Auth
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigAuth(SyncTestCase):

    def testNewValue(self):
        """
        Tests the assignment and retrieval of dynamically added attributes in the Auth object.

        This method creates an instance of the Auth class and assigns values to new attributes
        that do not exist by default. It then verifies that these attributes are correctly set
        and retrievable, ensuring that the Auth object supports dynamic attribute assignment.

        Parameters
        ----------
        self : TestFoundationConfigAuth
            The test case instance.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Create a new Auth object
        auth = Auth()

        # Dynamically assign new attributes to the Auth object
        auth.new_value = "new_value"
        auth.new_value2 = "new_value2"

        # Assert that the new attributes hold the expected values
        self.assertEqual(auth.new_value, "new_value")
        self.assertEqual(auth.new_value2, "new_value2")
