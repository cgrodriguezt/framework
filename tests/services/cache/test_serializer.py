from __future__ import annotations
import datetime
import decimal
import json
import tempfile
import uuid
from pathlib import Path
from orionis.services.cache.serializer import Serializer
from orionis.support.types.sentinel import MISSING
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# TestSerializerPrimitives
# ---------------------------------------------------------------------------

class TestSerializerPrimitives(TestCase):

    def testDumpsAndLoadsString(self) -> None:
        """
        Serialize and deserialize a plain string.

        Validates that a string value is preserved exactly through
        a dumps/loads round-trip.
        """
        raw = Serializer.dumps("hello world")
        result = Serializer.loads(raw)
        self.assertEqual(result, "hello world")

    def testDumpsAndLoadsInt(self) -> None:
        """
        Serialize and deserialize an integer value.

        Validates that integer values survive a round-trip without
        type coercion.
        """
        raw = Serializer.dumps(42)
        result = Serializer.loads(raw)
        self.assertEqual(result, 42)
        self.assertIsInstance(result, int)

    def testDumpsAndLoadsFloat(self) -> None:
        """
        Serialize and deserialize a float value.

        Validates that floating-point numbers are preserved during
        serialization.
        """
        raw = Serializer.dumps(3.14)
        result = Serializer.loads(raw)
        self.assertAlmostEqual(result, 3.14)

    def testDumpsAndLoadsBoolTrue(self) -> None:
        """
        Serialize and deserialize the boolean True.

        Validates that boolean True is preserved and not coerced to int.
        """
        raw = Serializer.dumps(True)
        result = Serializer.loads(raw)
        self.assertIs(result, True)

    def testDumpsAndLoadsBoolFalse(self) -> None:
        """
        Serialize and deserialize the boolean False.

        Validates that boolean False is preserved and not coerced to int.
        """
        raw = Serializer.dumps(False)
        result = Serializer.loads(raw)
        self.assertIs(result, False)

    def testDumpsAndLoadsNone(self) -> None:
        """
        Serialize and deserialize the None value.

        Validates that None is encoded and decoded without alteration.
        """
        raw = Serializer.dumps(None)
        result = Serializer.loads(raw)
        self.assertIsNone(result)

    def testDumpsAndLoadsList(self) -> None:
        """
        Serialize and deserialize a nested list structure.

        Validates that list elements and nesting are preserved
        through the round-trip.
        """
        original = [1, "two", 3.0, None, True]
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertEqual(result, original)

    def testDumpsAndLoadsDict(self) -> None:
        """
        Serialize and deserialize a dictionary.

        Validates that all key-value pairs in a dictionary survive
        the serialization round-trip.
        """
        original = {"a": 1, "b": "two", "c": None}
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertEqual(result, original)

    def testDumpsWithIndent(self) -> None:
        """
        Serialize data with non-null indent and verify JSON formatting.

        Validates that the indent parameter produces human-readable
        JSON output with the expected structure.
        """
        raw = Serializer.dumps({"key": "value"}, indent=2)
        parsed = json.loads(raw)
        self.assertEqual(parsed["key"], "value")
        self.assertIn("\n", raw)

# ---------------------------------------------------------------------------
# TestSerializerSpecialTypes
# ---------------------------------------------------------------------------

class TestSerializerSpecialTypes(TestCase):
    """Unit tests for Serializer with Python's special and stdlib types."""

    def testDumpsAndLoadsPath(self) -> None:
        """
        Serialize and deserialize a Path object.

        Validates that a Path instance is reconstructed correctly from
        the serialized form.
        """
        original = Path("/some/path/file.txt")
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, Path)
        self.assertEqual(result, original)

    def testDumpsAndLoadsBytes(self) -> None:
        """
        Serialize and deserialize a bytes object.

        Validates that raw byte data is base64-encoded and then
        reconstructed faithfully.
        """
        original = b"\x00\x01\x02\xff"
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, original)

    def testDumpsAndLoadsDatetime(self) -> None:
        """
        Serialize and deserialize a datetime object.

        Validates that datetime instances survive the ISO-format
        encoding round-trip.
        """
        original = datetime.datetime(2024, 6, 15, 12, 0, 0)
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result, original)

    def testDumpsAndLoadsDate(self) -> None:
        """
        Serialize and deserialize a date object.

        Validates that date instances are correctly round-tripped
        through ISO format.
        """
        original = datetime.date(2024, 6, 15)
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, datetime.date)
        self.assertEqual(result, original)

    def testDumpsAndLoadsTime(self) -> None:
        """
        Serialize and deserialize a time object.

        Validates that time instances are correctly round-tripped
        through ISO format.
        """
        original = datetime.time(10, 30, 45)
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, datetime.time)
        self.assertEqual(result, original)

    def testDumpsAndLoadsTimedelta(self) -> None:
        """
        Serialize and deserialize a timedelta object.

        Validates that timedelta instances are correctly encoded as
        days/seconds/microseconds and then reconstructed.
        """
        original = datetime.timedelta(days=3, seconds=7200, microseconds=500)
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, datetime.timedelta)
        self.assertEqual(result, original)

    def testDumpsAndLoadsDecimal(self) -> None:
        """
        Serialize and deserialize a Decimal object.

        Validates that Decimal values are preserved with full precision
        through string-based encoding.
        """
        original = decimal.Decimal("3.141592653589793")
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, decimal.Decimal)
        self.assertEqual(result, original)

    def testDumpsAndLoadsUUID(self) -> None:
        """
        Serialize and deserialize a UUID object.

        Validates that UUID instances survive the round-trip as
        proper UUID objects.
        """
        original = uuid.UUID("12345678-1234-5678-1234-567812345678")
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, uuid.UUID)
        self.assertEqual(result, original)

    def testDumpsAndLoadsTuple(self) -> None:
        """
        Serialize and deserialize a tuple.

        Validates that tuples are reconstructed as tuples (not lists)
        after deserialization.
        """
        original = (1, 2, 3)
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, tuple)
        self.assertEqual(result, original)

    def testDumpsAndLoadsSet(self) -> None:
        """
        Serialize and deserialize a set.

        Validates that sets are reconstructed with the same elements
        after deserialization.
        """
        original = {1, 2, 3}
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, set)
        self.assertEqual(result, original)

    def testDumpsAndLoadsFrozenset(self) -> None:
        """
        Serialize and deserialize a frozenset.

        Validates that frozensets are reconstructed as frozensets
        after deserialization.
        """
        original = frozenset({10, 20, 30})
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, frozenset)
        self.assertEqual(result, original)

    def testDumpsAndLoadsComplex(self) -> None:
        """
        Serialize and deserialize a complex number.

        Validates that the real and imaginary parts are preserved
        through the round-trip.
        """
        original = complex(3.5, -1.2)
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, complex)
        self.assertEqual(result, original)

    def testDumpsAndLoadsType(self) -> None:
        """
        Serialize and deserialize a type object.

        Validates that a class reference is encoded via its qualified
        module path and decoded back to the original class.
        """
        raw = Serializer.dumps(int)
        result = Serializer.loads(raw)
        self.assertIs(result, int)

    def testDumpsAndLoadsMissing(self) -> None:
        """
        Serialize and deserialize the MISSING sentinel.

        Validates that the MISSING sentinel value is reconstructed
        correctly after the round-trip.
        """
        from orionis.support.types.sentinel import _MISSING_TYPE

        raw = Serializer.dumps(MISSING)
        result = Serializer.loads(raw)
        self.assertIsInstance(result, _MISSING_TYPE)

# ---------------------------------------------------------------------------
# TestSerializerEdgeCases
# ---------------------------------------------------------------------------

class TestSerializerEdgeCases(TestCase):

    def testDumpsEmptyDict(self) -> None:
        """
        Serialize and deserialize an empty dictionary.

        Validates that an empty dict is preserved as an empty dict
        through the round-trip.
        """
        raw = Serializer.dumps({})
        result = Serializer.loads(raw)
        self.assertEqual(result, {})

    def testDumpsEmptyList(self) -> None:
        """
        Serialize and deserialize an empty list.

        Validates that an empty list is preserved after the round-trip.
        """
        raw = Serializer.dumps([])
        result = Serializer.loads(raw)
        self.assertEqual(result, [])

    def testDumpsEmptyString(self) -> None:
        """
        Serialize and deserialize an empty string.

        Validates that an empty string is preserved without modification.
        """
        raw = Serializer.dumps("")
        result = Serializer.loads(raw)
        self.assertEqual(result, "")

    def testDumpsNestedStructure(self) -> None:
        """
        Serialize and deserialize a deeply nested structure.

        Validates that recursive encoding and decoding handles nested
        dicts and lists correctly.
        """
        original = {
            "key": [1, {"inner": (True, None)}, decimal.Decimal("1.5")]
        }
        raw = Serializer.dumps(original)
        result = Serializer.loads(raw)
        self.assertEqual(result["key"][0], 1)
        self.assertEqual(result["key"][1]["inner"], (True, None))
        self.assertEqual(result["key"][2], decimal.Decimal("1.5"))

    def testDumpsUnsupportedTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when serializing an unsupported type.

        Validates that attempting to serialize an object whose type
        is not handled raises TypeError instead of terminating the
        process.
        """

        class _Custom:
            pass

        with self.assertRaises(TypeError):
            Serializer.dumps(_Custom())

    def testLoadsUnknownTypeKeyRaisesValueError(self) -> None:
        """
        Raise ValueError when deserializing an unknown type marker.

        Validates that a JSON payload with an unrecognised ``__type__``
        key raises ValueError on decoding.
        """
        payload = json.dumps({"__type__": "unknown_xyz", "__value__": None})
        with self.assertRaises(ValueError):
            Serializer.loads(payload)

    def testDumpsZeroInt(self) -> None:
        """
        Serialize and deserialize the integer zero.

        Validates that zero is not confused with falsy None during
        serialization.
        """
        raw = Serializer.dumps(0)
        result = Serializer.loads(raw)
        self.assertEqual(result, 0)
        self.assertIsInstance(result, int)

    def testDumpsNegativeFloat(self) -> None:
        """
        Serialize and deserialize a negative floating-point number.

        Validates that negative floats are preserved correctly.
        """
        raw = Serializer.dumps(-0.001)
        result = Serializer.loads(raw)
        self.assertAlmostEqual(result, -0.001)

# ---------------------------------------------------------------------------
# TestSerializerFileOperations
# ---------------------------------------------------------------------------

class TestSerializerFileOperations(TestCase):
    """Unit tests for Serializer file I/O methods."""

    def testDumpToFileAndLoadFromFile(self) -> None:
        """
        Write data to a file and recover it via loadFromFile.

        Validates that dumpToFile produces a valid file and that
        loadFromFile restores the original data faithfully.
        """
        original = {"name": "orionis", "version": 1, "active": True}
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "cache.json"
            Serializer.dumpToFile(original, file_path)
            self.assertTrue(file_path.exists())
            result = Serializer.loadFromFile(file_path)
            self.assertEqual(result, original)

    def testDumpToFileIsAtomic(self) -> None:
        """
        Verify that dumpToFile does not leave a temporary file behind.

        Validates that after a successful write there is no residual
        ``.tmp`` file alongside the target file.
        """
        data = {"x": 42}
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "data.json"
            Serializer.dumpToFile(data, file_path)
            tmp_path = file_path.with_suffix(".tmp")
            self.assertFalse(tmp_path.exists())

    def testLoadFromFileNonExistentReturnsNone(self) -> None:
        """
        Return None when the target file does not exist.

        Validates that loadFromFile gracefully handles missing files
        without raising an exception.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "no_such_file.json"
            result = Serializer.loadFromFile(missing)
            self.assertIsNone(result)

    def testLoadFromFileEmptyReturnsNone(self) -> None:
        """
        Return None when the target file is empty.

        Validates that loadFromFile returns None for a zero-byte file
        rather than raising a JSON parse error.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            empty_file = Path(tmp_dir) / "empty.json"
            empty_file.write_text("", encoding="utf-8")
            result = Serializer.loadFromFile(empty_file)
            self.assertIsNone(result)

    def testDumpToFilePreservesSpecialTypes(self) -> None:
        """
        Preserve special types when writing and reading from a file.

        Validates that Path, UUID, and Decimal values survive the
        file-based serialization round-trip.
        """
        original = {
            "path": Path("/tmp/test"),
            "uid": uuid.UUID("aaaabbbb-cccc-dddd-eeee-ffffaaaabbbb"),
            "amount": decimal.Decimal("99.99"),
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "special.json"
            Serializer.dumpToFile(original, file_path)
            result = Serializer.loadFromFile(file_path)
            self.assertEqual(result["path"], original["path"])
            self.assertEqual(result["uid"], original["uid"])
            self.assertEqual(result["amount"], original["amount"])

    def testDumpToFileOverwritesPreviousContent(self) -> None:
        """
        Overwrite an existing file when dumpToFile is called again.

        Validates that a second write replaces the previous content
        in the cache file completely.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "overwrite.json"
            Serializer.dumpToFile({"v": 1}, file_path)
            Serializer.dumpToFile({"v": 2}, file_path)
            result = Serializer.loadFromFile(file_path)
            self.assertEqual(result["v"], 2)
