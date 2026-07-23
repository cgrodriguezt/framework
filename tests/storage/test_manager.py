from __future__ import annotations
import tempfile
from pathlib import Path
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.storage.contracts.manager import IStorageManager
from orionis.storage.contracts.uploaded_file import IUploadedFile
from orionis.storage.disk import Disk
from orionis.storage.drivers.azure import AzureStorageDriver
from orionis.storage.drivers.gcs import GoogleStorageDriver
from orionis.storage.drivers.local import LocalStorageDriver
from orionis.storage.drivers.memory import MemoryStorageDriver
from orionis.storage.drivers.s3 import S3StorageDriver
from orionis.storage.exceptions import (
    DiskNotFoundException,
    DriverNotSupportedException,
)
from orionis.storage.manager import StorageManager
from orionis.storage.provider import StorageProvider
from orionis.test import TestCase

class _StubApp:
    """Minimal application stub exposing config and base path."""

    def __init__(self, base_path: Path, config: dict) -> None:
        """
        Initialize the stub with its base path and configuration.

        Parameters
        ----------
        base_path : Path
            Directory acting as the application base path.
        config : dict
            Mapping of configuration keys to raw dictionaries.
        """
        self._base_path = base_path
        self._config = config

    @property
    def basePath(self) -> Path:
        """
        Return the application base path.

        Returns
        -------
        Path
            Base path injected at construction time.
        """
        return self._base_path

    def config(self, key: str) -> dict:
        """
        Return the raw configuration stored under *key*.

        Parameters
        ----------
        key : str
            Configuration key to resolve.

        Returns
        -------
        dict
            Raw configuration dictionary.
        """
        return self._config[key]

class _FakeUpload:
    """Duck-typed multipart payload used to exercise uploaded()."""

    def __init__(self, filename: str, data: bytes) -> None:
        """
        Initialize the fake payload.

        Parameters
        ----------
        filename : str
            Client-supplied file name.
        data : bytes
            Buffered payload content.
        """
        self.filename = filename
        self.content_type = "application/octet-stream"
        self._data = data
        dot = filename.rfind(".")
        self.extension = filename[dot:].lower() if dot > 0 else ""

    @property
    def size(self) -> int:
        """
        Return the payload size in bytes.

        Returns
        -------
        int
            Byte count of the buffered data.
        """
        return len(self._data)

    def read(self) -> bytes:
        """
        Return the full payload.

        Returns
        -------
        bytes
            Buffered content.
        """
        return self._data

    def chunks(self, size: int = 65536):
        """
        Yield the payload in fixed-size chunks.

        Parameters
        ----------
        size : int
            Maximum number of bytes per yielded chunk.
        """
        for start in range(0, len(self._data), size):
            yield self._data[start:start + size]

    def close(self) -> None:
        """Release the fake buffer (no-op)."""

class TestStorageManager(TestCase):

    def setUp(self) -> None:
        """
        Build a manager over a temporary base path before each test.

        The configuration mirrors config/filesystems.py with disk
        roots isolated inside a temporary directory.
        """
        self._tmpdir = tempfile.TemporaryDirectory()
        base = Path(self._tmpdir.name)
        config = {
            "filesystems": {
                "default": "local",
                "disks": {
                    "local": {
                        "driver": "local",
                        "path": str(base / "private"),
                    },
                    "public": {
                        "driver": "local",
                        "path": str(base / "public"),
                        "url": "/static",
                    },
                    "s3": {
                        "driver": "aws",
                        "region": "us-east-1",
                    },
                },
            },
        }
        self._app = _StubApp(base, config)
        self._manager = StorageManager(self._app)  # type: ignore[arg-type]

    def tearDown(self) -> None:
        """
        Remove the temporary base path after each test.

        Ensures disk roots created by the manager are cleaned up.
        """
        self._tmpdir.cleanup()

    # ── Disk resolution ──────────────────────────────────────────────────────

    async def testDefaultReturnsConfiguredDefaultDisk(self) -> None:
        """
        Resolve the disk declared as default in the configuration.

        Validates default() and its disk name.
        """
        disk = self._manager.default()
        self.assertIsInstance(disk, Disk)
        self.assertEqual(disk.name(), "local")

    async def testDiskBuildsLocalDriverForLocalDisks(self) -> None:
        """
        Bind local disks to the local storage driver.

        Validates driver selection from the disk configuration.
        """
        disk = self._manager.disk("local")
        self.assertIsInstance(disk._driver, LocalStorageDriver)

    async def testDiskInstancesAreCachedPerName(self) -> None:
        """
        Reuse the disk instance built on first access.

        Validates the manager-level disk cache.
        """
        self.assertIs(self._manager.disk("public"), self._manager.disk("public"))

    async def testUnknownDiskRaisesDiskNotFound(self) -> None:
        """
        Raise DiskNotFoundException for undeclared disk names.

        Validates the failure contract of disk().
        """
        with self.assertRaises(DiskNotFoundException):
            self._manager.disk("dropbox")

    async def testUnimplementedDriverRaisesDriverNotSupported(self) -> None:
        """
        Raise DriverNotSupportedException for unknown driver names.

        Validates the failure contract when a disk references a
        driver that has no implementation and no custom factory.
        """
        base = Path(self._tmpdir.name)
        manager = StorageManager(
            _StubApp(
                base,
                {
                    "filesystems": {
                        "default": "local",
                        "disks": {
                            "local": {
                                "driver": "local",
                                "path": str(base / "private"),
                            },
                            "s3": {"driver": "dropbox"},
                        },
                    },
                },
            ),  # type: ignore[arg-type]
        )
        with self.assertRaises(DriverNotSupportedException):
            manager.disk("s3")

    async def testCloudDisksBuildOfficialSdkDrivers(self) -> None:
        """
        Bind cloud disks to their official-SDK driver classes.

        Driver construction is lazy, so no cloud SDK needs to be
        installed for the disks to resolve.
        """
        self.assertIsInstance(
            self._manager.disk("s3")._driver, S3StorageDriver,
        )
        self.assertIsInstance(
            self._manager.disk("azure")._driver, AzureStorageDriver,
        )
        self.assertIsInstance(
            self._manager.disk("gcs")._driver, GoogleStorageDriver,
        )

    async def testExtendRegistersCustomDriverFactory(self) -> None:
        """
        Resolve disks through custom factories registered at runtime.

        Validates the extend() extension point using the memory
        driver as an s3 stand-in.
        """
        self._manager.extend("aws", lambda _config: MemoryStorageDriver())
        disk = self._manager.disk("s3")
        await disk.put("f.txt", b"x")
        self.assertTrue(await disk.exists("f.txt"))

    async def testPublicDiskExposesConfiguredUrl(self) -> None:
        """
        Build public URLs from the disk configuration.

        Validates that the url option reaches the driver.
        """
        disk = self._manager.disk("public")
        file = await disk.put("logo.svg", b"<svg/>")
        self.assertEqual(await file.url(), "/static/logo.svg")

    async def testWritesLandInsideConfiguredRoot(self) -> None:
        """
        Anchor disk roots at the configured filesystem paths.

        Validates end-to-end persistence through the resolved disk.
        """
        await self._manager.disk("local").put("inner/data.txt", "ok")
        stored = Path(self._tmpdir.name) / "private" / "inner" / "data.txt"
        self.assertEqual(stored.read_text(encoding="utf-8"), "ok")

    # ── Uploaded files ───────────────────────────────────────────────────────

    async def testUploadedWrapsPayloadForStorage(self) -> None:
        """
        Wrap an HTTP payload and persist it onto a managed disk.

        Validates uploaded() together with storeAs().
        """
        upload = self._manager.uploaded(_FakeUpload("photo.png", b"png-bytes"))  # type: ignore[arg-type]
        self.assertIsInstance(upload, IUploadedFile)

        stored = await upload.storeAs("avatars", "user.png")
        self.assertEqual(stored.path(), "avatars/user.png")
        self.assertEqual(await stored.read(), b"png-bytes")

class TestStorageProvider(TestCase):

    async def testProviderInheritsFrameworkBases(self) -> None:
        """
        Extend both ServiceProvider and DeferrableProvider.

        Validates the provider class hierarchy.
        """
        self.assertTrue(issubclass(StorageProvider, ServiceProvider))
        self.assertTrue(issubclass(StorageProvider, DeferrableProvider))

    async def testProvidesExposesManagerContract(self) -> None:
        """
        Advertise IStorageManager as the provided service.

        Validates the deferred-provider contract.
        """
        self.assertEqual(StorageProvider.provides(), [IStorageManager])
