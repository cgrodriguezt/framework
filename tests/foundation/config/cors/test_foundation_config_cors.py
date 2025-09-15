from orionis.foundation.config.cors.entities.cors import Cors
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigCors(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Tests the default values assigned by the Cors configuration.

        This method verifies that a newly instantiated Cors object has the expected default settings for all configuration parameters. It checks each attribute individually to ensure the defaults are correctly set.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. Assertions are used to validate the default state of the Cors object.

        Notes
        -----
        The expected default values are:
            - allow_origins : list of str
                ["*"]
            - allow_origin_regex : None
            - allow_methods : list of str
                ["*"]
            - allow_headers : list of str
                ["*"]
            - expose_headers : list of str
                []
            - allow_credentials : bool
                False
            - max_age : int
                600
        """

        # Instantiate Cors with default parameters
        cors = Cors()

        # Assert default allowed origins
        self.assertEqual(cors.allow_origins, ["*"])

        # Assert default origin regex is None
        self.assertIsNone(cors.allow_origin_regex)

        # Assert default allowed methods
        self.assertEqual(cors.allow_methods, ["*"])

        # Assert default allowed headers
        self.assertEqual(cors.allow_headers, ["*"])

        # Assert default exposed headers
        self.assertEqual(cors.expose_headers, [])

        # Assert default credentials setting
        self.assertFalse(cors.allow_credentials)

        # Assert default max age
        self.assertEqual(cors.max_age, 600)

    async def testCustomValues(self):
        """
        Validates custom value assignment for all Cors configuration parameters.

        This test ensures that when a Cors object is instantiated with custom configuration values,
        each attribute accurately reflects the provided value. It covers all configurable parameters
        of the Cors entity and asserts their correct assignment.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. Assertions are used to validate the state of the Cors object.

        Notes
        -----
        The following custom values are tested:
            - allow_origins : list of str
                ["https://example.com"]
            - allow_origin_regex : str
                "^https://.*\\.example\\.com$"
            - allow_methods : list of str
                ["GET", "POST"]
            - allow_headers : list of str
                ["Authorization", "Content-Type"]
            - expose_headers : list of str
                ["X-Custom-Header"]
            - allow_credentials : bool
                True
            - max_age : int
                3600
        """

        # Instantiate Cors with custom parameters
        cors = Cors(
            allow_origins=["https://example.com"],
            allow_origin_regex="^https://.*\\.example\\.com$",
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type"],
            expose_headers=["X-Custom-Header"],
            allow_credentials=True,
            max_age=3600
        )

        # Assert custom allowed origins
        self.assertEqual(cors.allow_origins, ["https://example.com"])

        # Assert custom origin regex
        self.assertEqual(cors.allow_origin_regex, "^https://.*\\.example\\.com$")

        # Assert custom allowed methods
        self.assertEqual(cors.allow_methods, ["GET", "POST"])

        # Assert custom allowed headers
        self.assertEqual(cors.allow_headers, ["Authorization", "Content-Type"])

        # Assert custom exposed headers
        self.assertEqual(cors.expose_headers, ["X-Custom-Header"])

        # Assert custom credentials setting
        self.assertTrue(cors.allow_credentials)

        # Assert custom max age
        self.assertEqual(cors.max_age, 3600)

    async def testInvalidAllowOriginsType(self):
        """
        Validates type enforcement for the 'allow_origins' parameter.

        This test checks that the `Cors` configuration enforces the correct type for the
        `allow_origins` parameter. Specifically, it verifies that passing a string instead
        of a list to `allow_origins` results in an `OrionisIntegrityException` being raised.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. The test passes if the exception is raised,
            otherwise it fails.

        Raises
        ------
        OrionisIntegrityException
            If `allow_origins` is not a list.
        """

        # Attempt to instantiate Cors with an invalid type for allow_origins (string instead of list)
        with self.assertRaises(OrionisIntegrityException):
            Cors(allow_origins="*")

    async def testInvalidAllowOriginRegexType(self):
        """
        Validates type enforcement for the 'allow_origin_regex' parameter.

        This test ensures that the `Cors` configuration enforces the correct type for the
        `allow_origin_regex` parameter. Specifically, it verifies that passing a value
        that is neither a string nor None (such as an integer) to `allow_origin_regex`
        results in an `OrionisIntegrityException` being raised.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The method does not return any value. The test passes if the exception is raised,
            otherwise it fails.

        Raises
        ------
        OrionisIntegrityException
            If `allow_origin_regex` is not a string or None.
        """

        # Attempt to instantiate Cors with an invalid type for allow_origin_regex (integer instead of string or None)
        with self.assertRaises(OrionisIntegrityException):
            Cors(allow_origin_regex=123)

    async def testInvalidAllowMethodsType(self):
        """
        Validates type enforcement for the 'allow_methods' parameter.

        This test ensures that the `Cors` configuration enforces the correct type for the
        `allow_methods` parameter. Specifically, it verifies that passing a string instead
        of a list to `allow_methods` results in an `OrionisIntegrityException` being raised.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. The test passes if the exception is raised,
            otherwise it fails.

        Raises
        ------
        OrionisIntegrityException
            If `allow_methods` is not a list.

        Notes
        -----
        The `allow_methods` parameter must be a list of strings. Passing any other type,
        such as a string, should trigger an integrity exception.
        """

        # Attempt to instantiate Cors with an invalid type for allow_methods (string instead of list)
        with self.assertRaises(OrionisIntegrityException):
            Cors(allow_methods="GET")

    async def testInvalidAllowHeadersType(self):
        """
        Validates type enforcement for the 'allow_headers' parameter.

        This test ensures that the `Cors` configuration enforces the correct type for the
        `allow_headers` parameter. Specifically, it verifies that passing a string instead
        of a list to `allow_headers` results in an `OrionisIntegrityException` being raised.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The method does not return any value. The test passes if the exception is raised,
            otherwise it fails.

        Raises
        ------
        OrionisIntegrityException
            If `allow_headers` is not a list.

        Notes
        -----
        The `allow_headers` parameter must be a list of strings. Passing any other type,
        such as a string, should trigger an integrity exception.
        """

        # Attempt to instantiate Cors with an invalid type for allow_headers (string instead of list)
        with self.assertRaises(OrionisIntegrityException):
            Cors(allow_headers="Authorization")

    async def testInvalidExposeHeadersType(self):
        """
        Validates type enforcement for the 'expose_headers' parameter.

        This test ensures that the `Cors` configuration enforces the correct type for the
        `expose_headers` parameter. Specifically, it verifies that passing a string instead
        of a list to `expose_headers` results in an `OrionisIntegrityException` being raised.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. The test passes if the exception is raised,
            otherwise it fails.

        Raises
        ------
        OrionisIntegrityException
            If `expose_headers` is not a list.

        Notes
        -----
        The `expose_headers` parameter must be a list of strings. Passing any other type,
        such as a string, should trigger an integrity exception.
        """

        # Attempt to instantiate Cors with an invalid type for expose_headers (string instead of list)
        with self.assertRaises(OrionisIntegrityException):
            Cors(expose_headers="X-Custom-Header")

    async def testInvalidAllowCredentialsType(self):
        """
        Validates type enforcement for the 'allow_credentials' parameter.

        This test checks that the `Cors` configuration enforces the correct type for the
        `allow_credentials` parameter. Specifically, it verifies that passing a value
        that is not a boolean (such as a string) to `allow_credentials` results in an
        `OrionisIntegrityException` being raised.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. The test passes if the exception is raised,
            otherwise it fails.

        Raises
        ------
        OrionisIntegrityException
            If `allow_credentials` is not a boolean.

        Notes
        -----
        The `allow_credentials` parameter must be a boolean. Passing any other type,
        such as a string, should trigger an integrity exception.
        """

        # Attempt to instantiate Cors with an invalid type for allow_credentials (string instead of boolean)
        with self.assertRaises(OrionisIntegrityException):
            Cors(allow_credentials="yes")

    async def testInvalidMaxAgeType(self):
        """
        Validates type enforcement for the 'max_age' parameter.

        This test ensures that the `Cors` configuration enforces the correct type for the
        `max_age` parameter. Specifically, it verifies that passing a value that is not
        an integer or None (such as a string) to `max_age` results in an
        `OrionisIntegrityException` being raised.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. The test passes if the exception is raised,
            otherwise it fails.

        Raises
        ------
        OrionisIntegrityException
            If `max_age` is not an integer or None.

        Notes
        -----
        The `max_age` parameter must be an integer or None. Passing any other type,
        such as a string, should trigger an integrity exception.
        """

        # Attempt to instantiate Cors with an invalid type for max_age (string instead of integer or None)
        with self.assertRaises(OrionisIntegrityException):
            Cors(max_age="3600")