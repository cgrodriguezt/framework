from orionis.foundation.config.mail.entities.mailers import Mailers
from orionis.foundation.config.mail.entities.smtp import Smtp
from orionis.foundation.config.mail.entities.file import File
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigMailMailers(AsyncTestCase):

    async def testDefaultInitialization(self):
        """
        Verify that a Mailers instance is initialized with correct default values.

        This method ensures that a Mailers instance is initialized with default factories
        and that the `smtp` and `file` attributes are instances of their respective types.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Mailers instance with default parameters
        mailers = Mailers()

        # Assert that smtp and file attributes are instances of their respective types
        self.assertIsInstance(mailers.smtp, Smtp)
        self.assertIsInstance(mailers.file, File)

    async def testTypeValidation(self):
        """
        Validate type checking for smtp and file attributes.

        This method ensures that providing invalid types for `smtp` or `file` raises
        an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Mailers with invalid smtp type; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Mailers(smtp="invalid_smtp")

        # Attempt to initialize Mailers with invalid file type; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Mailers(file="invalid_file")

    async def testCustomInitialization(self):
        """
        Validate custom initialization with valid parameters.

        This method ensures that valid Smtp and File instances can be provided to the
        Mailers constructor and are correctly assigned.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create custom Smtp and File instances
        custom_smtp = Smtp()
        custom_file = File()

        # Initialize Mailers with custom instances
        mailers = Mailers(smtp=custom_smtp, file=custom_file)

        # Assert that the custom instances are assigned correctly
        self.assertIs(mailers.smtp, custom_smtp)
        self.assertIs(mailers.file, custom_file)

    async def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Mailers.

        This method ensures that the `toDict` method returns a dictionary representation
        containing all fields with correct values and types.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Mailers instance
        mailers = Mailers()

        # Convert the Mailers instance to a dictionary
        result = mailers.toDict()

        # Assert that the dictionary contains the expected keys and value types
        self.assertIsInstance(result, dict)
        self.assertIn("smtp", result)
        self.assertIn("file", result)
        self.assertIsInstance(result["smtp"], dict)
        self.assertIsInstance(result["file"], dict)

    async def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Mailers.

        This method ensures that the Mailers class enforces keyword-only arguments
        during initialization and raises a TypeError if positional arguments are provided.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Mailers with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Mailers(Smtp(), File())