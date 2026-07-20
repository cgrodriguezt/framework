from __future__ import annotations
from datetime import UTC, datetime, timedelta
from orionis.session.entities.record import SessionRecord
from orionis.session.exceptions import SessionException, SessionStorageException
from orionis.test import TestCase

class TestSessionRecord(TestCase):
    """Unit tests for the SessionRecord dataclass."""

    def testRecordStoresIdentifier(self) -> None:
        """
        Persist the session identifier in the id field.

        Validates that the id argument supplied at construction is
        stored verbatim and accessible as an attribute.
        """
        record = SessionRecord(
            id="my-id",
            data={},
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        self.assertEqual(record.id, "my-id")

    def testRecordStoresData(self) -> None:
        """
        Persist the data payload in the data field.

        Validates that arbitrary key-value pairs supplied at construction
        are stored and accessible without modification.
        """
        payload = {"user_id": 7, "role": "editor"}
        record = SessionRecord(
            id="d",
            data=payload,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        self.assertEqual(record.data, payload)

    def testRecordStoresExpiresAt(self) -> None:
        """
        Store the expires_at timestamp accurately.

        Validates that the datetime supplied at construction is
        preserved without alteration.
        """
        ts = datetime(2030, 1, 1, tzinfo=UTC)
        record = SessionRecord(id="e", data={}, expires_at=ts)
        self.assertEqual(record.expires_at, ts)

    def testRecordEmptyDataIsAllowed(self) -> None:
        """
        Accept an empty data dictionary without error.

        Validates that SessionRecord does not enforce a non-empty payload
        since new sessions legitimately start with no data.
        """
        record = SessionRecord(
            id="empty",
            data={},
            expires_at=datetime.now(UTC) + timedelta(minutes=30),
        )
        self.assertEqual(record.data, {})

    def testRecordIsDataclass(self) -> None:
        """
        Verify that SessionRecord behaves as a dataclass.

        Validates that two records with equal fields compare as equal,
        confirming standard dataclass __eq__ semantics.
        """
        ts = datetime.now(UTC) + timedelta(hours=1)
        r1 = SessionRecord(id="x", data={"a": 1}, expires_at=ts)
        r2 = SessionRecord(id="x", data={"a": 1}, expires_at=ts)
        self.assertEqual(r1, r2)

class TestSessionExceptions(TestCase):
    """Unit tests for the session exception hierarchy."""

    def testSessionExceptionIsException(self) -> None:
        """
        Confirm SessionException inherits from the built-in Exception.

        Validates that session exceptions can be caught using the
        generic Exception handler.
        """
        exc = SessionException("base error")
        self.assertIsInstance(exc, Exception)

    def testSessionStorageExceptionIsSessionException(self) -> None:
        """
        Confirm SessionStorageException inherits from SessionException.

        Validates that storage-specific exceptions are catchable via
        the base SessionException handler.
        """
        exc = SessionStorageException("store error")
        self.assertIsInstance(exc, SessionException)

    def testSessionStorageExceptionIsException(self) -> None:
        """
        Confirm SessionStorageException also inherits from Exception.

        Validates the full inheritance chain so that callers can catch
        any session error with a single broad handler if needed.
        """
        exc = SessionStorageException("store error")
        self.assertIsInstance(exc, Exception)

    def testSessionExceptionPreservesMessage(self) -> None:
        """
        Preserve the error message string in the exception args.

        Validates that the message supplied to the constructor is
        accessible through the standard args attribute.
        """
        msg = "something went wrong"
        exc = SessionException(msg)
        self.assertIn(msg, str(exc))

    def testSessionStorageExceptionPreservesMessage(self) -> None:
        """
        Preserve the error message in SessionStorageException.

        Validates that the message supplied at construction is
        accessible through the standard str() representation.
        """
        msg = "disk write failed"
        exc = SessionStorageException(msg)
        self.assertIn(msg, str(exc))

    def testSessionExceptionCanBeRaised(self) -> None:
        """
        Raise and catch SessionException correctly.

        Validates that SessionException integrates with standard Python
        exception handling machinery.
        """
        with self.assertRaises(SessionException):
            err = "test raise"
            raise SessionException(err)

    def testSessionStorageExceptionCanBeRaised(self) -> None:
        """
        Raise and catch SessionStorageException correctly.

        Validates that SessionStorageException integrates with standard
        Python exception handling machinery.
        """
        with self.assertRaises(SessionStorageException):
            err = "test raise"
            raise SessionStorageException(err)

    def testSessionStorageExceptionCaughtAsSessionException(self) -> None:
        """
        Catch SessionStorageException via the SessionException handler.

        Validates the polymorphic catch behaviour expected from the
        exception hierarchy.
        """
        with self.assertRaises(SessionException):
            err = "hierarchy test"
            raise SessionStorageException(err)
