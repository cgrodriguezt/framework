from __future__ import annotations
import importlib.util
import tempfile
from pathlib import Path
from orionis.foundation.config.filesystems.entitites.aws import S3
from orionis.foundation.config.filesystems.entitites.azure import Azure
from orionis.foundation.config.filesystems.entitites.gcs import GCS
from orionis.storage.drivers.azure import AzureStorageDriver
from orionis.storage.drivers.functions import (
    assertBinaryMode,
    deriveDirectories,
    filterFiles,
    importDriverDependency,
    resolveDownloadTarget,
)
from orionis.storage.drivers.gcs import GoogleStorageDriver
from orionis.storage.drivers.s3 import S3StorageDriver
from orionis.storage.exceptions import (
    MissingStorageDependencyException,
    StoragePathException,
    UnsupportedStorageOperationException,
)
from orionis.test import TestCase

# Shared key fixture emulating an object-store listing.
_KEYS: list[str] = [
    "docs/a.txt",
    "docs/sub/b.txt",
    "docs/sub/",
    "other/c.txt",
    "root.txt",
]

class TestDriverFunctions(TestCase):

    async def testImportDriverDependencyRaisesWithInstallHint(self) -> None:
        """
        Raise a descriptive error for a missing optional package.

        Validates that the exception names the package and both
        installation commands.
        """
        with self.assertRaises(MissingStorageDependencyException) as ctx:
            importDriverDependency(
                "orionis_missing_sdk_xyz", "fake-sdk", "faker",
            )
        message = str(ctx.exception)
        self.assertIn("pip install fake-sdk", message)
        self.assertIn("orionis[faker]", message)

    async def testAssertBinaryModeAcceptsBinaryModes(self) -> None:
        """
        Accept every supported binary mode without raising.

        Validates the mode whitelist shared by cloud drivers.
        """
        for mode in ("rb", "wb", "ab", "rb+", "wb+", "ab+"):
            assertBinaryMode(mode)

    async def testAssertBinaryModeRejectsTextModes(self) -> None:
        """
        Reject text-oriented stream modes.

        Validates the failure contract of the shared mode check.
        """
        with self.assertRaises(UnsupportedStorageOperationException):
            assertBinaryMode("r")

    async def testFilterFilesExcludesMarkersAndScopes(self) -> None:
        """
        Select only file keys under the requested base prefix.

        Validates marker exclusion and recursive scoping.
        """
        self.assertEqual(
            filterFiles(_KEYS, "docs", recursive=False),
            ["docs/a.txt"],
        )
        self.assertEqual(
            filterFiles(_KEYS, "docs", recursive=True),
            ["docs/a.txt", "docs/sub/b.txt"],
        )
        self.assertEqual(
            filterFiles(_KEYS, "", recursive=False),
            ["root.txt"],
        )

    async def testDeriveDirectoriesFromKeysAndMarkers(self) -> None:
        """
        Infer directory prefixes from keys and explicit markers.

        Validates direct and recursive derivation at several bases.
        """
        self.assertEqual(
            deriveDirectories(_KEYS, "docs", recursive=False),
            ["docs/sub"],
        )
        self.assertEqual(
            deriveDirectories(_KEYS, "", recursive=False),
            ["docs", "other"],
        )
        self.assertEqual(
            deriveDirectories(_KEYS, "", recursive=True),
            ["docs", "docs/sub", "other"],
        )

    async def testResolveDownloadTargetHandlesDirectories(self) -> None:
        """
        Keep the remote file name when the destination is a folder.

        Validates directory targets and parent creation for file
        targets.
        """
        with tempfile.TemporaryDirectory() as tmp:
            into_dir = resolveDownloadTarget("docs/report.pdf", tmp)
            self.assertEqual(into_dir, Path(tmp) / "report.pdf")

            explicit = resolveDownloadTarget(
                "docs/report.pdf", Path(tmp) / "nested" / "out.pdf",
            )
            self.assertEqual(explicit.name, "out.pdf")
            self.assertTrue(explicit.parent.is_dir())

class TestS3StorageDriver(TestCase):

    async def testUrlUsesVirtualHostAddress(self) -> None:
        """
        Compose the canonical virtual-host URL for the bucket.

        Validates URL building and quoting without any SDK.
        """
        driver = S3StorageDriver(S3(bucket="media", region="us-east-1"))
        self.assertEqual(
            await driver.url("img/a b.png"),
            "https://media.s3.us-east-1.amazonaws.com/img/a%20b.png",
        )

    async def testUrlPrefersConfiguredBaseUrl(self) -> None:
        """
        Prefer the configured base URL over computed addresses.

        Validates the url override option of the disk.
        """
        driver = S3StorageDriver(
            S3(bucket="media", url="https://cdn.example.com/"),
        )
        self.assertEqual(
            await driver.url("logo.svg"),
            "https://cdn.example.com/logo.svg",
        )

    async def testUrlUsesCustomEndpointWhenConfigured(self) -> None:
        """
        Compose path-style URLs against custom endpoints.

        Validates URL building for S3-compatible services.
        """
        driver = S3StorageDriver(
            S3(bucket="media", endpoint="http://localhost:9000"),
        )
        self.assertEqual(
            await driver.url("f.bin"),
            "http://localhost:9000/media/f.bin",
        )

    async def testPathTraversalRejectedBeforeSdkBootstrap(self) -> None:
        """
        Reject invalid paths before touching the SDK.

        Validates that path safety never depends on boto3.
        """
        driver = S3StorageDriver(S3(bucket="media"))
        with self.assertRaises(StoragePathException):
            await driver.read("../escape")

    async def testOpenRejectsTextModesWithoutSdk(self) -> None:
        """
        Reject text stream modes before touching the SDK.

        Validates the shared mode whitelist in the S3 driver.
        """
        driver = S3StorageDriver(S3(bucket="media"))
        with self.assertRaises(UnsupportedStorageOperationException):
            driver.open("f.txt", "w")

    async def testOperationsRequireOptionalDependency(self) -> None:
        """
        Surface the missing boto3 package with install instructions.

        Only asserted when boto3 is absent from the environment, so
        the test remains valid on machines that have it installed.
        """
        if importlib.util.find_spec("boto3") is not None:
            return
        driver = S3StorageDriver(S3(bucket="media"))
        with self.assertRaises(MissingStorageDependencyException):
            await driver.exists("f.txt")

class TestAzureStorageDriver(TestCase):

    async def testUrlComposedFromAccountAndContainer(self) -> None:
        """
        Compose the canonical Azure Blob URL for the container.

        Validates URL building and quoting without any SDK.
        """
        driver = AzureStorageDriver(
            Azure(account_name="acct", container="media"),
        )
        self.assertEqual(
            await driver.url("img/a b.png"),
            "https://acct.blob.core.windows.net/media/img/a%20b.png",
        )

    async def testCredentialsParsedFromConnectionString(self) -> None:
        """
        Derive the account name and key from the connection string.

        Validates the pure parsing performed at construction time.
        """
        connection = (
            "DefaultEndpointsProtocol=https;AccountName=demo;"
            "AccountKey=c2VjcmV0;EndpointSuffix=core.windows.net"
        )
        driver = AzureStorageDriver(
            Azure(connection_string=connection, container="media"),
        )
        self.assertEqual(
            await driver.url("f.txt"),
            "https://demo.blob.core.windows.net/media/f.txt",
        )

    async def testSetVisibilityIsUnsupported(self) -> None:
        """
        Reject per-blob visibility changes.

        Validates the documented Azure limitation.
        """
        driver = AzureStorageDriver(Azure(container="media"))
        with self.assertRaises(UnsupportedStorageOperationException):
            await driver.setVisibility("f.txt", "public")

    async def testTemporaryUrlRequiresAccountKey(self) -> None:
        """
        Reject SAS generation without an account key.

        Validates the failure contract of temporaryUrl().
        """
        driver = AzureStorageDriver(
            Azure(account_name="acct", container="media"),
        )
        with self.assertRaises(UnsupportedStorageOperationException):
            await driver.temporaryUrl("f.txt", 60)

    async def testOperationsRequireOptionalDependency(self) -> None:
        """
        Surface the missing Azure SDK with install instructions.

        Only asserted when azure-storage-blob is absent from the
        environment, so the test remains valid anywhere.
        """
        if importlib.util.find_spec("azure") is not None:
            return
        driver = AzureStorageDriver(Azure(container="media"))
        with self.assertRaises(MissingStorageDependencyException):
            await driver.exists("f.txt")

class TestGoogleStorageDriver(TestCase):

    async def testUrlUsesCanonicalGoogleAddress(self) -> None:
        """
        Compose the canonical storage.googleapis.com URL.

        Validates URL building and quoting without any SDK.
        """
        driver = GoogleStorageDriver(GCS(bucket="media"))
        self.assertEqual(
            await driver.url("img/a b.png"),
            "https://storage.googleapis.com/media/img/a%20b.png",
        )

    async def testUrlPrefersConfiguredBaseUrl(self) -> None:
        """
        Prefer the configured base URL over the canonical address.

        Validates the url override option of the disk.
        """
        driver = GoogleStorageDriver(
            GCS(bucket="media", url="https://cdn.example.com"),
        )
        self.assertEqual(
            await driver.url("logo.svg"),
            "https://cdn.example.com/logo.svg",
        )

    async def testPathTraversalRejectedBeforeSdkBootstrap(self) -> None:
        """
        Reject invalid paths before touching the SDK.

        Validates that path safety never depends on the Google SDK.
        """
        driver = GoogleStorageDriver(GCS(bucket="media"))
        with self.assertRaises(StoragePathException):
            await driver.read("..\\escape")

    async def testSetVisibilityValidatesLevelWithoutSdk(self) -> None:
        """
        Reject unknown visibility levels before touching the SDK.

        Validates the pure level validation of setVisibility().
        """
        driver = GoogleStorageDriver(GCS(bucket="media"))
        with self.assertRaises(UnsupportedStorageOperationException):
            await driver.setVisibility("f.txt", "secret")

    async def testOperationsRequireOptionalDependency(self) -> None:
        """
        Surface the missing Google SDK with install instructions.

        Only asserted when google-cloud-storage is absent from the
        environment, so the test remains valid anywhere.
        """
        if importlib.util.find_spec("google") is not None:
            return
        driver = GoogleStorageDriver(GCS(bucket="media"))
        with self.assertRaises(MissingStorageDependencyException):
            await driver.exists("f.txt")
