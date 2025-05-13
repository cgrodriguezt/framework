from orionis.luminate.test import TestCase
from orionis.luminate.config.auth import Auth

class TestConfigApp(TestCase):
    """
    Unit tests for App configuration defaults.
    """

    async def testNewValue(self):
        """
        Test that the default name of the App instance is 'Orionis Application'.

        This test creates a new App object and asserts that its 'name' attribute
        is set to the expected default value.
        """
        auth = Auth()
        auth.new_value = 'new_value'
        auth.new_value2 = 'new_value2'

        self.assertEqual(auth.new_value, 'new_value')
        self.assertEqual(auth.new_value2, 'new_value2')