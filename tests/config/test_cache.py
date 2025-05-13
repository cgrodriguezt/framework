from dataclasses import asdict
import json
from orionis.luminate.test import TestCase
from orionis.luminate.config.cache import Cache

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
        cache = Cache()
        self.assertEqual(cache.default.value, "memory")
        self.assertEqual(cache.stores.file.path, "storage/framework/cache/data")