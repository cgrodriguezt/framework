from orionis.test.cases.synchronous import SyncTestCase
from orionis.metadata.package import PypiOrionisPackage
from unittest.mock import patch, Mock
import requests

class TestPypiOrionisPackage(SyncTestCase):
    """
    Test suite for the PypiOrionisPackage class.

    This test class provides comprehensive coverage for all methods and error scenarios
    of the PypiOrionisPackage class, ensuring robust validation of package metadata
    retrieval from the PyPI API.
    """

    def setUp(self) -> None:
        """
        Set up test environment before each test method.

        Initializes sample data that mimics PyPI API response structure for testing
        various scenarios including successful responses and error conditions.

        Notes
        -----
        The sample_pypi_response contains a complete mock of PyPI API response
        structure including all expected metadata fields.
        """
        self.sample_pypi_response = {
            "info": {
                "name": "orionis",
                "version": "0.690.0",
                "author": "Raul Mauricio Uñate Castro",
                "author_email": "raulmauriciounate@gmail.com",
                "summary": "Orionis Framework – Elegant, Fast, and Powerful.",
                "description": "A comprehensive Python framework for building elegant and powerful applications.",
                "description_content_type": "text/markdown",
                "license": "MIT",
                "classifiers": [
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: MIT License",
                    "Programming Language :: Python :: 3.12",
                ],
                "requires_python": ">=3.12",
                "keywords": ["orionis", "framework", "python"],
                "project_urls": {
                    "Homepage": "https://orionis-framework.com/",
                },
            },
        }

    @patch("requests.get")
    def testInitializationSuccess(self, mock_get):
        """
        Test successful initialization of PypiOrionisPackage.

        This test verifies that the class initializes correctly when the PyPI API
        responds with valid data, ensuring that getAllData() is called during
        initialization and the internal _info dictionary is populated.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test validates the happy path of package initialization where all
        data is successfully retrieved from PyPI.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance
        package = PypiOrionisPackage()

        # Verify API was called
        mock_get.assert_called_once()
        self.assertEqual(package._info, self.sample_pypi_response["info"])

    @patch("requests.get")
    def testGetAllDataSuccess(self, mock_get):
        """
        Test successful data retrieval from PyPI API.

        This test validates that getAllData() method correctly processes a successful
        API response and returns the expected data structure while updating the
        internal _info attribute.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test ensures that the getAllData method properly handles successful
        API responses and extracts the info section correctly.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getAllData
        package = PypiOrionisPackage()
        result = package.getAllData()

        # Verify the result
        self.assertEqual(result, self.sample_pypi_response["info"])
        self.assertEqual(package._info, self.sample_pypi_response["info"])

    @patch("requests.get")
    def testGetAllDataRequestError(self, mock_get):
        """
        Test getAllData method handling of network errors.

        This test verifies that the method properly raises ConnectionError when
        network-related issues occur during API requests, such as timeouts or
        connection failures.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate network failure.

        Notes
        -----
        This test ensures proper error handling for network connectivity issues
        and validates that appropriate error messages are provided to users.
        """
        # Configure mock to raise RequestException
        mock_get.side_effect = requests.RequestException("Network error")

        # Verify that ConnectionError is raised
        with self.assertRaises(ConnectionError) as context:
            PypiOrionisPackage()

        self.assertIn("Error fetching data from PyPI", str(context.exception))

    @patch("requests.get")
    def testGetAllDataMissingInfoKey(self, mock_get):
        """
        Test getAllData method handling of invalid response structure.

        This test validates that the method raises ValueError when the PyPI API
        response lacks the expected 'info' key or contains an empty info section.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate invalid API response structure.

        Notes
        -----
        This test ensures robust validation of API response structure and proper
        error handling when the response format is unexpected.
        """
        # Configure mock response without 'info' key
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        # Verify that ValueError is raised
        with self.assertRaises(ValueError) as context:
            PypiOrionisPackage()

        self.assertIn("Invalid response structure from PyPI", str(context.exception))

    @patch("requests.get")
    def testGetName(self, mock_get):
        """
        Test the getName method of PypiOrionisPackage.

        This test verifies that the getName method correctly retrieves and returns
        the package name from the internal metadata dictionary populated during
        initialization.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test validates that the package name is correctly extracted from
        the PyPI metadata and returned as expected.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getName
        package = PypiOrionisPackage()
        result = package.getName()

        # Verify the result
        self.assertEqual(result, "orionis")

    @patch("requests.get")
    def testGetVersion(self, mock_get):
        """
        Test the getVersion method of PypiOrionisPackage.

        This test validates that the getVersion method correctly retrieves and
        returns the version string from the package metadata obtained from PyPI.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test ensures that version information is properly extracted from
        the metadata and returned in the expected format.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getVersion
        package = PypiOrionisPackage()
        result = package.getVersion()

        # Verify the result
        self.assertEqual(result, "0.690.0")

    @patch("requests.get")
    def testGetAuthor(self, mock_get):
        """
        Test the getAuthor method of PypiOrionisPackage.

        This test verifies that the getAuthor method correctly retrieves and
        returns the author name from the package metadata dictionary.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test validates that author information is correctly extracted
        from the PyPI metadata and returned as expected.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getAuthor
        package = PypiOrionisPackage()
        result = package.getAuthor()

        # Verify the result
        self.assertEqual(result, "Raul Mauricio Uñate Castro")

    @patch("requests.get")
    def testGetAuthorEmail(self, mock_get):
        """
        Test the getAuthorEmail method of PypiOrionisPackage.

        This test validates that the getAuthorEmail method correctly retrieves
        and returns the author's email address from the package metadata.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test ensures that author email information is properly extracted
        from the metadata and returned in the expected format.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getAuthorEmail
        package = PypiOrionisPackage()
        result = package.getAuthorEmail()

        # Verify the result
        self.assertEqual(result, "raulmauriciounate@gmail.com")

    @patch("requests.get")
    def testGetDescription(self, mock_get):
        """
        Test the getDescription method of PypiOrionisPackage.

        This test verifies that the getDescription method correctly retrieves
        and returns the package summary description from the metadata.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test validates that the package summary description is correctly
        extracted from the PyPI metadata and returned as expected.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getDescription
        package = PypiOrionisPackage()
        result = package.getDescription()

        # Verify the result
        self.assertEqual(result, "Orionis Framework – Elegant, Fast, and Powerful.")

    @patch("requests.get")
    def testGetUrl(self, mock_get):
        """
        Test the getUrl method of PypiOrionisPackage.

        This test validates that the getUrl method correctly retrieves and
        returns the homepage URL from the project URLs section of the metadata.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test ensures that the homepage URL is properly extracted from
        the project_urls dictionary and returned as expected.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getUrl
        package = PypiOrionisPackage()
        result = package.getUrl()

        # Verify the result
        self.assertEqual(result, "https://orionis-framework.com/")

    @patch("requests.get")
    def testGetLongDescription(self, mock_get):
        """
        Test the getLongDescription method of PypiOrionisPackage.

        This test verifies that the getLongDescription method correctly retrieves
        and returns the detailed package description from the metadata.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test validates that the long description is correctly extracted
        from the PyPI metadata and returned in the expected format.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getLongDescription
        package = PypiOrionisPackage()
        result = package.getLongDescription()

        # Verify the result
        self.assertEqual(result, "A comprehensive Python framework for building elegant and powerful applications.")

    @patch("requests.get")
    def testGetDescriptionContentType(self, mock_get):
        """
        Test the getDescriptionContentType method of PypiOrionisPackage.

        This test validates that the getDescriptionContentType method correctly
        retrieves and returns the content type of the package description.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test ensures that the description content type is properly extracted
        from the metadata and returned as expected (e.g., 'text/markdown').
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getDescriptionContentType
        package = PypiOrionisPackage()
        result = package.getDescriptionContentType()

        # Verify the result
        self.assertEqual(result, "text/markdown")

    @patch("requests.get")
    def testGetLicense(self, mock_get):
        """
        Test the getLicense method of PypiOrionisPackage.

        This test verifies that the getLicense method correctly retrieves and
        returns the license information from the package metadata, with proper
        handling of the default "MIT" license when no license is specified.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test validates that license information is correctly extracted
        and that the method properly defaults to "MIT" when needed.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getLicense
        package = PypiOrionisPackage()
        result = package.getLicense()

        # Verify the result
        self.assertEqual(result, "MIT")

    @patch("requests.get")
    def testGetLicenseDefaultValue(self, mock_get):
        """
        Test the getLicense method with empty license field.

        This test validates that the getLicense method properly defaults to "MIT"
        when the license field is empty or None in the package metadata.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate API response with empty license.

        Notes
        -----
        This test ensures that the method handles edge cases where license
        information is not properly specified in the PyPI metadata.
        """
        # Configure mock response with empty license
        response_data = self.sample_pypi_response.copy()
        response_data["info"]["license"] = ""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = response_data
        mock_get.return_value = mock_response

        # Create instance and test getLicense
        package = PypiOrionisPackage()
        result = package.getLicense()

        # Verify the result defaults to "MIT"
        self.assertEqual(result, "MIT")

    @patch("requests.get")
    def testGetClassifiers(self, mock_get):
        """
        Test the getClassifiers method of PypiOrionisPackage.

        This test verifies that the getClassifiers method correctly retrieves
        and returns the list of classifiers from the package metadata.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test validates that the classifiers list is correctly extracted
        from the PyPI metadata and returned as a list of strings.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getClassifiers
        package = PypiOrionisPackage()
        result = package.getClassifiers()

        # Verify the result
        expected_classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.12",
        ]
        self.assertEqual(result, expected_classifiers)

    @patch("requests.get")
    def testGetPythonVersion(self, mock_get):
        """
        Test the getPythonVersion method of PypiOrionisPackage.

        This test validates that the getPythonVersion method correctly retrieves
        and returns the Python version requirement from the package metadata.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test ensures that Python version requirements are correctly
        extracted from the metadata and returned in the expected format.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getPythonVersion
        package = PypiOrionisPackage()
        result = package.getPythonVersion()

        # Verify the result
        self.assertEqual(result, ">=3.12")

    @patch("requests.get")
    def testGetKeywords(self, mock_get):
        """
        Test the getKeywords method of PypiOrionisPackage.

        This test verifies that the getKeywords method correctly retrieves
        and returns the list of keywords from the package metadata.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate successful API response.

        Notes
        -----
        This test validates that the keywords list is correctly extracted
        from the PyPI metadata and returned as a list of strings.
        """
        # Configure mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_pypi_response
        mock_get.return_value = mock_response

        # Create instance and test getKeywords
        package = PypiOrionisPackage()
        result = package.getKeywords()

        # Verify the result
        expected_keywords = ["orionis", "framework", "python"]
        self.assertEqual(result, expected_keywords)

    @patch("requests.get")
    def testKeyErrorHandling(self, mock_get):
        """
        Test proper handling of missing keys in metadata.

        This test validates that methods properly raise KeyError when expected
        keys are missing from the metadata dictionary, ensuring robust error
        handling for incomplete API responses.

        Parameters
        ----------
        mock_get : Mock
            Mocked requests.get method to simulate incomplete API response.

        Notes
        -----
        This test ensures that the class handles edge cases where certain
        metadata fields are missing from the PyPI API response.
        """
        # Configure mock response with incomplete data
        incomplete_response = {"info": {"name": "orionis"}}
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = incomplete_response
        mock_get.return_value = mock_response

        # Create instance
        package = PypiOrionisPackage()

        # Test that KeyError is raised for missing keys
        with self.assertRaises(KeyError):
            package.getVersion()

        with self.assertRaises(KeyError):
            package.getAuthor()

        with self.assertRaises(KeyError):
            package.getUrl()
