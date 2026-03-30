from __future__ import annotations
from unittest.mock import patch
from orionis.test import TestCase
from orionis.services.environment.helpers.functions import env

# ---------------------------------------------------------------------------
# TestEnvHelperGet
# ---------------------------------------------------------------------------

class TestEnvHelperGet(TestCase):

    def testReturnsMockedValue(self):
        """
        Return the value provided by the underlying Env.get call.

        Patches Env.get to return a sentinel and confirms that env() passes
        the return value through unchanged.
        """
        with patch(
            "orionis.services.environment.helpers.functions.Env.get",
            return_value="mocked_value",
        ) as mock_get:
            result = env("SOME_KEY")
            self.assertEqual(result, "mocked_value")
            mock_get.assert_called_once_with("SOME_KEY", None)

    def testPassesKeyToEnvGet(self):
        """
        Forward the key argument to Env.get without modification.

        Verifies that the key string is delivered to the underlying facade
        exactly as provided by the caller.
        """
        with patch(
            "orionis.services.environment.helpers.functions.Env.get",
            return_value=None,
        ) as mock_get:
            env("MY_VAR")
            args, _ = mock_get.call_args
            self.assertEqual(args[0], "MY_VAR")

    def testPassesDefaultNoneWhenOmitted(self):
        """
        Pass None as the default argument when none is supplied by the caller.

        Ensures that omitting the default parameter results in None being
        forwarded to Env.get, not some other sentinel or omission.
        """
        with patch(
            "orionis.services.environment.helpers.functions.Env.get",
            return_value=None,
        ) as mock_get:
            env("MISSING_KEY")
            _, kwargs = mock_get.call_args # NOSONAR
            positional = mock_get.call_args[0]
            # default is the second positional arg
            self.assertIsNone(positional[1])

    def testPassesExplicitDefault(self):
        """
        Forward an explicit default value to Env.get.

        Validates that the helper does not discard a caller-supplied default
        before delegating to the facade.
        """
        with patch(
            "orionis.services.environment.helpers.functions.Env.get",
            return_value="fallback",
        ) as mock_get:
            result = env("ABSENT_KEY", "fallback")
            mock_get.assert_called_once_with("ABSENT_KEY", "fallback")
            self.assertEqual(result, "fallback")

    def testReturnsNoneWhenEnvGetReturnsNone(self):
        """
        Return None when Env.get returns None for a missing variable.

        Confirms that the helper propagates None faithfully rather than
        converting it to another type.
        """
        with patch(
            "orionis.services.environment.helpers.functions.Env.get",
            return_value=None,
        ):
            result = env("NONEXISTENT")
            self.assertIsNone(result)

    def testReturnsIntegerDefault(self):
        """
        Return an integer default value when Env.get returns it.

        Ensures that non-string default types are carried through without
        coercion or modification.
        """
        with patch(
            "orionis.services.environment.helpers.functions.Env.get",
            return_value=42,
        ):
            result = env("INT_KEY", 42)
            self.assertEqual(result, 42)

    def testReturnsBooleanValue(self):
        """
        Return a boolean value when Env.get resolves the key to a bool.

        Validates that boolean results (e.g., from a bool-typed env var)
        are not cast to another type by the helper.
        """
        with patch(
            "orionis.services.environment.helpers.functions.Env.get",
            return_value=True,
        ):
            result = env("BOOL_KEY")
            self.assertIs(result, True)

    def testReturnsListValue(self):
        """
        Return a list value when Env.get resolves the key to a list.

        Confirms that complex return types such as lists pass through
        the helper without transformation.
        """
        with patch(
            "orionis.services.environment.helpers.functions.Env.get",
            return_value=[1, 2, 3],
        ):
            result = env("LIST_KEY")
            self.assertEqual(result, [1, 2, 3])

    def testDelegatesExactlyOnce(self):
        """
        Delegate to Env.get exactly once per env() call.

        Ensures the helper does not call the underlying facade multiple
        times for a single invocation.
        """
        with patch(
            "orionis.services.environment.helpers.functions.Env.get",
            return_value="x",
        ) as mock_get:
            env("KEY")
            self.assertEqual(mock_get.call_count, 1)
