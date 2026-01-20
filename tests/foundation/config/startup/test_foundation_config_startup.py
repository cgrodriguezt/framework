from dataclasses import is_dataclass
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.startup import Configuration
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.auth.entities.auth import Auth
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.cors.entities.cors import Cors
from orionis.foundation.config.database.entities.database import Database
from orionis.foundation.config.roots.paths import Paths
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.queue.entities.queue import Queue
from orionis.foundation.config.session.entities.session import Session
from orionis.foundation.config.testing.entities.testing import Testing
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigStartup(SyncTestCase):

    def testConfigurationIsDataclass(self):
        """
        Verify that `Configuration` is implemented as a dataclass.

        This method checks that the `Configuration` class is implemented as a dataclass.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Assert that Configuration is a dataclass
        self.assertTrue(is_dataclass(Configuration))

    def testDefaultInitialization(self):
        """
        Ensure all fields of `Configuration` are initialized with their default factories and correct types.

        This method checks that all fields of `Configuration` are initialized with their default factories
        and are instances of their respective entity classes.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Configuration instance with default parameters
        config = Configuration()

        # Assert that each field is an instance of the expected class
        self.assertIsInstance(config, Configuration)
        self.assertIsInstance(config.app, App)
        self.assertIsInstance(config.auth, Auth)
        self.assertIsInstance(config.cache, Cache)
        self.assertIsInstance(config.cors, Cors)
        self.assertIsInstance(config.database, Database)
        self.assertIsInstance(config.filesystems, Filesystems)
        self.assertIsInstance(config.logging, Logging)
        self.assertIsInstance(config.mail, Mail)
        self.assertIsInstance(config.path, Paths)
        self.assertIsInstance(config.queue, Queue)
        self.assertIsInstance(config.session, Session)
        self.assertIsInstance(config.testing, Testing)

    def testAllSectionsHaveDefaultFactories(self):
        """
        Validate that every field in `Configuration` has a callable default factory.

        This method checks that every field in `Configuration` has a callable default factory.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Configuration instance
        config = Configuration()

        # Assert that each field has a callable default_factory
        for field in config.__dataclass_fields__.values():
            self.assertTrue(callable(field.default_factory),
                            f"Field {field.name} is missing default_factory")

    def testTypeValidationInPostInit(self):
        """
        Confirm type validation and dictionary conversion in `__post_init__`.

        This method validates that dictionaries are converted to entity instances and invalid types
        raise `OrionisIntegrityException` during post-initialization.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Valid dict conversion for the app section
        config = Configuration(app={"name": "TestApp"})
        self.assertIsInstance(config.app, App)

        # Invalid types for each section should raise an exception
        sections = [
            ("app", 123),
            ("auth", 123),
            ("cache", 123),
            ("cors", 123),
            ("database", 123),
            ("filesystems", 123),
            ("logging", 123),
            ("mail", 123),
            ("path", 123),
            ("queue", 123),
            ("session", 123),
            ("testing", 123),
        ]
        for section_name, wrong_value in sections:
            with self.subTest(section=section_name):
                kwargs = {section_name: wrong_value}
                # Attempt to initialize Configuration with invalid type; should raise exception
                with self.assertRaises(OrionisIntegrityException):
                    Configuration(**kwargs)

    def testToDictReturnsCompleteDictionary(self):
        """
        Validate that `toDict()` returns a dictionary containing all configuration sections.

        This method asserts that `toDict()` returns a dictionary containing all configuration sections.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Configuration instance
        config = Configuration()

        # Convert the Configuration instance to a dictionary
        config_dict = config.toDict()

        # Assert that the dictionary contains all configuration sections
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(set(config_dict.keys()), set(config.__dataclass_fields__.keys()))

    def testToDictReturnsNestedStructures(self):
        """
        Validate that nested configuration sections are represented as dictionaries in `toDict()` output.

        This method ensures that nested configuration sections are represented as dictionaries
        in the output of `toDict()`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Configuration instance
        config = Configuration()

        # Convert the Configuration instance to a dictionary
        config_dict = config.toDict()

        # Assert that nested sections are represented as dictionaries
        self.assertIsInstance(config_dict["app"], dict)
        self.assertIsInstance(config_dict["auth"], dict)
        self.assertIsInstance(config_dict["database"], dict)
        self.assertIsInstance(config_dict["path"], dict)

    def testMetadataIsAccessible(self):
        """
        Validate that field metadata is accessible and contains the 'description' and 'default' keys.

        This method checks that field metadata is accessible and contains the 'description' key as a string and the 'default' key.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Configuration instance
        config = Configuration()

        # Check that each field's metadata contains the required keys and correct types
        for field in config.__dataclass_fields__.values():
            metadata = field.metadata
            self.assertIn("description", metadata)
            self.assertIsInstance(metadata["description"], str)
            self.assertIn("default", metadata)

    def testConfigurationIsMutable(self):
        """
        Validate that attributes of `Configuration` can be modified after initialization.

        This method checks that attributes of `Configuration` can be modified after initialization.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Configuration instance
        config = Configuration()
        new_app = App()

        # Attempt to modify an attribute; should not raise an exception
        try:
            config.app = new_app
        except Exception as e:
            self.fail(f"Should be able to modify attributes, but got {type(e).__name__}")

    def testConfigurationEquality(self):
        """
        Validate the equality of `Configuration` instances based on their `app` section's key.

        This method creates two `Configuration` instances with identical `app` data and
        asserts that their `app.key` attributes are equal, verifying that the equality
        logic for the `app` section is consistent when initialized with the same data.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Prepare app data for both Configuration instances
        app_data = {"name": "TestApp"}

        # Create two Configuration instances with the same app data
        config1 = Configuration(app=app_data)
        config2 = Configuration(app=app_data)

        # Assert that the 'key' attribute of the 'app' section is equal for both instances
        self.assertEqual(config1.app.key, config2.app.key)
