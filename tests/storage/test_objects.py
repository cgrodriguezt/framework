from __future__ import annotations
from orionis.storage.contracts.directory import IDirectory
from orionis.storage.contracts.file import IFile
from orionis.storage.directory import Directory
from orionis.storage.disk import Disk
from orionis.storage.drivers.memory import MemoryStorageDriver
from orionis.storage.exceptions import StoragePathException
from orionis.storage.file import File
from orionis.storage.uploaded_file import UploadedFile
from orionis.test import TestCase

class _FakeUpload:
    """Duck-typed multipart payload for UploadedFile tests."""

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
        self.content_type = "image/png"
        self.closed = False
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

    def chunks(self, size: int = 4):
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
        """Mark the fake buffer as released."""
        self.closed = True

class _FakeManager:
    """Minimal manager stub resolving a single disk."""

    def __init__(self, disk: Disk) -> None:
        """
        Initialize the stub with the disk to hand out.

        Parameters
        ----------
        disk : Disk
            Disk returned for every resolution.
        """
        self._disk = disk

    def disk(self, name: str | None = None) -> Disk:  # noqa: ARG002
        """
        Return the configured disk regardless of *name*.

        Parameters
        ----------
        name : str | None
            Ignored disk name.

        Returns
        -------
        Disk
            The stubbed disk instance.
        """
        return self._disk

class TestDisk(TestCase):

    def setUp(self) -> None:
        """
        Build a disk over a fresh memory driver before each test.

        Keeps every test isolated in its own in-memory store.
        """
        self._disk = Disk(name="fake", driver=MemoryStorageDriver())

    async def testFileFactoryReturnsFileObjects(self) -> None:
        """
        Build File objects bound to the disk driver.

        Validates the file() factory and path normalization.
        """
        file = self._disk.file("avatars//user.png")
        self.assertIsInstance(file, File)
        self.assertEqual(file.path(), "avatars/user.png")

    async def testFileFactoryRejectsRootPath(self) -> None:
        """
        Reject file paths resolving to the disk root.

        Validates the failure contract of file().
        """
        with self.assertRaises(StoragePathException):
            self._disk.file("")

    async def testDirectoryFactoryReturnsDirectoryObjects(self) -> None:
        """
        Build Directory objects bound to the disk driver.

        Validates the directory() factory including the root form.
        """
        directory = self._disk.directory("avatars")
        self.assertIsInstance(directory, Directory)
        self.assertEqual(directory.path(), "avatars")
        self.assertEqual(self._disk.directory().path(), "")

    async def testConvenienceMethodsDelegateToFile(self) -> None:
        """
        Route put/exists/copy/move/delete through File objects.

        Validates the high-level convenience API end to end.
        """
        stored = await self._disk.put("a.txt", b"data")
        self.assertIsInstance(stored, IFile)
        self.assertTrue(await self._disk.exists("a.txt"))

        copied = await self._disk.copy("a.txt", "b.txt")
        self.assertEqual(await copied.read(), b"data")

        moved = await self._disk.move("b.txt", "c.txt")
        self.assertEqual(moved.path(), "c.txt")
        self.assertFalse(await self._disk.exists("b.txt"))

        self.assertTrue(await self._disk.delete("c.txt"))

class TestFile(TestCase):

    def setUp(self) -> None:
        """
        Build a disk over a fresh memory driver before each test.

        Keeps every test isolated in its own in-memory store.
        """
        self._disk = Disk(name="fake", driver=MemoryStorageDriver())

    async def testWriteIsFluent(self) -> None:
        """
        Return the same file object from write().

        Validates fluent chaining on the write path.
        """
        file = self._disk.file("f.txt")
        self.assertIs(await file.write(b"x"), file)

    async def testCopyToReturnsNewFileObject(self) -> None:
        """
        Return a distinct file object pointing at the copy.

        Validates copyTo() semantics and content duplication.
        """
        original = await self._disk.put("one.txt", b"data")
        clone = await original.copyTo("two.txt")
        self.assertEqual(clone.path(), "two.txt")
        self.assertEqual(await clone.read(), b"data")
        self.assertTrue(await original.exists())

    async def testMoveToReturnsNewFileObject(self) -> None:
        """
        Return a distinct file object pointing at the new location.

        Validates moveTo() semantics and source removal.
        """
        original = await self._disk.put("one.txt", b"data")
        moved = await original.moveTo("sub/two.txt")
        self.assertEqual(moved.path(), "sub/two.txt")
        self.assertFalse(await original.exists())

    async def testRenameKeepsDirectory(self) -> None:
        """
        Rename the file inside its current directory.

        Validates rename() path computation.
        """
        original = await self._disk.put("docs/old.txt", b"data")
        renamed = await original.rename("new.txt")
        self.assertEqual(renamed.path(), "docs/new.txt")
        self.assertEqual(await renamed.read(), b"data")

    async def testRenameRejectsSeparators(self) -> None:
        """
        Reject rename targets containing directory separators.

        Validates the failure contract of rename().
        """
        file = await self._disk.put("docs/old.txt", b"data")
        with self.assertRaises(StoragePathException):
            await file.rename("sub/new.txt")

    async def testInfoDelegatesToDriver(self) -> None:
        """
        Return the FileInfo snapshot produced by the driver.

        Validates the info() delegation.
        """
        file = await self._disk.put("f.txt", b"abc")
        info = await file.info()
        self.assertEqual(info.path, "f.txt")
        self.assertEqual(info.size, 3)

class TestDirectory(TestCase):

    def setUp(self) -> None:
        """
        Build a disk over a fresh memory driver before each test.

        Keeps every test isolated in its own in-memory store.
        """
        self._disk = Disk(name="fake", driver=MemoryStorageDriver())

    async def testLifecycleCreateExistsDelete(self) -> None:
        """
        Create, detect, and delete a directory.

        Validates the directory lifecycle end to end.
        """
        directory = self._disk.directory("uploads")
        self.assertFalse(await directory.exists())
        self.assertIs(await directory.create(), directory)
        self.assertTrue(await directory.exists())
        self.assertTrue(await directory.delete())
        self.assertFalse(await directory.exists())

    async def testFilesReturnsFileObjects(self) -> None:
        """
        Return File objects — never strings — from listings.

        Validates files() and allFiles() object mapping.
        """
        await self._disk.put("photos/a.png", b"1")
        await self._disk.put("photos/nested/b.png", b"2")

        photos = await self._disk.directory("photos").files()
        self.assertEqual(len(photos), 1)
        self.assertIsInstance(photos[0], IFile)
        self.assertEqual(photos[0].path(), "photos/a.png")
        self.assertEqual(await photos[0].size(), 1)

        everything = await self._disk.directory("photos").allFiles()
        self.assertEqual(
            [file.path() for file in everything],
            ["photos/a.png", "photos/nested/b.png"],
        )

    async def testDirectoriesReturnsDirectoryObjects(self) -> None:
        """
        Return Directory objects — never strings — from listings.

        Validates directories() and allDirectories() object mapping.
        """
        await self._disk.put("root/a/deep/f.txt", b"x")

        children = await self._disk.directory("root").directories()
        self.assertEqual(len(children), 1)
        self.assertIsInstance(children[0], IDirectory)
        self.assertEqual(children[0].path(), "root/a")

        tree = await self._disk.directory("root").allDirectories()
        self.assertEqual(
            [directory.path() for directory in tree],
            ["root/a", "root/a/deep"],
        )

class TestUploadedFile(TestCase):

    def setUp(self) -> None:
        """
        Build an uploaded file over a memory-backed disk.

        Provides a fake payload and a stub manager so tests run
        without a booted application.
        """
        self._disk = Disk(name="fake", driver=MemoryStorageDriver())
        self._source = _FakeUpload("Profile Photo.png", b"png-payload")
        self._upload = UploadedFile(
            source=self._source,  # type: ignore[arg-type]
            manager=_FakeManager(self._disk),  # type: ignore[arg-type]
        )

    async def testMetadataAccessors(self) -> None:
        """
        Expose the payload metadata through camelCase accessors.

        Validates originalName, extension, size, and mimeType.
        """
        self.assertEqual(self._upload.originalName(), "Profile Photo.png")
        self.assertEqual(self._upload.extension(), ".png")
        self.assertEqual(self._upload.size(), len(b"png-payload"))
        self.assertEqual(self._upload.mimeType(), "image/png")

    async def testHashNameIsStableAndKeepsExtension(self) -> None:
        """
        Generate the random name once and keep the extension.

        Validates hashName() caching and formatting.
        """
        name = self._upload.hashName()
        self.assertTrue(name.endswith(".png"))
        self.assertEqual(name, self._upload.hashName())

    async def testStorePersistsUnderHashName(self) -> None:
        """
        Persist the payload under a generated hash name.

        Validates store() delegation to File.writeStream().
        """
        stored = await self._upload.store("avatars")
        self.assertEqual(stored.path(), f"avatars/{self._upload.hashName()}")
        self.assertEqual(await stored.read(), b"png-payload")

    async def testStoreAsPersistsUnderExplicitName(self) -> None:
        """
        Persist the payload under an explicit name.

        Validates storeAs() and the resulting file content.
        """
        stored = await self._upload.storeAs("avatars", "user.png")
        self.assertEqual(stored.path(), "avatars/user.png")
        self.assertEqual(await stored.read(), b"png-payload")

    async def testStoreAsRejectsSeparators(self) -> None:
        """
        Reject explicit names containing directory separators.

        Validates the failure contract of storeAs().
        """
        with self.assertRaises(StoragePathException):
            await self._upload.storeAs("avatars", "../user.png")

    async def testMoveClosesTheSourceBuffer(self) -> None:
        """
        Release the upload buffer after persisting via move().

        Validates the buffer lifecycle difference between move()
        and copy().
        """
        await self._upload.copy("avatars", "kept.png")
        self.assertFalse(self._source.closed)

        await self._upload.move("avatars", "moved.png")
        self.assertTrue(self._source.closed)

    async def testReadReturnsFullPayload(self) -> None:
        """
        Return the complete buffered payload.

        Validates read() delegation to the source.
        """
        self.assertEqual(await self._upload.read(), b"png-payload")
