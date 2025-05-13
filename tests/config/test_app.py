from orionis.luminate.config.exceptions.integrity_exception import OrionisIntegrityException
from orionis.luminate.test import TestCase
from orionis.luminate.config.app import App
from orionis.luminate.config.app.enums.environments import Environments
from orionis.luminate.services.workers.maximum_workers import MaximumWorkers
from orionis.luminate.config.app.enums.ciphers import Cipher

class TestConfigApp(TestCase):
    """
    Unit tests for App configuration defaults.
    """

    async def testDefaultName(self):
        """
        Test that the default name of the App instance is 'Orionis Application'.

        This test creates a new App object and asserts that its 'name' attribute
        is set to the expected default value.
        """
        app = App()
        self.assertEqual(app.name, 'Orionis Application')

    async def testDefaultEnv(self):
        """
        Test that the default environment of the App instance is set to Environments.DEVELOPMENT.

        This test creates a new App object and asserts that its 'env' attribute is equal to
        Environments.DEVELOPMENT, ensuring that the application initializes with the correct
        default environment setting.
        """
        app = App()
        self.assertEqual(app.env, Environments.DEVELOPMENT)

    async def testDefaultDebug(self):
        """
        Test that the default value of the 'debug' attribute in the App class is set to True upon initialization.
        """
        app = App()
        self.assertTrue(app.debug)

    async def testDefaultUrl(self):
        """
        Test that the default URL of the App instance is set to 'http://127.0.0.1'.
        """
        app = App()
        self.assertEqual(app.url, 'http://127.0.0.1')

    async def testDefaultPort(self):
        """
        Test that the default port for the App instance is set to 8000.
        """
        app = App()
        self.assertEqual(app.port, 8000)

    async def testDefaultWorkers(self):
        """
        Test that the default number of workers in the App instance is set to the value calculated by MaximumWorkers.
        """
        app = App()
        self.assertEqual(app.workers, MaximumWorkers().calculate())

    async def testDefaultReload(self):
        """
        Test that the default value of the 'reload' attribute in the App class is True.
        """
        app = App()
        self.assertTrue(app.reload)

    async def testDefaultTimezone(self):
        """
        Test that the default timezone of the App instance is set to 'UTC'.
        """
        app = App()
        self.assertEqual(app.timezone, 'UTC')

    async def testDefaultLocale(self):
        """
        Test that the default locale of the App instance is set to 'en'.

        This test creates a new App object and asserts that its 'locale' attribute
        is equal to 'en', ensuring the default locale configuration is correct.
        """
        app = App()
        self.assertEqual(app.locale, 'en')

    async def testDefaultFallbackLocale(self):
        """
        Test that the default fallback locale for the App instance is set to 'en'.
        """
        app = App()
        self.assertEqual(app.fallback_locale, 'en')

    async def testDefaultCipher(self):
        """
        Test that the default cipher for the App instance is set to AES_256_CBC.
        """
        app = App()
        self.assertEqual(app.cipher, Cipher.AES_256_CBC)

    async def testDefaultKey(self):
        """
        Test that the default value of the 'key' attribute in the App instance is None.

        This test creates a new App object and asserts that its 'key' attribute is not set,
        ensuring that the default state is as expected.
        """
        app = App()
        self.assertIsNone(app.key)

    async def testDefaultMaintenance(self):
        """
        Test that the default value of the 'maintenance' attribute in the App class is set to '/maintenance'.
        """
        app = App()
        self.assertEqual(app.maintenance, '/maintenance')

    async def testDefaultMaintenanceMode(self):
        """
        Test that creating an App with an invalid 'name' type raises an OrionisIntegrityException.
        """
        with self.assertRaises(OrionisIntegrityException):
            App(name=tuple)