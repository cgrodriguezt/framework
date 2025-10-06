from orionis.foundation.config.mail.entities.file import File
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigMailFile(SyncTestCase):

    def testDefaultPathValue(self):
        """
        Verify that a File instance is initialized with the correct default path.

        This method checks that a new File object has 'storage/mail' as the default path.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a File instance with default parameters
        file = File()

        # Assert that the default path is as expected
        self.assertEqual(file.path, "storage/mail")

    def testPathValidation(self):
        """
        Validate the path attribute for correct type and value.

        This method verifies that non-string paths or empty strings raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test non-string type for path
        with self.assertRaises(OrionisIntegrityException):
            File(path=123)

        # Test empty string for path
        with self.assertRaises(OrionisIntegrityException):
            File(path="")

    def testValidPathAssignment(self):
        """
        Validate that valid path assignments are accepted and stored correctly.

        This method verifies that string paths are accepted and stored properly.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Assign a valid string path
        test_path = "custom/path/to/mail"
        file = File(path=test_path)

        # Assert that the path is stored correctly
        self.assertEqual(file.path, test_path)

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for File.

        This method checks that the toDict method converts the File instance into a dictionary
        with the expected path field.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a File instance
        file = File()

        # Convert the File instance to a dictionary
        result = file.toDict()

        # Assert that the dictionary contains the expected path
        self.assertIsInstance(result, dict)
        self.assertEqual(result["path"], "storage/mail")

    def testHashability(self):
        """
        Validate hashability of File instances.

        This method verifies that File instances can be used in sets or as dictionary keys.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two File instances with different paths
        file1 = File()
        file2 = File(path="other/path")

        # Add both to a set; should contain two unique instances
        test_set = {file1, file2}
        self.assertEqual(len(test_set), 2)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for File.

        This method ensures that the class enforces kw_only=True in its dataclass decorator
        and raises a TypeError if positional arguments are used for initialization.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize File with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            File("storage/mail")