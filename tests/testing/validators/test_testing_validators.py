from pathlib import Path
from orionis.foundation.config.testing.enums.drivers import PersistentDrivers
from orionis.foundation.config.testing.enums.mode import ExecutionMode
from orionis.foundation.config.testing.enums.verbosity import VerbosityMode
from orionis.test.cases.synchronous import SyncTestCase
from orionis.support.facades.workers import Workers
from orionis.test.exceptions import OrionisTestValueError
from orionis.test.validators import (
    ValidWorkers,
    ValidBasePath,
    ValidExecutionMode,
    ValidFailFast,
    ValidFolderPath,
    ValidModuleName,
    ValidNamePattern,
    ValidPattern,
    ValidPersistentDriver,
    ValidPersistent,
    ValidPrintResult,
    ValidTags,
    ValidThrowException,
    ValidVerbosity,
    ValidWebReport,
)

class TestTestingDumper(SyncTestCase):

    def testValidWorkers(self) -> None:
        """
        Test the ValidWorkers validator for correct worker count validation.

        Validates that the ValidWorkers function accepts integer values within the allowed range
        and raises OrionisTestValueError for invalid values such as zero, negative numbers,
        values exceeding the maximum, or non-integer types.

        Returns
        -------
        None
        """
        # Get the maximum allowed number of workers from the Workers facade
        max_allowed = Workers.calculate()

        # Valid cases: should return the input value if within allowed range
        self.assertEqual(ValidWorkers(1), 1)
        self.assertEqual(ValidWorkers(max_allowed), max_allowed)

        # Invalid cases: should raise OrionisTestValueError for out-of-range or wrong type
        with self.assertRaises(OrionisTestValueError):
            ValidWorkers(0)  # Zero is not allowed
        with self.assertRaises(OrionisTestValueError):
            ValidWorkers(max_allowed + 1)  # Exceeds maximum allowed
        with self.assertRaises(OrionisTestValueError):
            ValidWorkers(-5)  # Negative value is not allowed
        with self.assertRaises(OrionisTestValueError):
            ValidWorkers(-1)  # Another negative value
        with self.assertRaises(OrionisTestValueError):
            ValidWorkers("not_an_int")  # Non-integer type is not allowed
        with self.assertRaises(OrionisTestValueError):
            ValidWorkers(3.14)  # Float value is not allowed
        with self.assertRaises(OrionisTestValueError):
            ValidWorkers(None)  # None is not allowed
        with self.assertRaises(OrionisTestValueError):
            ValidWorkers([])  # List is not allowed
        with self.assertRaises(OrionisTestValueError):
            ValidWorkers({"workers": 2})  # Dictionary is not allowed

    def testValidBasePath(self) -> None:
        """
        Test the ValidBasePath validator for correct base path validation.

        Checks that ValidBasePath accepts valid path strings and Path objects, returning a pathlib.Path instance.
        Ensures that invalid inputs such as empty strings, None, and non-path types raise OrionisTestValueError.

        Returns
        -------
        None
        """
        # Valid cases: should return a Path instance for valid string or Path input
        self.assertIsInstance(ValidBasePath("/tmp"), Path)
        self.assertIsInstance(ValidBasePath(Path("/tmp")), Path)
        self.assertIsInstance(ValidBasePath("  /tmp/test  "), Path)

        # Test that whitespace is stripped properly by comparing with a clean path
        cleaned_path = ValidBasePath("  /tmp/test  ")
        expected_path = Path("/tmp/test")
        self.assertEqual(cleaned_path, expected_path)

        # Invalid cases: should raise OrionisTestValueError for empty string, None, or non-path type
        with self.assertRaises(OrionisTestValueError):
            ValidBasePath("")
        with self.assertRaises(OrionisTestValueError):
            ValidBasePath("   ")
        with self.assertRaises(OrionisTestValueError):
            ValidBasePath(Path())
        with self.assertRaises(OrionisTestValueError):
            ValidBasePath(Path("   "))
        with self.assertRaises(OrionisTestValueError):
            ValidBasePath(None)
        with self.assertRaises(OrionisTestValueError):
            ValidBasePath(123)
        with self.assertRaises(OrionisTestValueError):
            ValidBasePath([])

    def testValidExecutionMode(self) -> None:
        """
        Test the ValidExecutionMode validator for execution mode validation.

        Validates that ValidExecutionMode accepts valid execution mode strings and enum values,
        returning the corresponding string value. Ensures that invalid inputs such as unknown strings
        and non-enum types raise OrionisTestValueError.

        Returns
        -------
        None
        """
        # Valid cases: should return the string value for valid mode string or enum input
        self.assertEqual(ValidExecutionMode("parallel"), ExecutionMode.PARALLEL.value)
        self.assertEqual(ValidExecutionMode("PARALLEL"), ExecutionMode.PARALLEL.value)
        self.assertEqual(ValidExecutionMode("sequential"), ExecutionMode.SEQUENTIAL.value)
        self.assertEqual(ValidExecutionMode("SEQUENTIAL"), ExecutionMode.SEQUENTIAL.value)
        self.assertEqual(ValidExecutionMode(ExecutionMode.SEQUENTIAL), ExecutionMode.SEQUENTIAL.value)
        self.assertEqual(ValidExecutionMode(ExecutionMode.PARALLEL), ExecutionMode.PARALLEL.value)

        # Invalid cases: should raise OrionisTestValueError for unknown string or non-enum type
        with self.assertRaises(OrionisTestValueError):
            ValidExecutionMode("INVALID")  # Unknown execution mode string
        with self.assertRaises(OrionisTestValueError):
            ValidExecutionMode("unknown")  # Unknown execution mode string
        with self.assertRaises(OrionisTestValueError):
            ValidExecutionMode("")  # Empty string
        with self.assertRaises(OrionisTestValueError):
            ValidExecutionMode(None)  # None value
        with self.assertRaises(OrionisTestValueError):
            ValidExecutionMode(123)        # Non-enum type
        with self.assertRaises(OrionisTestValueError):
            ValidExecutionMode([])         # List type

    def testValidFailFast(self) -> None:
        """
        Test the ValidFailFast validator for fail-fast configuration validation.

        Ensures that ValidFailFast accepts valid boolean inputs and returns the corresponding
        boolean value. Raises OrionisTestValueError for non-boolean types or None.

        Returns
        -------
        None
        """
        # Valid cases: should return True or False for boolean input
        self.assertTrue(ValidFailFast(True))
        self.assertFalse(ValidFailFast(False))

        # Invalid cases: should raise OrionisTestValueError for non-boolean or None input
        with self.assertRaises(OrionisTestValueError):
            ValidFailFast("not_bool")
        with self.assertRaises(OrionisTestValueError):
            ValidFailFast("true")  # String representation of boolean
        with self.assertRaises(OrionisTestValueError):
            ValidFailFast(1)  # Integer that could be truthy
        with self.assertRaises(OrionisTestValueError):
            ValidFailFast(0)  # Integer that could be falsy
        with self.assertRaises(OrionisTestValueError):
            ValidFailFast(None)
        with self.assertRaises(OrionisTestValueError):
            ValidFailFast([])
        with self.assertRaises(OrionisTestValueError):
            ValidFailFast({})

    def testValidFolderPath(self) -> None:
        """
        Test the ValidFolderPath validator for folder path validation.

        Checks that ValidFolderPath accepts valid folder path strings, including those with whitespace,
        and returns the normalized string path. Ensures that empty strings, None, or non-string types
        raise OrionisTestValueError.

        Returns
        -------
        None
        """
        # Valid cases: should return the normalized string path for valid input
        self.assertEqual(ValidFolderPath("/tmp"), "/tmp")
        self.assertEqual(ValidFolderPath("  /tmp  "), "/tmp")
        self.assertEqual(ValidFolderPath("/path/to/folder"), "/path/to/folder")
        self.assertEqual(ValidFolderPath("  /path/with/spaces  "), "/path/with/spaces")

        # Invalid cases: should raise OrionisTestValueError for empty string, None, or non-string type
        with self.assertRaises(OrionisTestValueError):
            ValidFolderPath("")
        with self.assertRaises(OrionisTestValueError):
            ValidFolderPath("   ")
        with self.assertRaises(OrionisTestValueError):
            ValidFolderPath(None)
        with self.assertRaises(OrionisTestValueError):
            ValidFolderPath(123)
        with self.assertRaises(OrionisTestValueError):
            ValidFolderPath([])
        with self.assertRaises(OrionisTestValueError):
            ValidFolderPath({"path": "/tmp"})

    def testValidModuleName(self) -> None:
        """
        Test the ValidModuleName validator for module name validation.

        Validates that ValidModuleName accepts valid non-empty string module names and returns
        the normalized string value. Ensures that empty strings, None, or non-string types
        raise OrionisTestValueError.

        Returns
        -------
        None
        """
        # Valid cases: should return the string for a valid module name
        self.assertEqual(ValidModuleName("mod"), "mod")
        self.assertEqual(ValidModuleName("test_module"), "test_module")
        self.assertEqual(ValidModuleName("my.module.name"), "my.module.name")

        # Invalid cases: should raise OrionisTestValueError for empty string, None, or non-string type
        with self.assertRaises(OrionisTestValueError):
            ValidModuleName("")
        with self.assertRaises(OrionisTestValueError):
            ValidModuleName("   ")
        with self.assertRaises(OrionisTestValueError):
            ValidModuleName(None)
        with self.assertRaises(OrionisTestValueError):
            ValidModuleName(123)
        with self.assertRaises(OrionisTestValueError):
            ValidModuleName([])
        with self.assertRaises(OrionisTestValueError):
            ValidModuleName({"module": "name"})

    def testValidNamePattern(self) -> None:
        """
        Test the ValidNamePattern validator for name pattern validation.

        Ensures that ValidNamePattern accepts valid non-empty string patterns and None,
        returning the normalized string pattern or None. Raises OrionisTestValueError for
        empty strings or non-string types.

        Returns
        -------
        None
        """
        # Valid cases: should return the normalized string for a valid pattern or None
        self.assertEqual(ValidNamePattern("test_*"), "test_*")
        self.assertEqual(ValidNamePattern("  test_pattern  "), "test_pattern")
        self.assertEqual(ValidNamePattern("Test*Pattern"), "Test*Pattern")
        self.assertIsNone(ValidNamePattern(None))

        # Invalid cases: should raise OrionisTestValueError for empty string or non-string type
        with self.assertRaises(OrionisTestValueError):
            ValidNamePattern("")
        with self.assertRaises(OrionisTestValueError):
            ValidNamePattern("   ")
        with self.assertRaises(OrionisTestValueError):
            ValidNamePattern(123)
        with self.assertRaises(OrionisTestValueError):
            ValidNamePattern([])
        with self.assertRaises(OrionisTestValueError):
            ValidNamePattern({"pattern": "test"})

    def testValidPattern(self) -> None:
        """
        Test the ValidPattern validator for pattern string validation.

        Validates that ValidPattern accepts valid non-empty string patterns and returns
        the normalized string value. Ensures that empty strings, None, or non-string types
        raise OrionisTestValueError.

        Returns
        -------
        None
        """
        # Valid cases: should return the normalized string for a valid pattern
        self.assertEqual(ValidPattern("abc"), "abc")
        self.assertEqual(ValidPattern("  test_pattern  "), "test_pattern")
        self.assertEqual(ValidPattern("*complex?pattern[0-9]"), "*complex?pattern[0-9]")

        # Invalid cases: should raise OrionisTestValueError for empty string, None, or non-string type
        with self.assertRaises(OrionisTestValueError):
            ValidPattern("")
        with self.assertRaises(OrionisTestValueError):
            ValidPattern("   ")
        with self.assertRaises(OrionisTestValueError):
            ValidPattern(None)
        with self.assertRaises(OrionisTestValueError):
            ValidPattern(123)
        with self.assertRaises(OrionisTestValueError):
            ValidPattern([])
        with self.assertRaises(OrionisTestValueError):
            ValidPattern({"pattern": "abc"})

    def testValidPersistentDriver(self) -> None:
        """
        Test the ValidPersistentDriver validator for persistent driver validation.

        Checks that ValidPersistentDriver accepts valid persistent driver names as strings
        and enum values, returning the normalized string value. Ensures that unknown driver
        names or non-enum types raise OrionisTestValueError.

        Returns
        -------
        None
        """
        # Valid cases: should return the normalized string for valid driver name or enum input
        self.assertEqual(ValidPersistentDriver("sqlite"), "sqlite")
        self.assertEqual(ValidPersistentDriver(PersistentDrivers.SQLITE), "sqlite")

        # Test all available drivers from enum
        for driver in PersistentDrivers:
            self.assertEqual(ValidPersistentDriver(driver), driver.value)
            self.assertEqual(ValidPersistentDriver(driver.value), driver.value)

        # Invalid cases: should raise OrionisTestValueError for unknown driver name or non-enum type
        with self.assertRaises(OrionisTestValueError):
            ValidPersistentDriver("invalid")
        with self.assertRaises(OrionisTestValueError):
            ValidPersistentDriver("SQLITE")  # Case sensitive
        with self.assertRaises(OrionisTestValueError):
            ValidPersistentDriver("")
        with self.assertRaises(OrionisTestValueError):
            ValidPersistentDriver(None)
        with self.assertRaises(OrionisTestValueError):
            ValidPersistentDriver(123)
        with self.assertRaises(OrionisTestValueError):
            ValidPersistentDriver([])
        with self.assertRaises(OrionisTestValueError):
            ValidPersistentDriver({"driver": "sqlite"})

    def testValidPersistent(self) -> None:
        """
        Test the ValidPersistent validator for persistent configuration validation.

        Validates that ValidPersistent accepts valid boolean inputs and returns the corresponding
        boolean value. Raises OrionisTestValueError for non-boolean types or None.

        Returns
        -------
        None
        """
        # Valid cases: should return True or False for boolean input
        self.assertTrue(ValidPersistent(True))
        self.assertFalse(ValidPersistent(False))

        # Invalid cases: should raise OrionisTestValueError for non-boolean or None input
        with self.assertRaises(OrionisTestValueError):
            ValidPersistent("not_bool")
        with self.assertRaises(OrionisTestValueError):
            ValidPersistent("false")  # String representation of boolean
        with self.assertRaises(OrionisTestValueError):
            ValidPersistent(1)  # Integer that could be truthy
        with self.assertRaises(OrionisTestValueError):
            ValidPersistent(0)  # Integer that could be falsy
        with self.assertRaises(OrionisTestValueError):
            ValidPersistent(None)
        with self.assertRaises(OrionisTestValueError):
            ValidPersistent([])
        with self.assertRaises(OrionisTestValueError):
            ValidPersistent({})

    def testValidPrintResult(self) -> None:
        """
        Test the ValidPrintResult validator for print result configuration validation.

        Ensures that ValidPrintResult accepts valid boolean inputs and returns the corresponding
        boolean value. Raises OrionisTestValueError for non-boolean types or None.

        Returns
        -------
        None
        """
        # Valid cases: should return True or False for boolean input
        self.assertTrue(ValidPrintResult(True))
        self.assertFalse(ValidPrintResult(False))

        # Invalid cases: should raise OrionisTestValueError for non-boolean or None input
        with self.assertRaises(OrionisTestValueError):
            ValidPrintResult("not_bool")
        with self.assertRaises(OrionisTestValueError):
            ValidPrintResult("True")  # String representation of boolean
        with self.assertRaises(OrionisTestValueError):
            ValidPrintResult(1)  # Integer that could be truthy
        with self.assertRaises(OrionisTestValueError):
            ValidPrintResult(0)  # Integer that could be falsy
        with self.assertRaises(OrionisTestValueError):
            ValidPrintResult(None)
        with self.assertRaises(OrionisTestValueError):
            ValidPrintResult([])
        with self.assertRaises(OrionisTestValueError):
            ValidPrintResult({})

    def testValidTags(self) -> None:
        """
        Test the ValidTags validator for tag list validation.

        Validates that ValidTags accepts a list of non-empty string tags, normalizes whitespace,
        and returns a list of cleaned tag strings. Accepts None and returns None. Raises
        OrionisTestValueError for empty lists, lists with empty strings or non-string types,
        and non-list inputs.

        Returns
        -------
        None
        """
        # Valid cases: should return a list of normalized tag strings or None
        self.assertEqual(ValidTags(["a", "b ", " c"]), ["a", "b", "c"])
        self.assertEqual(ValidTags(["tag1", "tag2", "tag3"]), ["tag1", "tag2", "tag3"])
        self.assertEqual(ValidTags(["  multi  ", "  word  ", "  tags  "]), ["multi", "word", "tags"])
        self.assertIsNone(ValidTags(None))

        # Invalid cases: should raise OrionisTestValueError for various invalid inputs
        with self.assertRaises(OrionisTestValueError):
            ValidTags([])  # Empty list
        with self.assertRaises(OrionisTestValueError):
            ValidTags([""])  # List containing empty string
        with self.assertRaises(OrionisTestValueError):
            ValidTags(["   "])  # List containing whitespace-only string
        with self.assertRaises(OrionisTestValueError):
            ValidTags([123])  # List containing non-string type
        with self.assertRaises(OrionisTestValueError):
            ValidTags(["valid", 123])  # Mixed valid and invalid types
        with self.assertRaises(OrionisTestValueError):
            ValidTags(["valid", ""])  # Mixed valid and empty string
        with self.assertRaises(OrionisTestValueError):
            ValidTags("not_a_list")  # Non-list input
        with self.assertRaises(OrionisTestValueError):
            ValidTags(123)  # Non-list input
        with self.assertRaises(OrionisTestValueError):
            ValidTags({"tags": ["a", "b"]})  # Dictionary input

    def testValidThrowException(self) -> None:
        """
        Test the ValidThrowException validator for throw exception configuration validation.

        Ensures that ValidThrowException accepts valid boolean inputs and returns the corresponding
        boolean value. Raises OrionisTestValueError for non-boolean types or None.

        Returns
        -------
        None
        """
        # Valid cases: should return True or False for boolean input
        self.assertTrue(ValidThrowException(True))
        self.assertFalse(ValidThrowException(False))

        # Invalid cases: should raise OrionisTestValueError for non-boolean or None input
        with self.assertRaises(OrionisTestValueError):
            ValidThrowException("not_bool")
        with self.assertRaises(OrionisTestValueError):
            ValidThrowException("false")  # String representation of boolean
        with self.assertRaises(OrionisTestValueError):
            ValidThrowException(1)  # Integer that could be truthy
        with self.assertRaises(OrionisTestValueError):
            ValidThrowException(0)  # Integer that could be falsy
        with self.assertRaises(OrionisTestValueError):
            ValidThrowException(None)
        with self.assertRaises(OrionisTestValueError):
            ValidThrowException([])
        with self.assertRaises(OrionisTestValueError):
            ValidThrowException({})

    def testValidVerbosity(self) -> None:
        """
        Test the ValidVerbosity validator for verbosity mode validation.

        Validates that ValidVerbosity accepts valid verbosity mode enum values and their corresponding
        integer values, returning the normalized integer value. Ensures that negative values, unknown
        integers, or non-integer types raise OrionisTestValueError.

        Returns
        -------
        None
        """
        # Valid cases: should return the integer value for valid enum or integer input
        self.assertEqual(ValidVerbosity(VerbosityMode.MINIMAL), VerbosityMode.MINIMAL.value)
        self.assertEqual(ValidVerbosity(VerbosityMode.DETAILED.value), VerbosityMode.DETAILED.value)

        # Test all available verbosity modes from enum
        for mode in VerbosityMode:
            self.assertEqual(ValidVerbosity(mode), mode.value)
            self.assertEqual(ValidVerbosity(mode.value), mode.value)

        # Valid edge case: should accept zero if it's a valid VerbosityMode value
        if 0 in [mode.value for mode in VerbosityMode]:
            self.assertEqual(ValidVerbosity(0), 0)

        # Invalid cases: should raise OrionisTestValueError for negative, unknown, or non-integer input
        with self.assertRaises(OrionisTestValueError):
            ValidVerbosity(-1)
        with self.assertRaises(OrionisTestValueError):
            ValidVerbosity("not_int")
        with self.assertRaises(OrionisTestValueError):
            ValidVerbosity(999)  # Unknown verbosity level
        with self.assertRaises(OrionisTestValueError):
            ValidVerbosity(3.14)  # Float value
        with self.assertRaises(OrionisTestValueError):
            ValidVerbosity(None)
        with self.assertRaises(OrionisTestValueError):
            ValidVerbosity([])
        with self.assertRaises(OrionisTestValueError):
            ValidVerbosity({"verbosity": 1})

    def testValidWebReport(self) -> None:
        """
        Test the ValidWebReport validator for web report configuration validation.

        Ensures that ValidWebReport accepts valid boolean inputs and returns the corresponding
        boolean value. Raises OrionisTestValueError for non-boolean types or None.

        Returns
        -------
        None
        """
        # Valid cases: should return True or False for boolean input
        self.assertTrue(ValidWebReport(True))
        self.assertFalse(ValidWebReport(False))

        # Invalid cases: should raise OrionisTestValueError for non-boolean or None input
        with self.assertRaises(OrionisTestValueError):
            ValidWebReport("not_bool")
        with self.assertRaises(OrionisTestValueError):
            ValidWebReport("true")  # String representation of boolean
        with self.assertRaises(OrionisTestValueError):
            ValidWebReport(1)  # Integer that could be truthy
        with self.assertRaises(OrionisTestValueError):
            ValidWebReport(0)  # Integer that could be falsy
        with self.assertRaises(OrionisTestValueError):
            ValidWebReport(None)
        with self.assertRaises(OrionisTestValueError):
            ValidWebReport([])
        with self.assertRaises(OrionisTestValueError):
            ValidWebReport({})
