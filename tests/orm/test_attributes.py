from __future__ import annotations
import uuid
from datetime import UTC, date, datetime
from typing import ClassVar
from orionis.orm import Integer, Model, String, StrictJson, Text, Uuid
from orionis.orm.attributes import getCastHandler, serializeForStorage
from orionis.orm.exceptions import OrmException
from orionis.test import TestCase

class _Doc(Model):
    id = Integer().primary().autoIncrement()
    body = Text().nullable()
    payload = StrictJson().nullable()
    token = Uuid().nullable()
    label = String().nullable()

    casts: ClassVar[dict[str, str]] = {"body": "json"}

class TestCastHandlers(TestCase):

    def testIntAndFloatCasts(self) -> None:
        """
        Cast textual and numeric inputs to int and float.

        Validates the numeric cast handlers.
        """
        self.assertEqual(getCastHandler("int")("42"), 42)
        self.assertEqual(getCastHandler("float")("2.5"), 2.5)

    def testBoolCastHandlesTextualForms(self) -> None:
        """
        Interpret common textual forms as booleans.

        Validates the truthy string table and fallbacks.
        """
        handler = getCastHandler("bool")
        for truthy in ("1", "true", "YES", " on "):
            self.assertTrue(handler(truthy))
        for falsy in ("0", "false", "off", ""):
            self.assertFalse(handler(falsy))
        self.assertTrue(handler(1))
        self.assertFalse(handler(0))

    def testDatetimeCastAcceptsMultipleShapes(self) -> None:
        """
        Cast datetimes from instances, ISO strings, and timestamps.

        Validates every accepted datetime input shape.
        """
        handler = getCastHandler("datetime")
        now = datetime.now(UTC)
        self.assertIs(handler(now), now)
        parsed = handler("2026-07-24T10:30:00")
        self.assertEqual(parsed, datetime(2026, 7, 24, 10, 30))
        stamped = handler(0)
        self.assertEqual(stamped, datetime.fromtimestamp(0, tz=UTC))

    def testDateCastAcceptsMultipleShapes(self) -> None:
        """
        Cast dates from datetimes, dates, and ISO strings.

        Validates every accepted date input shape.
        """
        handler = getCastHandler("date")
        today = date(2026, 7, 24)
        self.assertEqual(handler("2026-07-24"), today)
        self.assertEqual(handler(today), today)
        moment = datetime(2026, 7, 24, 8, 0)
        self.assertEqual(handler(moment), today)

    def testJsonCastDecodesStringsOnly(self) -> None:
        """
        Decode JSON strings and pass decoded structures through.

        Validates the JSON cast idempotency.
        """
        handler = getCastHandler("json")
        self.assertEqual(handler('{"a": 1}'), {"a": 1})
        self.assertEqual(handler(b"[1, 2]"), [1, 2])
        self.assertEqual(handler({"a": 1}), {"a": 1})

    def testUuidCastAcceptsStringAndInstance(self) -> None:
        """
        Cast UUIDs from strings and pass instances through.

        Validates the UUID cast idempotency.
        """
        handler = getCastHandler("uuid")
        value = uuid.uuid4()
        self.assertIs(handler(value), value)
        self.assertEqual(handler(str(value)), value)

    def testUnsupportedCastRaises(self) -> None:
        """
        Raise OrmException for unsupported cast names.

        Validates the cast registry guard.
        """
        with self.assertRaises(OrmException):
            getCastHandler("decimal128")

class TestSerializeForStorage(TestCase):

    def testJsonStructureOnNonJsonColumnIsDumped(self) -> None:
        """
        Serialize structures targeting non-JSON columns to strings.

        Validates the storage-side JSON encoding rule.
        """
        meta = _Doc.__meta__
        result = serializeForStorage(meta, {"body": {"a": 1}})
        self.assertEqual(result["body"], '{"a": 1}')

    def testStructureOnJsonColumnPassesThrough(self) -> None:
        """
        Keep structures intact when the column is a JSON column.

        Validates the JSON column passthrough.
        """
        meta = _Doc.__meta__
        payload = {"a": 1}
        result = serializeForStorage(meta, {"payload": payload})
        self.assertIs(result["payload"], payload)

    def testUuidOnNonUuidColumnIsStringified(self) -> None:
        """
        Serialize UUIDs targeting non-UUID columns to strings.

        Validates the storage-side UUID encoding rule.
        """
        meta = _Doc.__meta__
        value = uuid.uuid4()
        result = serializeForStorage(meta, {"label": value})
        self.assertEqual(result["label"], str(value))

    def testUuidOnUuidColumnPassesThrough(self) -> None:
        """
        Keep UUID instances intact for UUID columns.

        Validates the UUID column passthrough.
        """
        meta = _Doc.__meta__
        value = uuid.uuid4()
        result = serializeForStorage(meta, {"token": value})
        self.assertIs(result["token"], value)

    def testNoneAndUnknownColumnsPassThrough(self) -> None:
        """
        Keep None values and unknown columns untouched.

        Validates the serialization fallbacks.
        """
        meta = _Doc.__meta__
        result = serializeForStorage(meta, {"body": None, "ghost": 5})
        self.assertIsNone(result["body"])
        self.assertEqual(result["ghost"], 5)

class TestAttributeHelpers(TestCase):

    def testGetAttributeReturnsDefaultWhenAbsent(self) -> None:
        """
        Return the provided default for missing attributes.

        Validates the getAttribute fallback.
        """
        doc = _Doc()
        self.assertIsNone(doc.getAttribute("label"))
        self.assertEqual(doc.getAttribute("label", "n/a"), "n/a")

    def testSetAttributeAppliesDeclaredCast(self) -> None:
        """
        Apply declared casts on direct attribute assignment.

        Validates the assignment-time cast path.
        """
        doc = _Doc()
        doc.body = '{"k": true}'
        self.assertEqual(doc.body, {"k": True})

    def testSerializeMatchesToDict(self) -> None:
        """
        Keep serialize() aligned with toDict().

        Validates the collection serialization hook.
        """
        doc = _Doc({"label": "x"})
        self.assertEqual(doc.serialize(), doc.toDict())
