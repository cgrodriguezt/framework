from pathlib import Path
from unittest.mock import Mock
from orionis.foundation.contracts.application import IApplication
from orionis.services.file.directory import Directory
from orionis.test.cases.synchronous import SyncTestCase

class TestDirectory(SyncTestCase):

    def setUp(self) -> None:
        """
        Set up the test environment before each test method.

        Creates a mock application instance and configures it to return
        predefined path strings for various directory keys. Initializes
        a Directory instance with the mock application and defines test
        path data for validation.

        Returns
        -------
        None
        """
        # Create mock application instance
        self.mock_app: Mock = Mock(spec=IApplication)

        # Define test paths for different directories (using Path for OS compatibility)
        self.test_paths = {
            "root": str(Path("/app")),
            "app": str(Path("/app/app")),
            "console": str(Path("/app/app/console")),
            "exceptions": str(Path("/app/app/exceptions")),
            "http": str(Path("/app/app/http")),
            "models": str(Path("/app/app/models")),
            "providers": str(Path("/app/app/providers")),
            "notifications": str(Path("/app/app/notifications")),
            "services": str(Path("/app/app/services")),
            "jobs": str(Path("/app/app/jobs")),
            "bootstrap": str(Path("/app/bootstrap")),
            "config": str(Path("/app/config")),
            "database": str(Path("/app/database")),
            "resources": str(Path("/app/resources")),
            "routes": str(Path("/app/routes")),
            "storage": str(Path("/app/storage")),
            "tests": str(Path("/app/tests")),
        }

        # Configure mock application to return specific paths
        def mock_path_side_effect(key):
            return self.test_paths.get(key, f"/app/{key}")

        self.mock_app.path.side_effect = mock_path_side_effect

        # Create Directory instance with mock application
        self.directory = Directory(self.mock_app)

    def tearDown(self) -> None:
        """
        Clean up test resources after each test method completion.

        Resets all mock objects and test data to None to ensure clean
        state between test method executions and prevent test interference.

        Returns
        -------
        None
        """
        self.mock_app = None
        self.directory = None
        self.test_paths = None

    def testInitialization(self) -> None:
        """
        Test that Directory initializes correctly with an application instance.

        Validates that the Directory constructor properly stores the provided
        application instance and that the instance is accessible for path
        resolution operations.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If Directory initialization fails or application instance is not stored correctly.
        """
        # Test that Directory can be instantiated with an application
        directory = Directory(self.mock_app)
        self.assertIsNotNone(directory)

        # Test that the private app instance is properly set
        self.assertEqual(directory._Directory__app, self.mock_app)

    def testRootDirectory(self) -> None:
        """
        Test root directory path resolution.

        Validates that the root() method correctly calls the application's
        path() method with 'root' key and returns a Path object representing
        the application's root directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If root directory path is not resolved correctly or return type is invalid.
        """
        # Call root method and verify result
        result = self.directory.root()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("root")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["root"])

    def testAppDirectory(self) -> None:
        """
        Test application directory path resolution.

        Validates that the app() method correctly calls the application's
        path() method with 'app' key and returns a Path object representing
        the main application directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If app directory path is not resolved correctly or return type is invalid.
        """
        # Call app method and verify result
        result = self.directory.app()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("app")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["app"])

    def testConsoleDirectory(self) -> None:
        """
        Test console directory path resolution.

        Validates that the console() method correctly calls the application's
        path() method with 'console' key and returns a Path object representing
        the console directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If console directory path is not resolved correctly or return type is invalid.
        """
        # Call console method and verify result
        result = self.directory.console()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("console")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["console"])

    def testExceptionsDirectory(self) -> None:
        """
        Test exceptions directory path resolution.

        Validates that the exceptions() method correctly calls the application's
        path() method with 'exceptions' key and returns a Path object representing
        the exceptions directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If exceptions directory path is not resolved correctly or return type is invalid.
        """
        # Call exceptions method and verify result
        result = self.directory.exceptions()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("exceptions")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["exceptions"])

    def testHttpDirectory(self) -> None:
        """
        Test HTTP directory path resolution.

        Validates that the http() method correctly calls the application's
        path() method with 'http' key and returns a Path object representing
        the HTTP directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If HTTP directory path is not resolved correctly or return type is invalid.
        """
        # Call http method and verify result
        result = self.directory.http()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("http")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["http"])

    def testModelsDirectory(self) -> None:
        """
        Test models directory path resolution.

        Validates that the models() method correctly calls the application's
        path() method with 'models' key and returns a Path object representing
        the models directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If models directory path is not resolved correctly or return type is invalid.
        """
        # Call models method and verify result
        result = self.directory.models()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("models")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["models"])

    def testProvidersDirectory(self) -> None:
        """
        Test providers directory path resolution.

        Validates that the providers() method correctly calls the application's
        path() method with 'providers' key and returns a Path object representing
        the providers directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If providers directory path is not resolved correctly or return type is invalid.
        """
        # Call providers method and verify result
        result = self.directory.providers()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("providers")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["providers"])

    def testNotificationsDirectory(self) -> None:
        """
        Test notifications directory path resolution.

        Validates that the notifications() method correctly calls the application's
        path() method with 'notifications' key and returns a Path object representing
        the notifications directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If notifications directory path is not resolved correctly or return type is invalid.
        """
        # Call notifications method and verify result
        result = self.directory.notifications()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("notifications")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["notifications"])

    def testServicesDirectory(self) -> None:
        """
        Test services directory path resolution.

        Validates that the services() method correctly calls the application's
        path() method with 'services' key and returns a Path object representing
        the services directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If services directory path is not resolved correctly or return type is invalid.
        """
        # Call services method and verify result
        result = self.directory.services()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("services")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["services"])

    def testJobsDirectory(self) -> None:
        """
        Test jobs directory path resolution.

        Validates that the jobs() method correctly calls the application's
        path() method with 'jobs' key and returns a Path object representing
        the jobs directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If jobs directory path is not resolved correctly or return type is invalid.
        """
        # Call jobs method and verify result
        result = self.directory.jobs()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("jobs")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["jobs"])

    def testBootstrapDirectory(self) -> None:
        """
        Test bootstrap directory path resolution.

        Validates that the bootstrap() method correctly calls the application's
        path() method with 'bootstrap' key and returns a Path object representing
        the bootstrap directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If bootstrap directory path is not resolved correctly or return type is invalid.
        """
        # Call bootstrap method and verify result
        result = self.directory.bootstrap()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("bootstrap")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["bootstrap"])

    def testConfigDirectory(self) -> None:
        """
        Test configuration directory path resolution.

        Validates that the config() method correctly calls the application's
        path() method with 'config' key and returns a Path object representing
        the configuration directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If config directory path is not resolved correctly or return type is invalid.
        """
        # Call config method and verify result
        result = self.directory.config()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("config")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["config"])

    def testDatabaseDirectory(self) -> None:
        """
        Test database directory path resolution.

        Validates that the database() method correctly calls the application's
        path() method with 'database' key and returns a Path object representing
        the database directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If database directory path is not resolved correctly or return type is invalid.
        """
        # Call database method and verify result
        result = self.directory.database()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("database")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["database"])

    def testResourcesDirectory(self) -> None:
        """
        Test resources directory path resolution.

        Validates that the resources() method correctly calls the application's
        path() method with 'resources' key and returns a Path object representing
        the resources directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If resources directory path is not resolved correctly or return type is invalid.
        """
        # Call resources method and verify result
        result = self.directory.resources()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("resources")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["resources"])

    def testRoutesDirectory(self) -> None:
        """
        Test routes directory path resolution.

        Validates that the routes() method correctly calls the application's
        path() method with 'routes' key and returns a Path object representing
        the routes directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If routes directory path is not resolved correctly or return type is invalid.
        """
        # Call routes method and verify result
        result = self.directory.routes()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("routes")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["routes"])

    def testStorageDirectory(self) -> None:
        """
        Test storage directory path resolution.

        Validates that the storage() method correctly calls the application's
        path() method with 'storage' key and returns a Path object representing
        the storage directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If storage directory path is not resolved correctly or return type is invalid.
        """
        # Call storage method and verify result
        result = self.directory.storage()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("storage")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["storage"])

    def testTestsDirectory(self) -> None:
        """
        Test tests directory path resolution.

        Validates that the tests() method correctly calls the application's
        path() method with 'tests' key and returns a Path object representing
        the tests directory.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If tests directory path is not resolved correctly or return type is invalid.
        """
        # Call tests method and verify result
        result = self.directory.tests()

        # Assert that the application path method was called with correct key
        self.mock_app.path.assert_called_with("tests")

        # Assert that result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that result represents the expected path
        self.assertEqual(str(result), self.test_paths["tests"])

    def testAllDirectoryMethodsReturnPathObjects(self) -> None:
        """
        Test that all directory methods return Path objects.

        Validates that every public method in the Directory class returns
        a pathlib.Path object, ensuring consistent return types across
        all directory access methods.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If any directory method returns a non-Path object.
        """
        # Define all directory methods to test
        directory_methods = [
            "root", "app", "console", "exceptions", "http", "models",
            "providers", "notifications", "services", "jobs", "bootstrap",
            "config", "database", "resources", "routes", "storage", "tests",
        ]

        # Test each method returns a Path object
        for method_name in directory_methods:
            method = getattr(self.directory, method_name)
            result = method()
            self.assertIsInstance(result, Path, f"{method_name}() should return a Path object")

    def testApplicationPathMethodCalledWithCorrectKeys(self) -> None:
        """
        Test that application path method is called with correct keys.

        Validates that each Directory method calls the application's path()
        method with the appropriate key parameter, ensuring proper delegation
        to the application's path resolution system.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If any method calls application.path() with incorrect key parameter.
        """
        # Define method to key mapping
        method_key_mapping = {
            "root": "root",
            "app": "app",
            "console": "console",
            "exceptions": "exceptions",
            "http": "http",
            "models": "models",
            "providers": "providers",
            "notifications": "notifications",
            "services": "services",
            "jobs": "jobs",
            "bootstrap": "bootstrap",
            "config": "config",
            "database": "database",
            "resources": "resources",
            "routes": "routes",
            "storage": "storage",
            "tests": "tests",
        }

        # Reset mock to clear previous calls
        self.mock_app.path.reset_mock()

        # Test each method calls with correct key
        for method_name, expected_key in method_key_mapping.items():
            # Reset mock for each test
            self.mock_app.path.reset_mock()

            # Call the method
            method = getattr(self.directory, method_name)
            method()

            # Assert that path was called with the correct key
            self.mock_app.path.assert_called_once_with(expected_key)

    def testDirectoryMethodsWithNonExistentPaths(self) -> None:
        """
        Test directory methods behavior with non-existent paths.

        Validates that Directory methods handle cases where the application's
        path() method returns paths for non-existent directories, ensuring
        that Path objects are still created correctly.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If directory methods fail to handle non-existent paths correctly.
        """
        # Configure mock to return non-existent paths
        self.mock_app.path.side_effect = lambda key: f"/non/existent/{key}"

        # Test that methods still return Path objects for non-existent paths
        result = self.directory.root()
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), str(Path("/non/existent/root")))

        result = self.directory.app()
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), str(Path("/non/existent/app")))

    def testDirectoryMethodsWithEmptyPaths(self) -> None:
        """
        Test directory methods behavior with empty path strings.

        Validates that Directory methods handle cases where the application's
        path() method returns empty strings, ensuring that Path objects
        are created correctly even with empty path values.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If directory methods fail to handle empty path strings correctly.
        """
        # Configure mock to return empty paths
        self.mock_app.path.side_effect = lambda key: ""

        # Test that methods still return Path objects for empty paths
        result = self.directory.root()
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), ".")

        result = self.directory.config()
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), ".")

    def testMultipleDirectoryInstancesWithSameApp(self) -> None:
        """
        Test multiple Directory instances sharing the same application.

        Validates that multiple Directory instances can be created with
        the same application instance and that they behave consistently,
        ensuring proper isolation and shared resource management.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If multiple Directory instances do not behave consistently.
        """
        # Create multiple Directory instances with same application
        directory1 = Directory(self.mock_app)
        directory2 = Directory(self.mock_app)

        # Test that both instances return same paths
        result1 = directory1.root()
        result2 = directory2.root()

        self.assertEqual(str(result1), str(result2))
        self.assertIsInstance(result1, Path)
        self.assertIsInstance(result2, Path)

        # Test that both instances call the same application methods
        self.assertEqual(directory1._Directory__app, directory2._Directory__app)

    def testDirectoryMethodsConsistency(self) -> None:
        """
        Test consistency of directory method calls and return values.

        Validates that repeated calls to the same Directory method return
        consistent results and that the application's path() method is
        called consistently for each invocation.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If directory methods return inconsistent results across multiple calls.
        """
        # Test consistency across multiple calls
        first_result = self.directory.root()
        second_result = self.directory.root()

        # Results should be equivalent (same path)
        self.assertEqual(str(first_result), str(second_result))
        self.assertIsInstance(first_result, Path)
        self.assertIsInstance(second_result, Path)

        # Test that application path method is called each time
        call_count = self.mock_app.path.call_count
        self.directory.root()
        self.assertEqual(self.mock_app.path.call_count, call_count + 1)
