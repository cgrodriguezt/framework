from pathlib import Path
import shutil

from orionis.test import TestCase
from orionis.foundation.config.filesystems.entitites.aws import S3
from orionis.foundation.config.filesystems.entitites.local import Local
from orionis.foundation.config.filesystems.entitites.public import Public
from orionis.foundation.config.filesystems.entitites.disks import Disks
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems

# ===========================================================================
# S3 entity
# ===========================================================================

class TestS3Entity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that S3 can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        s3 = S3()
        self.assertIsInstance(s3, S3)

    def testDefaultFieldValues(self) -> None:
        """
        Test that S3 default field values are set correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        s3 = S3()
        self.assertEqual(s3.key, "")
        self.assertEqual(s3.secret, "")
        self.assertEqual(s3.region, "us-east-1")
        self.assertEqual(s3.bucket, "")
        self.assertIsNone(s3.url)
        self.assertIsNone(s3.endpoint)
        self.assertFalse(s3.use_path_style_endpoint)
        self.assertFalse(s3.throw)

    def testCustomFieldValues(self) -> None:
        """
        Test that S3 stores custom field values correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        s3 = S3(
            key="AKIAIOSFODNN7EXAMPLE",
            secret="wJalrXUtnFEMI",
            region="eu-west-1",
            bucket="my-bucket",
            url="https://s3.eu-west-1.amazonaws.com",
            endpoint="https://s3.eu-west-1.amazonaws.com",
            use_path_style_endpoint=True,
            throw=True,
        )
        self.assertEqual(s3.key, "AKIAIOSFODNN7EXAMPLE")
        self.assertEqual(s3.secret, "wJalrXUtnFEMI")
        self.assertEqual(s3.region, "eu-west-1")
        self.assertEqual(s3.bucket, "my-bucket")
        self.assertEqual(s3.url, "https://s3.eu-west-1.amazonaws.com")
        self.assertEqual(s3.endpoint, "https://s3.eu-west-1.amazonaws.com")
        self.assertTrue(s3.use_path_style_endpoint)
        self.assertTrue(s3.throw)

    def testInvalidKeyTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string key raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            S3(key=123)  # type: ignore[arg-type]

    def testInvalidSecretTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string secret raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            S3(secret=456)  # type: ignore[arg-type]

    def testInvalidRegionTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string region raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            S3(region=10)  # type: ignore[arg-type]

    def testEmptyRegionRaisesValueError(self) -> None:
        """
        Test that an empty string for region raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            S3(region="")

    def testInvalidUrlTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string non-None url raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            S3(url=123)  # type: ignore[arg-type]

    def testInvalidEndpointTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string non-None endpoint raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            S3(endpoint=456)  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen S3 instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        s3 = S3()
        with self.assertRaises(FrozenInstanceError):
            s3.key = "new-key"  # type: ignore[misc]

# ===========================================================================
# Local entity
# ===========================================================================

class TestLocalEntity(TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up the custom storage directory after all tests complete.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Remove custom storage directory if it exists
        path = Path.cwd() / "storage" / "custom"
        if path.exists():
            shutil.rmtree(path)

    def testDefaultConstruction(self) -> None:
        """
        Test that Local can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        local = Local()
        self.assertIsInstance(local, Local)

    def testDefaultPath(self) -> None:
        """
        Test that the default path is set to the expected value.

        Returns
        -------
        None
            This method does not return a value.
        """
        local = Local()
        self.assertEqual(local.path, "storage/app/private")

    def testCustomPath(self) -> None:
        """
        Test that a custom path is stored correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        local = Local(path="storage/custom/private")
        self.assertEqual(local.path, "storage/custom/private")

    def testEmptyPathRaisesValueError(self) -> None:
        """
        Test that an empty path string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Local(path="")

    def testWhitespacePathRaisesValueError(self) -> None:
        """
        Test that a whitespace-only path string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Local(path="   ")

    def testInvalidPathTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string path raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Local(path=123)  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Local instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        local = Local()
        with self.assertRaises(FrozenInstanceError):
            local.path = "other"  # type: ignore[misc]

# ===========================================================================
# Public entity
# ===========================================================================

class TestPublicEntity(TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up the custom storage directory after all tests complete.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Remove custom storage directory if it exists
        path = Path.cwd() / "storage" / "custom"
        if path.exists():
            shutil.rmtree(path)

    def testDefaultConstruction(self) -> None:
        """
        Test that Public can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        pub = Public()
        self.assertIsInstance(pub, Public)

    def testDefaultFieldValues(self) -> None:
        """
        Test that the default path and url are set to the expected values.

        Returns
        -------
        None
            This method does not return a value.
        """
        pub = Public()
        self.assertEqual(pub.path, "storage/app/public")
        self.assertEqual(pub.url, "/static")

    def testCustomFieldValues(self) -> None:
        """
        Test that custom path and url are stored correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        pub = Public(path="storage/custom/public", url="/files")
        self.assertEqual(pub.path, "storage/custom/public")
        self.assertEqual(pub.url, "/files")

    def testEmptyPathRaisesValueError(self) -> None:
        """
        Test that an empty path raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Public(path="", url="/static")

    def testEmptyUrlRaisesValueError(self) -> None:
        """
        Test that an empty url raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Public(path="storage/app/public", url="")

    def testInvalidPathTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string path raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Public(path=123, url="/static")  # type: ignore[arg-type]

    def testInvalidUrlTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string url raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Public(path="storage/app/public", url=456)  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Public instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        pub = Public()
        with self.assertRaises(FrozenInstanceError):
            pub.path = "other"  # type: ignore[misc]

# ===========================================================================
# Disks entity
# ===========================================================================

class TestDisksEntity(TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up the custom storage directory after all tests complete.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Remove custom storage directory if it exists
        path = Path.cwd() / "storage" / "custom"
        if path.exists():
            shutil.rmtree(path)

    def testDefaultConstruction(self) -> None:
        """
        Test that Disks can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        disks = Disks()
        self.assertIsInstance(disks, Disks)

    def testDefaultLocalIsLocalInstance(self) -> None:
        """
        Test that the default local attribute is a Local instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        disks = Disks()
        self.assertIsInstance(disks.local, Local)

    def testDefaultPublicIsPublicInstance(self) -> None:
        """
        Test that the default public attribute is a Public instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        disks = Disks()
        self.assertIsInstance(disks.public, Public)

    def testDefaultAwsIsS3Instance(self) -> None:
        """
        Test that the default aws attribute is an S3 instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        disks = Disks()
        self.assertIsInstance(disks.aws, S3)

    def testDictConversionForLocal(self) -> None:
        """
        Test that a dict for local is converted to a Local instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        disks = Disks(local={"path": "storage/custom/private"})
        self.assertIsInstance(disks.local, Local)
        self.assertEqual(disks.local.path, "storage/custom/private")

    def testDictConversionForPublic(self) -> None:
        """
        Test that a dict for public is converted to a Public instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        disks = Disks(public={"path": "storage/custom/public", "url": "/assets"})
        self.assertIsInstance(disks.public, Public)
        self.assertEqual(disks.public.url, "/assets")

    def testDictConversionForAws(self) -> None:
        """
        Test that a dict for aws is converted to an S3 instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        disks = Disks(aws={"region": "eu-central-1"})
        self.assertIsInstance(disks.aws, S3)
        self.assertEqual(disks.aws.region, "eu-central-1")

    def testInvalidLocalTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for local raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Disks(local="not_a_local")  # type: ignore[arg-type]

    def testInvalidPublicTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for public raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Disks(public=99)  # type: ignore[arg-type]

    def testInvalidAwsTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for aws raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Disks(aws=True)  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Disks instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        disks = Disks()
        with self.assertRaises(FrozenInstanceError):
            disks.local = Local()  # type: ignore[misc]

# ===========================================================================
# Filesystems entity
# ===========================================================================

class TestFilesystemsEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Filesystems can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        fs = Filesystems()
        self.assertIsInstance(fs, Filesystems)

    def testDefaultDisksIsDisksInstance(self) -> None:
        """
        Test that the default disks attribute is a Disks instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        fs = Filesystems()
        self.assertIsInstance(fs.disks, Disks)

    def testDefaultIsValidOption(self) -> None:
        """
        Test that the default disk name is one of the valid options.

        Returns
        -------
        None
            This method does not return a value.
        """
        fs = Filesystems()
        self.assertIn(fs.default, ["local", "public", "aws"])

    def testCustomDefaultLocal(self) -> None:
        """
        Test that setting default to 'local' works correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        fs = Filesystems(default="local")
        self.assertEqual(fs.default, "local")

    def testCustomDefaultPublic(self) -> None:
        """
        Test that setting default to 'public' works correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        fs = Filesystems(default="public")
        self.assertEqual(fs.default, "public")

    def testCustomDefaultAws(self) -> None:
        """
        Test that setting default to 'aws' works correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        fs = Filesystems(default="aws")
        self.assertEqual(fs.default, "aws")

    def testInvalidDefaultRaisesValueError(self) -> None:
        """
        Test that an invalid default disk name raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Filesystems(default="s3")

    def testDictConversionForDisks(self) -> None:
        """
        Test that a dict for disks is converted to a Disks instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        fs = Filesystems(disks={"aws": {"region": "ap-southeast-1"}})
        self.assertIsInstance(fs.disks, Disks)
        self.assertEqual(fs.disks.aws.region, "ap-southeast-1")

    def testInvalidDisksTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for disks raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Filesystems(disks="not_a_disks")  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Filesystems instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        fs = Filesystems()
        with self.assertRaises(FrozenInstanceError):
            fs.default = "aws"  # type: ignore[misc]
