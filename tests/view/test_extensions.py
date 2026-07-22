from orionis.test import TestCase
from orionis.view.extensions import buildViewExtensions

class TestBuildViewExtensions(TestCase):

    def testReturnsAList(self) -> None:
        """
        Verify buildViewExtensions returns a list instance.

        Validates that the return type is always a list so that callers
        can safely iterate or extend it without type checks.
        """
        result = buildViewExtensions()
        self.assertIsInstance(result, list)

    def testReturnsEmptyListByDefault(self) -> None:
        """
        Verify buildViewExtensions returns an empty list by default.

        Validates the baseline state where no custom Jinja2 extensions
        have been registered with the view system.
        """
        result = buildViewExtensions()
        self.assertEqual(len(result), 0)

    def testResultIsDeterministic(self) -> None:
        """
        Verify buildViewExtensions produces the same result on every call.

        Validates that repeated invocations return equal lists so the
        provider can call it safely during boot without side effects.
        """
        first = buildViewExtensions()
        second = buildViewExtensions()
        self.assertEqual(first, second)

    def testReturnedListIsIndependent(self) -> None:
        """
        Verify mutations on the returned list do not affect subsequent calls.

        Validates that each invocation returns a new list so callers cannot
        corrupt the extension registry by mutating the return value.
        """
        first = buildViewExtensions()
        sentinel = "test-sentinel-value"
        first.append(sentinel)
        second = buildViewExtensions()
        self.assertEqual(len(second), 0)

    def testFunctionIsCallable(self) -> None:
        """
        Confirm buildViewExtensions is a callable function.

        Validates that the builder can be invoked without arguments and
        produces a result compatible with the ViewServiceProvider boot phase.
        """
        self.assertTrue(callable(buildViewExtensions))
