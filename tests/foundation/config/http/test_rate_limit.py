from dataclasses import FrozenInstanceError
from orionis.test import TestCase
from orionis.foundation.config.http.entitites.rate_limit import HTTPRateLimit

# ===========================================================================
# HTTPRateLimit entity
# ===========================================================================


class TestHTTPRateLimit(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Construct HTTPRateLimit with all default values.

        Verifies that an HTTPRateLimit instance can be created without
        providing any arguments.

        Returns
        -------
        None
            This method does not return a value.
        """
        rl = HTTPRateLimit()
        self.assertIsInstance(rl, HTTPRateLimit)

    def testDefaultRateLimitEnabledIsBool(self) -> None:
        """
        Verify rate_limit_enabled defaults to a boolean.

        Ensures the field is typed correctly when no environment
        variable overrides the default.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(HTTPRateLimit().rate_limit_enabled, bool)

    def testDefaultRateLimitRequestsIsPositiveInt(self) -> None:
        """
        Verify rate_limit_requests defaults to a positive integer.

        Ensures the default request cap is a strictly positive int
        when no environment variable is present.

        Returns
        -------
        None
            This method does not return a value.
        """
        val = HTTPRateLimit().rate_limit_requests
        self.assertIsInstance(val, int)
        self.assertGreater(val, 0)

    def testDefaultRateLimitWindowSecondsIsPositiveInt(self) -> None:
        """
        Verify rate_limit_window_seconds defaults to a positive integer.

        Ensures the default time window is a strictly positive int
        when no environment variable is present.

        Returns
        -------
        None
            This method does not return a value.
        """
        val = HTTPRateLimit().rate_limit_window_seconds
        self.assertIsInstance(val, int)
        self.assertGreater(val, 0)

    def testCustomRateLimitEnabledTrue(self) -> None:
        """
        Accept True for rate_limit_enabled.

        Verifies that enabling rate limiting is stored on the instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        rl = HTTPRateLimit(rate_limit_enabled=True)
        self.assertTrue(rl.rate_limit_enabled)

    def testCustomRateLimitEnabledFalse(self) -> None:
        """
        Accept False for rate_limit_enabled.

        Verifies that disabling rate limiting is stored on the instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        rl = HTTPRateLimit(rate_limit_enabled=False)
        self.assertFalse(rl.rate_limit_enabled)

    def testCustomRateLimitRequests(self) -> None:
        """
        Accept a custom positive integer for rate_limit_requests.

        Verifies that a specific request cap is stored on the
        HTTPRateLimit instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        rl = HTTPRateLimit(rate_limit_requests=200)
        self.assertEqual(rl.rate_limit_requests, 200)

    def testCustomRateLimitWindowSeconds(self) -> None:
        """
        Accept a custom positive integer for rate_limit_window_seconds.

        Verifies that a specific time window is stored on the
        HTTPRateLimit instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        rl = HTTPRateLimit(rate_limit_window_seconds=120)
        self.assertEqual(rl.rate_limit_window_seconds, 120)

    def testInvalidRateLimitEnabledTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when rate_limit_enabled is not a boolean.

        Verifies that a string value for rate_limit_enabled triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRateLimit(rate_limit_enabled="true")  # type: ignore[arg-type]

    def testInvalidRateLimitRequestsTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when rate_limit_requests is not an integer.

        Verifies that a string value for rate_limit_requests triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRateLimit(rate_limit_requests="100")  # type: ignore[arg-type]

    def testBoolAsRateLimitRequestsRaisesTypeError(self) -> None:
        """
        Raise TypeError when rate_limit_requests is a boolean.

        Verifies that bool values are rejected even though bool is a
        subclass of int in Python.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRateLimit(rate_limit_requests=True)  # type: ignore[arg-type]

    def testRateLimitRequestsZeroRaisesValueError(self) -> None:
        """
        Raise ValueError when rate_limit_requests is zero.

        Verifies that a zero request cap is rejected as a non-positive
        integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            HTTPRateLimit(rate_limit_requests=0)

    def testRateLimitRequestsNegativeRaisesValueError(self) -> None:
        """
        Raise ValueError when rate_limit_requests is negative.

        Verifies that a negative request cap is rejected during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            HTTPRateLimit(rate_limit_requests=-1)

    def testInvalidRateLimitWindowSecondsTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when rate_limit_window_seconds is not an integer.

        Verifies that a float value for the time window triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRateLimit(
                rate_limit_window_seconds="60"  # type: ignore[arg-type]
            )

    def testBoolAsRateLimitWindowSecondsRaisesTypeError(self) -> None:
        """
        Raise TypeError when rate_limit_window_seconds is a boolean.

        Verifies that bool values are rejected even though bool is a
        subclass of int in Python.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRateLimit(
                rate_limit_window_seconds=True  # type: ignore[arg-type]
            )

    def testRateLimitWindowSecondsZeroRaisesValueError(self) -> None:
        """
        Raise ValueError when rate_limit_window_seconds is zero.

        Verifies that a zero-second window is rejected as a
        non-positive integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            HTTPRateLimit(rate_limit_window_seconds=0)

    def testRateLimitWindowSecondsNegativeRaisesValueError(self) -> None:
        """
        Raise ValueError when rate_limit_window_seconds is negative.

        Verifies that a negative time window is rejected during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            HTTPRateLimit(rate_limit_window_seconds=-30)

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Raise FrozenInstanceError when mutating an HTTPRateLimit instance.

        Confirms the dataclass is immutable and rejects attribute
        reassignment after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        rl = HTTPRateLimit()
        with self.assertRaises(FrozenInstanceError):
            rl.rate_limit_enabled = True  # type: ignore[misc]
