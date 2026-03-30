import os
import shutil
import tempfile
from orionis.test import TestCase
from orionis.services.environment.core.dot_env import DotEnv
from orionis.services.environment.enums import EnvironmentValueType
from orionis.support.patterns.singleton import Singleton

# ---------------------------------------------------------------------------
# Shared base — singleton reset + temp-file lifecycle
# ---------------------------------------------------------------------------


class _DotEnvBase(TestCase):
    """
    Base class that resets the DotEnv singleton and manages a temp .env file.

    Each subclass gets an isolated DotEnv instance backed by a fresh
    temporary file; os.environ keys created during the test are cleaned
    up automatically in tearDown.
    """

    def setUp(self) -> None:
        """
        Reset the singleton and create a temporary .env file for the test.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # Clear any cached singleton so each test starts fresh
        Singleton._instances.pop(DotEnv, None)
        # Temporary directory + path used as the .env backing file
        self._tmpdir: str = tempfile.mkdtemp()
        self._env_path: str = os.path.join(self._tmpdir, ".test_env")
        self._dot_env: DotEnv = DotEnv(path=self._env_path)
        # Keys registered here are removed from os.environ in tearDown
        self._tracked_keys: list[str] = []

    def tearDown(self) -> None:
        """
        Clean up os.environ keys, temp files, and the singleton.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # Remove every key that was set during the test
        for key in self._tracked_keys:
            os.environ.pop(key, None)
        shutil.rmtree(self._tmpdir, ignore_errors=True)
        # Always reset the singleton so tests cannot bleed state
        Singleton._instances.pop(DotEnv, None)

    def _track(self, key: str) -> str:
        """
        Register a key for automatic os.environ cleanup in tearDown.

        Parameters
        ----------
        key : str
            Environment variable name to track.

        Returns
        -------
        str
            The same key, for convenient inline use.
        """
        if key not in self._tracked_keys:
            self._tracked_keys.append(key)
        return key


# ---------------------------------------------------------------------------
# TestDotEnvInit
# ---------------------------------------------------------------------------


class TestDotEnvInit(TestCase):
    """
    Verify DotEnv initialisation with various path configurations.

    Methods
    -------
    setUp
    tearDown
    testCustomPathCreatesFile
    testCustomPathFileExistsAfterInit
    testDefaultPathIsCwd
    testExistingFileIsNotOverwritten
    testSingletonReturnsSameInstance
    """

    def setUp(self) -> None:
        """
        Reset the singleton and create a temp directory for path tests.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        Singleton._instances.pop(DotEnv, None)
        self._tmpdir: str = tempfile.mkdtemp()
        self._env_path: str = os.path.join(self._tmpdir, ".test_env")

    def tearDown(self) -> None:
        """
        Clean up the temp directory and singleton after each test.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        Singleton._instances.pop(DotEnv, None)
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def testCustomPathCreatesFile(self) -> None:
        """
        Assert that DotEnv creates the .env file when it does not exist.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # The temp file path does not exist yet
        self.assertFalse(os.path.exists(self._env_path))
        DotEnv(path=self._env_path)
        # After init the file must exist on disk
        self.assertTrue(os.path.exists(self._env_path))

    def testCustomPathFileExistsAfterInit(self) -> None:
        """
        Assert that the resolved path is accessible after initialisation.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        DotEnv(path=self._env_path)
        self.assertTrue(os.path.isfile(self._env_path))

    def testExistingFileIsNotOverwritten(self) -> None:
        """
        Assert that pre-existing .env content is preserved on re-init.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # Write a sentinel line before DotEnv is created
        with open(self._env_path, "w") as fh:
            fh.write("SENTINEL=1\n")
        DotEnv(path=self._env_path)
        with open(self._env_path) as fh:
            content = fh.read()
        self.assertIn("SENTINEL", content)

    def testSingletonReturnsSameInstance(self) -> None:
        """
        Assert that two DotEnv calls return the identical singleton object.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        a = DotEnv(path=self._env_path)
        b = DotEnv(path=self._env_path)
        self.assertIs(a, b)


# ---------------------------------------------------------------------------
# TestDotEnvSet
# ---------------------------------------------------------------------------


class TestDotEnvSet(_DotEnvBase):
    """
    Verify the set() method across value types, options, and error cases.

    Methods
    -------
    testSetReturnsTrueForString
    testSetStringValueIsRetrievable
    testSetIntValueIsRetrievable
    testSetFloatValueIsRetrievable
    testSetBoolTrueIsRetrievable
    testSetBoolFalseIsRetrievable
    testSetListValueIsRetrievable
    testSetDictValueIsRetrievable
    testSetWithTypeHintInt
    testSetOnlyOsDoesNotWriteToFile
    testSetOnlyOsIsReadableFromOsEnviron
    testSetInvalidKeyLowercaseRaisesValueError
    testSetInvalidKeyStartsWithDigitRaisesValueError
    testSetNonStringKeyRaisesTypeError
    """

    def testSetReturnsTrueForString(self) -> None:
        """
        Assert that set() returns True after a successful string assignment.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_RETVAL")
        result = self._dot_env.set(key, "hello")
        self.assertTrue(result)

    def testSetStringValueIsRetrievable(self) -> None:
        """
        Assert that a string value stored via set() is returned by get().

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_STR")
        self._dot_env.set(key, "world")
        self.assertEqual(self._dot_env.get(key), "world")

    def testSetIntValueIsRetrievable(self) -> None:
        """
        Assert that an integer value stored via set() is parsed back as int.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_INT")
        self._dot_env.set(key, 42)
        self.assertEqual(self._dot_env.get(key), 42)

    def testSetFloatValueIsRetrievable(self) -> None:
        """
        Assert that a float value stored via set() is parsed back as float.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_FLOAT")
        self._dot_env.set(key, 3.14)
        self.assertAlmostEqual(self._dot_env.get(key), 3.14, places=5)

    def testSetBoolTrueIsRetrievable(self) -> None:
        """
        Assert that boolean True is serialized and parsed back correctly.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_BOOL_T")
        self._dot_env.set(key, True)
        self.assertIs(self._dot_env.get(key), True)

    def testSetBoolFalseIsRetrievable(self) -> None:
        """
        Assert that boolean False is serialized and parsed back correctly.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_BOOL_F")
        self._dot_env.set(key, False)
        self.assertIs(self._dot_env.get(key), False)

    def testSetListValueIsRetrievable(self) -> None:
        """
        Assert that a list value stored via set() is parsed back as a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_LIST")
        self._dot_env.set(key, [1, 2, 3])
        self.assertEqual(self._dot_env.get(key), [1, 2, 3])

    def testSetDictValueIsRetrievable(self) -> None:
        """
        Assert that a dict value stored via set() is parsed back as a dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_DICT")
        self._dot_env.set(key, {"a": 1, "b": 2})
        self.assertEqual(self._dot_env.get(key), {"a": 1, "b": 2})

    def testSetWithTypeHintInt(self) -> None:
        """
        Assert that set() with EnvironmentValueType.INT stores an int string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_HINT")
        # Passing a string "7" with INT hint should cast to integer 7
        self._dot_env.set(key, "7", type_hint=EnvironmentValueType.INT)
        result = self._dot_env.get(key)
        self.assertEqual(result, 7)

    def testSetOnlyOsDoesNotWriteToFile(self) -> None:
        """
        Assert that only_os=True skips writing to the .env file.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_ONLY_OS")
        self._dot_env.set(key, "inmemory", only_os=True)
        # Reading directly from the .env file must not contain the key
        with open(self._env_path) as fh:
            content = fh.read()
        self.assertNotIn(key, content)

    def testSetOnlyOsIsReadableFromOsEnviron(self) -> None:
        """
        Assert that only_os=True still sets the variable in os.environ.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SET_OS_READ")
        self._dot_env.set(key, "present", only_os=True)
        self.assertEqual(os.environ.get(key), "present")

    def testSetInvalidKeyLowercaseRaisesValueError(self) -> None:
        """
        Assert that set() raises ValueError for a lowercase key name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(ValueError):
            self._dot_env.set("invalid_key", "value")

    def testSetInvalidKeyStartsWithDigitRaisesValueError(self) -> None:
        """
        Assert that set() raises ValueError when the key starts with a digit.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(ValueError):
            self._dot_env.set("1INVALID", "value")

    def testSetNonStringKeyRaisesTypeError(self) -> None:
        """
        Assert that set() raises TypeError when the key is not a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            self._dot_env.set(123, "value")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# TestDotEnvGet
# ---------------------------------------------------------------------------


class TestDotEnvGet(_DotEnvBase):
    """
    Verify the get() method for present, absent, and typed values.

    Methods
    -------
    testGetExistingKeyReturnsValue
    testGetMissingKeyReturnsNoneByDefault
    testGetMissingKeyReturnsCustomDefault
    testGetBoolTrueString
    testGetBoolFalseString
    testGetNullStringReturnsNone
    testGetNoneStringReturnsNone
    testGetIntLiteral
    testGetFloatLiteral
    testGetInvalidKeyRaises
    """

    def testGetExistingKeyReturnsValue(self) -> None:
        """
        Assert that get() returns the stored value for an existing key.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_GET_EXIST")
        self._dot_env.set(key, "found")
        self.assertEqual(self._dot_env.get(key), "found")

    def testGetMissingKeyReturnsNoneByDefault(self) -> None:
        """
        Assert that get() returns None when the key is absent and no default.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self._dot_env.get("TEST_GET_MISSING_XYZ")
        self.assertIsNone(result)

    def testGetMissingKeyReturnsCustomDefault(self) -> None:
        """
        Assert that get() returns the provided default for a missing key.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self._dot_env.get("TEST_GET_NODEFAULT_XYZ", default="fallback")
        self.assertEqual(result, "fallback")

    def testGetBoolTrueString(self) -> None:
        """
        Assert that the string 'true' is parsed as boolean True.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_GET_BOOL_T")
        self._dot_env.set(key, "true")
        self.assertIs(self._dot_env.get(key), True)

    def testGetBoolFalseString(self) -> None:
        """
        Assert that the string 'false' is parsed as boolean False.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_GET_BOOL_F")
        self._dot_env.set(key, "false")
        self.assertIs(self._dot_env.get(key), False)

    def testGetNullStringReturnsNone(self) -> None:
        """
        Assert that the string 'null' stored in the file is parsed as None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_GET_NULL")
        # Write directly to the file to simulate a raw null value
        with open(self._env_path, "a") as fh:
            fh.write(f"{key}=null\n")
        self.assertIsNone(self._dot_env.get(key))

    def testGetNoneStringReturnsNone(self) -> None:
        """
        Assert that the string 'none' stored in the file is parsed as None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_GET_NONE_STR")
        with open(self._env_path, "a") as fh:
            fh.write(f"{key}=none\n")
        self.assertIsNone(self._dot_env.get(key))

    def testGetIntLiteral(self) -> None:
        """
        Assert that an integer literal in the file is returned as int.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_GET_INT_LIT")
        with open(self._env_path, "a") as fh:
            fh.write(f"{key}=99\n")
        self.assertEqual(self._dot_env.get(key), 99)

    def testGetFloatLiteral(self) -> None:
        """
        Assert that a float literal in the file is returned as float.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_GET_FLOAT_LIT")
        with open(self._env_path, "a") as fh:
            fh.write(f"{key}=2.71\n")
        result = self._dot_env.get(key)
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, 2.71, places=5)

    def testGetInvalidKeyRaises(self) -> None:
        """
        Assert that get() raises an error for an invalid key name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises((ValueError, TypeError)):
            self._dot_env.get("invalid-key")


# ---------------------------------------------------------------------------
# TestDotEnvUnset
# ---------------------------------------------------------------------------


class TestDotEnvUnset(_DotEnvBase):
    """
    Verify the unset() method removes keys from file and/or process env.

    Methods
    -------
    testUnsetReturnsTrueForExistingKey
    testUnsetRemovesKeyFromFile
    testUnsetRemovesKeyFromOsEnviron
    testUnsetOnlyOsKeepsKeyInFile
    testUnsetNonExistingKeyReturnsTrue
    testUnsetInvalidKeyRaises
    """

    def testUnsetReturnsTrueForExistingKey(self) -> None:
        """
        Assert that unset() returns True when the key existed.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_UNSET_RET")
        self._dot_env.set(key, "bye")
        result = self._dot_env.unset(key)
        self.assertTrue(result)

    def testUnsetRemovesKeyFromFile(self) -> None:
        """
        Assert that unset() removes the key from the .env file.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_UNSET_FILE")
        self._dot_env.set(key, "written")
        self._dot_env.unset(key)
        # The key must not appear in the file contents any more
        with open(self._env_path) as fh:
            content = fh.read()
        self.assertNotIn(key, content)

    def testUnsetRemovesKeyFromOsEnviron(self) -> None:
        """
        Assert that unset() removes the key from os.environ.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_UNSET_ENV")
        self._dot_env.set(key, "alive")
        self.assertIn(key, os.environ)
        self._dot_env.unset(key)
        self.assertNotIn(key, os.environ)

    def testUnsetOnlyOsKeepsKeyInFile(self) -> None:
        """
        Assert that only_os=True leaves the key in the .env file.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_UNSET_ONLYOS")
        self._dot_env.set(key, "stays_in_file")
        self._dot_env.unset(key, only_os=True)
        with open(self._env_path) as fh:
            content = fh.read()
        self.assertIn(key, content)

    def testUnsetNonExistingKeyReturnsTrue(self) -> None:
        """
        Assert that unset() returns True even when the key does not exist.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self._dot_env.unset("TEST_UNSET_GHOST_XYZ")
        self.assertTrue(result)

    def testUnsetInvalidKeyRaises(self) -> None:
        """
        Assert that unset() raises an error for an invalid key name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises((ValueError, TypeError)):
            self._dot_env.unset("bad-key")


# ---------------------------------------------------------------------------
# TestDotEnvAll
# ---------------------------------------------------------------------------


class TestDotEnvAll(_DotEnvBase):
    """
    Verify the all() method returns the correct dictionary of .env values.

    Methods
    -------
    testAllReturnsDictType
    testAllContainsSetKey
    testAllExcludesUnsetKey
    testAllEmptyFileReturnsEmptyDict
    testAllParsesValuesCorrectly
    """

    def testAllReturnsDictType(self) -> None:
        """
        Assert that all() returns a dict instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self._dot_env.all(), dict)

    def testAllContainsSetKey(self) -> None:
        """
        Assert that all() includes a key that was previously set.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_ALL_PRESENT")
        self._dot_env.set(key, "here")
        self.assertIn(key, self._dot_env.all())

    def testAllExcludesUnsetKey(self) -> None:
        """
        Assert that all() excludes a key that was unset.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_ALL_ABSENT")
        self._dot_env.set(key, "temp")
        self._dot_env.unset(key)
        self.assertNotIn(key, self._dot_env.all())

    def testAllEmptyFileReturnsEmptyDict(self) -> None:
        """
        Assert that all() returns an empty dict for a blank .env file.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # The file was created empty in setUp — no keys have been set
        self.assertEqual(self._dot_env.all(), {})

    def testAllParsesValuesCorrectly(self) -> None:
        """
        Assert that all() parses the stored values to their Python types.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_ALL_PARSED")
        self._dot_env.set(key, 7)
        result = self._dot_env.all()
        self.assertEqual(result[key], 7)


# ---------------------------------------------------------------------------
# TestDotEnvReload
# ---------------------------------------------------------------------------


class TestDotEnvReload(_DotEnvBase):
    """
    Verify that reload() re-reads the .env file into the process environment.

    Methods
    -------
    testReloadReturnsTrue
    testReloadPicksUpExternallyAddedKey
    testReloadOverridesExistingOsValue
    """

    def testReloadReturnsTrue(self) -> None:
        """
        Assert that reload() returns True on success.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(self._dot_env.reload())

    def testReloadPicksUpExternallyAddedKey(self) -> None:
        """
        Assert that reload() loads a key written externally to the .env file.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_RELOAD_EXT")
        # Write the key directly to disk, bypassing DotEnv.set()
        with open(self._env_path, "a") as fh:
            fh.write(f"{key}=external\n")
        self._dot_env.reload()
        # The key should now be accessible in os.environ
        self.assertEqual(os.environ.get(key), "external")

    def testReloadOverridesExistingOsValue(self) -> None:
        """
        Assert that reload() overrides os.environ with the file's value.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_RELOAD_OVERRIDE")
        # Store the original value via DotEnv
        self._dot_env.set(key, "original")
        # Tamper with os.environ directly
        os.environ[key] = "tampered"
        self._dot_env.reload()
        # Reload must restore the file's value
        self.assertEqual(os.environ.get(key), "original")


# ---------------------------------------------------------------------------
# TestDotEnvSerializeValue (exercised indirectly via set + get)
# ---------------------------------------------------------------------------


class TestDotEnvSerializeValue(_DotEnvBase):
    """
    Verify the private __serializeValue behaviour through set() and get().

    Methods
    -------
    testSerializeNoneStoresNull
    testSerializeTrueStoresTrue
    testSerializeFalseStoresFalse
    testSerializeIntRoundTrips
    testSerializeFloatRoundTrips
    testSerializeListRoundTrips
    testSerializeTupleRoundTrips
    testSerializeSetRoundTrips
    testSerializeStringStrip
    """

    def testSerializeNoneStoresNull(self) -> None:
        """
        Assert that None is serialized as the string 'null' in the file.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SER_NULL")
        self._dot_env.set(key, None)  # type: ignore[arg-type]
        with open(self._env_path) as fh:
            content = fh.read()
        self.assertIn("null", content)

    def testSerializeTrueStoresTrue(self) -> None:
        """
        Assert that True is serialized as the string 'true' in the file.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SER_T")
        self._dot_env.set(key, True)
        with open(self._env_path) as fh:
            content = fh.read()
        self.assertIn("true", content)

    def testSerializeFalseStoresFalse(self) -> None:
        """
        Assert that False is serialized as the string 'false' in the file.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SER_F")
        self._dot_env.set(key, False)
        with open(self._env_path) as fh:
            content = fh.read()
        self.assertIn("false", content)

    def testSerializeIntRoundTrips(self) -> None:
        """
        Assert that an integer set via set() round-trips as int through get().

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SER_INT_RT")
        self._dot_env.set(key, 100)
        self.assertEqual(self._dot_env.get(key), 100)

    def testSerializeFloatRoundTrips(self) -> None:
        """
        Assert that a float set via set() round-trips as float through get().

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SER_FLOAT_RT")
        self._dot_env.set(key, 1.5)
        self.assertAlmostEqual(self._dot_env.get(key), 1.5, places=5)

    def testSerializeListRoundTrips(self) -> None:
        """
        Assert that a list set via set() round-trips as list through get().

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SER_LIST_RT")
        self._dot_env.set(key, [10, 20])
        self.assertEqual(self._dot_env.get(key), [10, 20])

    def testSerializeTupleRoundTrips(self) -> None:
        """
        Assert that a tuple set via set() round-trips as tuple through get().

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SER_TUPLE_RT")
        self._dot_env.set(key, (1, 2))
        self.assertEqual(self._dot_env.get(key), (1, 2))

    def testSerializeSetRoundTrips(self) -> None:
        """
        Assert that a set value stored via set() returns a set through get().

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SER_SET_RT")
        self._dot_env.set(key, {7, 8})
        result = self._dot_env.get(key)
        self.assertIsInstance(result, set)

    def testSerializeStringStrip(self) -> None:
        """
        Assert that a string with surrounding whitespace is stripped on store.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        key = self._track("TEST_SER_STRIP")
        self._dot_env.set(key, "  trimmed  ")
        self.assertEqual(self._dot_env.get(key), "trimmed")


# ---------------------------------------------------------------------------
# TestDotEnvParseValue (exercised indirectly via get)
# ---------------------------------------------------------------------------


class TestDotEnvParseValue(_DotEnvBase):
    """
    Verify the private __parseValue behaviour through direct file writes + get().

    Methods
    -------
    testParseNullStringReturnsNone
    testParseNoneStringReturnsNone
    testParseNanStringReturnsNone
    testParseNilStringReturnsNone
    testParseBoolTrueString
    testParseBoolFalseString
    testParseIntString
    testParseFloatString
    testParseListString
    testParseDictString
    testParseEmptyStringReturnsNone
    testParseUnknownStringReturnedAsIs
    """

    def _write(self, key: str, raw: str) -> None:
        """
        Write a raw key=value line directly to the .env file.

        Parameters
        ----------
        key : str
            Environment variable name.
        raw : str
            Raw string value to write (not quoted).

        Returns
        -------
        None
        """
        self._track(key)
        with open(self._env_path, "a") as fh:
            fh.write(f"{key}={raw}\n")

    def testParseNullStringReturnsNone(self) -> None:
        """
        Assert that the raw token 'null' is parsed to None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_NULL", "null")
        self.assertIsNone(self._dot_env.get("TEST_PARSE_NULL"))

    def testParseNoneStringReturnsNone(self) -> None:
        """
        Assert that the raw token 'none' is parsed to None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_NONE", "none")
        self.assertIsNone(self._dot_env.get("TEST_PARSE_NONE"))

    def testParseNanStringReturnsNone(self) -> None:
        """
        Assert that the raw token 'nan' is parsed to None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_NAN", "nan")
        self.assertIsNone(self._dot_env.get("TEST_PARSE_NAN"))

    def testParseNilStringReturnsNone(self) -> None:
        """
        Assert that the raw token 'nil' is parsed to None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_NIL", "nil")
        self.assertIsNone(self._dot_env.get("TEST_PARSE_NIL"))

    def testParseBoolTrueString(self) -> None:
        """
        Assert that the raw token 'true' is parsed to boolean True.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_BOOL_T", "true")
        self.assertIs(self._dot_env.get("TEST_PARSE_BOOL_T"), True)

    def testParseBoolFalseString(self) -> None:
        """
        Assert that the raw token 'false' is parsed to boolean False.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_BOOL_F", "false")
        self.assertIs(self._dot_env.get("TEST_PARSE_BOOL_F"), False)

    def testParseIntString(self) -> None:
        """
        Assert that a raw integer string is parsed to int.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_INT", "55")
        self.assertEqual(self._dot_env.get("TEST_PARSE_INT"), 55)

    def testParseFloatString(self) -> None:
        """
        Assert that a raw float string is parsed to float.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_FLOAT", "9.81")
        result = self._dot_env.get("TEST_PARSE_FLOAT")
        self.assertAlmostEqual(result, 9.81, places=5)

    def testParseListString(self) -> None:
        """
        Assert that a raw Python list literal is parsed to a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_LIST", "[1, 2, 3]")
        self.assertEqual(self._dot_env.get("TEST_PARSE_LIST"), [1, 2, 3])

    def testParseDictString(self) -> None:
        """
        Assert that a raw Python dict literal is parsed to a dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_DICT", "{'x': 10}")
        self.assertEqual(self._dot_env.get("TEST_PARSE_DICT"), {"x": 10})

    def testParseEmptyStringReturnsNone(self) -> None:
        """
        Assert that an empty value in the file is parsed as None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_EMPTY", "")
        self.assertIsNone(self._dot_env.get("TEST_PARSE_EMPTY"))

    def testParseUnknownStringReturnedAsIs(self) -> None:
        """
        Assert that an unrecognised raw string is returned unchanged.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._write("TEST_PARSE_ASIS", "some_opaque_value")
        result = self._dot_env.get("TEST_PARSE_ASIS")
        self.assertEqual(result, "some_opaque_value")
