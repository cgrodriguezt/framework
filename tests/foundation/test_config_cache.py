from orionis.test import TestCase
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.cache.entities.file import File
from orionis.foundation.config.cache.entities.stores import Stores
from orionis.foundation.config.cache.enums.drivers import Drivers

# ===========================================================================
# Drivers enum
# ===========================================================================

class TestDriversEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that FILE, MEMCACHED and REDIS members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("FILE", Drivers._member_names_)
        self.assertIn("MEMCACHED", Drivers._member_names_)
        self.assertIn("REDIS", Drivers._member_names_)

    def testMemberValues(self) -> None:
        """
        Test the string values assigned to each Drivers member.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Drivers.FILE.value, "file")
        self.assertEqual(Drivers.MEMCACHED.value, "memcached")
        self.assertEqual(Drivers.REDIS.value, "redis")

    def testLookupByName(self) -> None:
        """
        Test that Drivers members can be retrieved by their name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Drivers["FILE"], Drivers.FILE)

    def testLookupByValue(self) -> None:
        """
        Test that Drivers members can be retrieved by their string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Drivers("redis"), Drivers.REDIS)

    def testUnknownValueRaises(self) -> None:
        """
        Test that looking up an unknown driver value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Drivers("sqlite")

    def testMemberCount(self) -> None:
        """
        Test that exactly three Drivers members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(Drivers), 3)

    def testIsHashable(self) -> None:
        """
        Test that Drivers members are hashable and usable as dict keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        mapping = {Drivers.FILE: "file_driver"}
        self.assertEqual(mapping[Drivers.FILE], "file_driver")

# ===========================================================================
# File entity
# ===========================================================================

class TestFileEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that File can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        f = File()
        self.assertIsInstance(f, File)

    def testDefaultPath(self) -> None:
        """
        Test that the default path is set to the expected value.

        Returns
        -------
        None
            This method does not return a value.
        """
        f = File()
        self.assertEqual(f.path, "storage/framework/cache/data")

    def testCustomPath(self) -> None:
        """
        Test that a custom path is stored correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        f = File(path="storage/custom/cache")
        self.assertEqual(f.path, "storage/custom/cache")

    def testEmptyPathRaisesValueError(self) -> None:
        """
        Test that an empty path string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            File(path="")

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen File instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        f = File()
        with self.assertRaises(FrozenInstanceError):
            f.path = "other"  # type: ignore[misc]


# ===========================================================================
# Stores entity
# ===========================================================================

class TestStoresEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Stores can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Stores()
        self.assertIsInstance(s, Stores)

    def testDefaultFileIsFileInstance(self) -> None:
        """
        Test that the default file attribute is a File instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Stores()
        self.assertIsInstance(s.file, File)

    def testDictConversion(self) -> None:
        """
        Test that a dict for file is converted to a File instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Stores(file={"path": "storage/custom"})
        self.assertIsInstance(s.file, File)
        self.assertEqual(s.file.path, "storage/custom")

    def testInvalidFileTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for file raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Stores(file="not_a_file")  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Stores instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        s = Stores()
        with self.assertRaises(FrozenInstanceError):
            s.file = File()  # type: ignore[misc]


# ===========================================================================
# Cache entity
# ===========================================================================

class TestCacheEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Cache can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Cache()
        self.assertIsInstance(c, Cache)

    def testDefaultDriverIsNormalized(self) -> None:
        """
        Test that the default cache driver is a valid Drivers value string.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Cache()
        self.assertIn(c.default, [d.value for d in Drivers])

    def testDefaultStoresIsStoresInstance(self) -> None:
        """
        Test that the default stores attribute is a Stores instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Cache()
        self.assertIsInstance(c.stores, Stores)

    def testDriverStringNormalization(self) -> None:
        """
        Test that a lowercase driver string is normalized to a Drivers value.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Cache(default="file")
        self.assertEqual(c.default, Drivers.FILE.value)

    def testDriverStringUpperCase(self) -> None:
        """
        Test that an uppercase driver string is accepted and normalized.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Cache(default="FILE")
        self.assertEqual(c.default, Drivers.FILE.value)

    def testDriverEnumNormalization(self) -> None:
        """
        Test that passing a Drivers enum is stored as its string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Cache(default=Drivers.REDIS)
        self.assertEqual(c.default, Drivers.REDIS.value)

    def testStoresDictConversion(self) -> None:
        """
        Test that a dict for stores is converted to a Stores instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Cache(stores={"file": {"path": "storage/custom"}})
        self.assertIsInstance(c.stores, Stores)

    def testInvalidDriverRaisesValueError(self) -> None:
        """
        Test that an unrecognized driver string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Cache(default="unknown_driver")

    def testInvalidDriverTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string, non-Drivers default raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cache(default=123)  # type: ignore[arg-type]

    def testInvalidStoresTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for stores raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cache(stores="invalid")  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Cache instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        c = Cache()
        with self.assertRaises(FrozenInstanceError):
            c.default = "redis"  # type: ignore[misc]
