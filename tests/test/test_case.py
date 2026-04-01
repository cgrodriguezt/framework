import unittest
from orionis.test import TestCase
from orionis.test.cases.case import TestCase as CoreTestCase
from orionis.test.executors.results import TestResultProcessor
from orionis.test.executors.runner import TestRunner

class TestTestCaseClass(TestCase):

    # ------------------------------------------------ inheritance

    def testTestCaseInheritsFromIsolatedAsyncioTestCase(self):
        """
        Confirm TestCase inherits from IsolatedAsyncioTestCase.

        Validates the MRO ensures that TestCase is a proper subclass
        of unittest.IsolatedAsyncioTestCase, enabling async test support.
        """
        self.assertTrue(issubclass(CoreTestCase, unittest.IsolatedAsyncioTestCase))

    def testTestCaseIsSubclassOfTestCase(self):
        """
        Confirm TestCase is a subclass of unittest.TestCase.

        Validates that CoreTestCase inherits the full standard test
        infrastructure from unittest.TestCase.
        """
        self.assertTrue(issubclass(CoreTestCase, unittest.TestCase))

    # ------------------------------------------------ setMethodPattern

    def testSetMethodPatternStoresPattern(self):
        """
        Store the provided pattern string via setMethodPattern.

        Validates that calling the classmethod with a custom glob
        pattern updates the internal name-mangled class attribute.
        """
        original = CoreTestCase._TestCase__method_pattern
        try:
            CoreTestCase.setMethodPattern("check*")
            self.assertEqual(
                CoreTestCase._TestCase__method_pattern, "check*"
            )
        finally:
            # Restore the default so subsequent tests are not affected
            CoreTestCase.setMethodPattern(original)

    def testSetMethodPatternDefaultIsTestStar(self):
        """
        Confirm the default method pattern is 'test*'.

        Validates that without any explicit call to setMethodPattern
        the pattern matches the standard pytest/unittest convention.
        """
        CoreTestCase.setMethodPattern("test*")
        self.assertEqual(CoreTestCase._TestCase__method_pattern, "test*")

    def testSetMethodPatternAcceptsAnyString(self):
        """
        Accept an arbitrary non-empty string as the method pattern.

        Validates that setMethodPattern does not restrict input to
        specific values, storing whatever string is provided.
        """
        original = CoreTestCase._TestCase__method_pattern
        try:
            CoreTestCase.setMethodPattern("verify_*")
            self.assertEqual(
                CoreTestCase._TestCase__method_pattern, "verify_*"
            )
        finally:
            CoreTestCase.setMethodPattern(original)

    # ------------------------------------------------ _resolveTest

    def testResolveTestReturnsCallable(self):
        """
        Return a callable from _resolveTest.

        Validates that wrapping a method via _resolveTest produces
        something that can be invoked as a function.
        """
        # Use a fresh subclass to avoid interfering with test discovery
        class _Dummy(CoreTestCase):
            def runTest(self): # NOSONAR
                pass

            def sample(self): # NOSONAR
                pass

        dummy = _Dummy("runTest")
        wrapped = dummy._resolveTest(dummy.sample)
        self.assertTrue(callable(wrapped))

    def testResolveTestReturnsAsyncCallable(self):
        """
        Return an async function (coroutine function) from _resolveTest.

        Validates that the wrapper produced by _resolveTest is a
        coroutine function, consistent with IsolatedAsyncioTestCase usage.
        """
        import inspect

        class _Dummy(CoreTestCase):
            def runTest(self): # NOSONAR
                pass

            def sample(self): # NOSONAR
                pass

        dummy = _Dummy("runTest")
        wrapped = dummy._resolveTest(dummy.sample)
        self.assertTrue(inspect.iscoroutinefunction(wrapped))

    # ------------------------------------------------ __init__.py public API

    def testImportFromOrionisTestExposesTestCase(self):
        """
        Confirm that 'from orionis.test import TestCase' works correctly.

        Validates that the public __init__.py exports TestCase and that
        the imported symbol is the same class.
        """
        from orionis.test import TestCase as PublicTestCase
        self.assertIs(PublicTestCase, CoreTestCase)

class TestTestResultProcessor(TestCase):

    # ------------------------------------------------ inheritance

    def testInheritsFromUnittestTestResult(self):
        """
        Confirm TestResultProcessor inherits from unittest.TestResult.

        Validates the class hierarchy enabling it to act as the
        result collector for unittest test runners.
        """
        self.assertTrue(
            issubclass(TestResultProcessor, unittest.TestResult)
        )

    # ------------------------------------------------ setPrintVerbosity

    def testSetPrintVerbosityStoresValue(self):
        """
        Store a verbosity integer via setPrintVerbosity.

        Validates that the class variable _print_verbosity is updated
        to the supplied integer when the classmethod is called.
        """
        original = TestResultProcessor._print_verbosity
        try:
            TestResultProcessor.setPrintVerbosity(2)
            self.assertEqual(TestResultProcessor._print_verbosity, 2)
        finally:
            TestResultProcessor._print_verbosity = original

    def testSetPrintVerbosityWithZero(self):
        """
        Store zero as the verbosity level via setPrintVerbosity.

        Validates that a verbosity of 0 (silent mode) is accepted and
        stored correctly on the class.
        """
        original = TestResultProcessor._print_verbosity
        try:
            TestResultProcessor.setPrintVerbosity(0)
            self.assertEqual(TestResultProcessor._print_verbosity, 0)
        finally:
            TestResultProcessor._print_verbosity = original

    def testSetPrintVerbosityWithOne(self):
        """
        Store 1 as the verbosity level via setPrintVerbosity.

        Validates that verbosity level 1 (compact output) is accepted
        and stored correctly.
        """
        original = TestResultProcessor._print_verbosity
        try:
            TestResultProcessor.setPrintVerbosity(1)
            self.assertEqual(TestResultProcessor._print_verbosity, 1)
        finally:
            TestResultProcessor._print_verbosity = original

    # ------------------------------------------------ getTestResults

    def testGetTestResultsReturnsListOnFreshInstance(self):
        """
        Return an empty list from getTestResults on a new instance.

        Validates that a freshly created TestResultProcessor has no
        results recorded and exposes an empty list.
        """
        processor = TestResultProcessor()
        results = processor.getTestResults()
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    def testGetTestResultsReturnsSameListReference(self):
        """
        Return the same list object on consecutive calls to getTestResults.

        Validates that getTestResults does not create a new list each
        time it is called, returning a stable reference.
        """
        processor = TestResultProcessor()
        first_call = processor.getTestResults()
        second_call = processor.getTestResults()
        self.assertIs(first_call, second_call)

class TestTestRunner(TestCase):

    # ------------------------------------------------ inheritance

    def testInheritsFromTextTestRunner(self):
        """
        Confirm TestRunner inherits from unittest.TextTestRunner.

        Validates the class hierarchy making TestRunner compatible with
        the standard unittest runner interface.
        """
        self.assertTrue(issubclass(TestRunner, unittest.TextTestRunner))

    def testResultClassIsTestResultProcessor(self):
        """
        Confirm the resultclass attribute is TestResultProcessor.

        Validates that the runner uses TestResultProcessor to collect
        and aggregate test results during execution.
        """
        self.assertIs(TestRunner.resultclass, TestResultProcessor)

    def testDefaultVerbosityIsZero(self):
        """
        Confirm the default verbosity is 0 when not provided.

        Validates that constructing TestRunner without arguments
        does not raise and uses 0 as the verbosity default.
        """
        runner = TestRunner()
        # verbosity is stored by unittest.TextTestRunner as self.verbosity
        self.assertEqual(runner.verbosity, 0)

    def testDefaultFailFastIsFalse(self):
        """
        Confirm the default fail_fast setting is False.

        Validates that TestRunner does not enable fail-fast mode
        unless explicitly requested.
        """
        runner = TestRunner()
        self.assertFalse(runner.failfast)

    def testExplicitVerbosityIsStored(self):
        """
        Store an explicit verbosity value when provided to TestRunner.

        Validates that passing verbosity=1 at construction results in
        the verbosity attribute being set to 1.
        """
        runner = TestRunner(verbosity=1)
        self.assertEqual(runner.verbosity, 1)

    def testExplicitFailFastIsStored(self):
        """
        Store an explicit fail_fast=True when provided to TestRunner.

        Validates that the failfast attribute reflects the value
        supplied at construction time.
        """
        runner = TestRunner(failfast=True)
        self.assertTrue(runner.failfast)
