from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.roots.paths import Paths
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigRootPaths(SyncTestCase):

    def testDefaultPathsInstantiation(self):
        """
        Verify instantiation of `Paths` with default values.

        This method ensures that a `Paths` instance can be created using default arguments and
        that the resulting object is an instance of `Paths`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Paths instance with default parameters
        paths = Paths()

        # Assert that the object is an instance of Paths
        self.assertIsInstance(paths, Paths)

    def testAllPathsAreStrings(self):
        """
        Verify that all attributes of `Paths` are non-empty strings.

        This method iterates through all fields of the `Paths` dataclass and asserts that each
        attribute is a non-empty string.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Paths instance
        paths = Paths()

        # Check that each field is a non-empty string
        for field_name in paths.__dataclass_fields__:
            value = getattr(paths, field_name)
            self.assertIsInstance(value, str)
            self.assertTrue(len(value) > 0)

    def testPathValidationRejectsNonStringValues(self):
        """
        Validate that non-string path values raise `OrionisIntegrityException`.

        This method attempts to instantiate `Paths` with a non-string value for a path field
        and asserts that an `OrionisIntegrityException` is raised.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Attempt to initialize Paths with a non-string value; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Paths(console=123)

    def testToDictReturnsCompleteDictionary(self):
        """
        Validate that `toDict()` returns a complete dictionary of all path fields.

        This method asserts that the dictionary returned by `toDict()` contains all fields
        defined in the `Paths` dataclass and that the dictionary has the correct length.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Paths instance
        paths = Paths()

        # Convert the Paths instance to a dictionary
        path_dict = paths.toDict()

        # Assert that the dictionary contains all fields and correct length
        self.assertIsInstance(path_dict, dict)
        self.assertEqual(len(path_dict), len(paths.__dataclass_fields__))
        for field in paths.__dataclass_fields__:
            self.assertIn(field, path_dict)

    def testFrozenDataclassBehavior(self):
        """
        Validate that the `Paths` dataclass is immutable (frozen).

        This method attempts to modify an attribute of a `Paths` instance after creation and
        asserts that an exception is raised due to immutability.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Paths instance
        paths = Paths()

        # Attempt to modify an attribute; should raise an exception due to immutability
        with self.assertRaises(Exception):
            paths.console_scheduler = "new/path"  # type: ignore

    def testPathMetadataIsAccessible(self):
        """
        Validate accessibility and structure of path field metadata.

        This method iterates through all fields of the `Paths` dataclass and asserts that each
        field's metadata contains both 'description' and 'default' keys, and that their values are of the expected types.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Paths instance
        paths = Paths()

        # Check that each field's metadata contains the required keys and correct types
        for field in paths.__dataclass_fields__.values():
            metadata = field.metadata
            self.assertIn("description", metadata)
            self.assertIn("default", metadata)
            self.assertIsInstance(metadata["description"], str)
            default_value = metadata["default"]
            if callable(default_value):
                default_value = default_value()
            self.assertIsInstance(default_value, str)
