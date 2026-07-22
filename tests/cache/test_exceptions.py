from __future__ import annotations
from orionis.cache.exceptions import CacheException, CacheStoreException
from orionis.test import TestCase

class TestCacheExceptions(TestCase):

    def testCacheExceptionInheritsFromException(self) -> None:
        """
        Verify CacheException is a subclass of Exception.

        Validates that CacheException fits the standard Python exception
        hierarchy and can be caught as a generic Exception.
        """
        self.assertTrue(issubclass(CacheException, Exception))

    def testCacheStoreExceptionInheritsFromCacheException(self) -> None:
        """
        Verify CacheStoreException is a subclass of CacheException.

        Validates the inheritance chain so callers can catch both the
        specific and the base cache error type with a single handler.
        """
        self.assertTrue(issubclass(CacheStoreException, CacheException))

    def testCacheStoreExceptionInheritsFromException(self) -> None:
        """
        Verify CacheStoreException is also a subclass of Exception.

        Validates the full chain: CacheStoreException → CacheException
        → Exception.
        """
        self.assertTrue(issubclass(CacheStoreException, Exception))

    def testRaiseCacheExceptionWithMessage(self) -> None:
        """
        Raise CacheException and confirm the message is preserved.

        Validates that instantiating with a string argument stores the
        message accessible via str(exception).
        """
        msg = "base cache error"
        with self.assertRaises(CacheException) as ctx:
            raise CacheException(msg)
        self.assertEqual(str(ctx.exception), msg)

    def testRaiseCacheStoreExceptionWithMessage(self) -> None:
        """
        Raise CacheStoreException and confirm the message is preserved.

        Validates that CacheStoreException stores its message correctly
        and is catchable at its own type level.
        """
        msg = "unknown store: foobar"
        with self.assertRaises(CacheStoreException) as ctx:
            raise CacheStoreException(msg)
        self.assertEqual(str(ctx.exception), msg)

    def testCatchCacheStoreExceptionAsCacheException(self) -> None:
        """
        Catch CacheStoreException using the CacheException base class.

        Validates polymorphic catching: callers that handle CacheException
        will also intercept CacheStoreException without code changes.
        """
        msg = "store not configured"
        with self.assertRaises(CacheException):
            raise CacheStoreException(msg)

    def testCacheExceptionWithNoArgs(self) -> None:
        """
        Raise CacheException with no arguments.

        Validates that the exception can be raised without a message,
        matching the pattern used in bare re-raise scenarios.
        """
        with self.assertRaises(CacheException):
            raise CacheException

    def testCacheStoreExceptionWithNoArgs(self) -> None:
        """
        Raise CacheStoreException with no arguments.

        Validates zero-argument instantiation so the exception can be
        used with a bare ``raise`` after the message is logged elsewhere.
        """
        with self.assertRaises(CacheStoreException):
            raise CacheStoreException

    def testCacheExceptionIsNotCacheStoreException(self) -> None:
        """
        Confirm CacheException is not a subclass of CacheStoreException.

        Validates that the hierarchy is strictly one-directional and that
        a plain CacheException is not caught by CacheStoreException handlers.
        """
        self.assertFalse(issubclass(CacheException, CacheStoreException))

    def testCacheExceptionCanCarryArgs(self) -> None:
        """
        Preserve multiple positional arguments on CacheException.

        Validates that args tuple is populated for callers that inspect
        exception.args directly.
        """
        exc = CacheException("code", 404)
        self.assertEqual(exc.args, ("code", 404))
