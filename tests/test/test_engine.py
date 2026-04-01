import unittest
from abc import ABC
from orionis.test import TestCase
from orionis.test.cases.case import TestCase as CoreTestCase
from orionis.test.contracts.engine import ITestingEngine
from orionis.test.core.engine import TestingEngine
from orionis.test.entities.result import TestResult
from orionis.support.facades.application import Application

class TestITestingEngine(TestCase):

    # ------------------------------------------------ abstract base class

    def testITestingEngineInheritsFromABC(self):
        """
        Confirm ITestingEngine inherits from ABC.

        Validates the class hierarchy ensuring that all engine contracts
        are enforced as truly abstract.
        """
        self.assertTrue(issubclass(ITestingEngine, ABC))

    def testITestingEngineCannotBeInstantiated(self):
        """
        Raise TypeError when attempting to instantiate ITestingEngine directly.

        Validates that the abstract class cannot be constructed without a
        concrete implementation of its abstract methods.
        """
        with self.assertRaises(TypeError):
            ITestingEngine()  # type: ignore[abstract]

    def testConcreteSubclassWithoutImplementationCannotBeInstantiated(self):
        """
        Raise TypeError for a concrete subclass missing abstract methods.

        Validates that any subclass that does not implement all abstract
        methods is also rejected at instantiation time.
        """
        class IncompleteEngine(ITestingEngine):
            pass

        with self.assertRaises(TypeError):
            IncompleteEngine()  # type: ignore[abstract]

    # ------------------------------------------------ abstract method names

    def testHasAbstractMethodSetVerbosity(self):
        """
        Confirm ITestingEngine declares setVerbosity as an abstract method.

        Validates that setVerbosity is listed in the set of abstract methods
        that concrete subclasses must implement.
        """
        self.assertIn("setVerbosity", ITestingEngine.__abstractmethods__)

    def testHasAbstractMethodSetFailFast(self):
        """
        Confirm ITestingEngine declares setFailFast as an abstract method.

        Validates that setFailFast is listed in the set of abstract methods
        that concrete subclasses must implement.
        """
        self.assertIn("setFailFast", ITestingEngine.__abstractmethods__)

    def testHasAbstractMethodSetStartDir(self):
        """
        Confirm ITestingEngine declares setStartDir as an abstract method.

        Validates that setStartDir is listed in the set of abstract methods
        that concrete subclasses must implement.
        """
        self.assertIn("setStartDir", ITestingEngine.__abstractmethods__)

    def testHasAbstractMethodSetFilePattern(self):
        """
        Confirm ITestingEngine declares setFilePattern as an abstract method.

        Validates that setFilePattern is listed in the set of abstract methods
        that concrete subclasses must implement.
        """
        self.assertIn("setFilePattern", ITestingEngine.__abstractmethods__)

    def testHasAbstractMethodSetMethodPattern(self):
        """
        Confirm ITestingEngine declares setMethodPattern as an abstract method.

        Validates that setMethodPattern is listed in the set of abstract
        methods that concrete subclasses must implement.
        """
        self.assertIn("setMethodPattern", ITestingEngine.__abstractmethods__)

    def testHasAbstractMethodDiscover(self):
        """
        Confirm ITestingEngine declares discover as an abstract method.

        Validates that discover is listed in the set of abstract methods
        that concrete subclasses must implement.
        """
        self.assertIn("discover", ITestingEngine.__abstractmethods__)

    def testHasAbstractMethodRun(self):
        """
        Confirm ITestingEngine declares run as an abstract method.

        Validates that run is listed in the set of abstract methods
        that concrete subclasses must implement.
        """
        self.assertIn("run", ITestingEngine.__abstractmethods__)

    def testHasExactlySevenAbstractMethods(self):
        """
        Confirm ITestingEngine declares exactly seven abstract methods.

        Validates that the interface contract consists of exactly the
        documented methods without any undocumented additions.
        """
        self.assertEqual(len(ITestingEngine.__abstractmethods__), 7)

    # ------------------------------------------------ concrete subclass contract

    def testConcreteSubclassImplementingAllMethodsCanBeInstantiated(self):
        """
        Allow instantiation of a concrete subclass implementing all methods.

        Validates that providing implementations for all abstract methods
        is sufficient to construct an engine instance.
        """
        class MinimalEngine(ITestingEngine):
            def setVerbosity(self, verbosity):
                return self

            def setFailFast(self, *, fail_fast):
                return self

            def setStartDir(self, start_dir):
                return self

            def setFilePattern(self, file_pattern):
                return self

            def setMethodPattern(self, method_pattern):
                return self

            def discover(self):
                return unittest.TestSuite()

            async def run(self):
                return []

        engine = MinimalEngine()
        self.assertIsInstance(engine, ITestingEngine)

    def testConcreteSubclassIsInstanceOfITestingEngine(self):
        """
        Confirm TestingEngine is a concrete subclass of ITestingEngine.

        Validates that the production TestingEngine class satisfies the
        ITestingEngine interface contract.
        """
        self.assertTrue(issubclass(TestingEngine, ITestingEngine))

class TestTestingEngine(TestCase):

    def _getEngine(self) -> TestingEngine:
        """Return a TestingEngine built from the live Application instance."""
        app = Application.resolve()
        return TestingEngine(app)

    # ------------------------------------------------ instantiation

    def testInstantiationWithApplicationSucceeds(self):
        """
        Create a TestingEngine instance using the live application.

        Validates that TestingEngine can be constructed from a valid
        IApplication instance without raising any error.
        """
        engine = self._getEngine()
        self.assertIsInstance(engine, TestingEngine)

    def testIsInstanceOfITestingEngine(self):
        """
        Confirm the created engine satisfies the ITestingEngine interface.

        Validates the polymorphic contract so that TestingEngine can be
        used wherever an ITestingEngine is expected.
        """
        engine = self._getEngine()
        self.assertIsInstance(engine, ITestingEngine)

    # ------------------------------------------------ setVerbosity

    def testSetVerbosityReturnsSelf(self):
        """
        Return the same engine instance from setVerbosity.

        Validates that setVerbosity supports fluent method chaining by
        returning 'self'.
        """
        engine = self._getEngine()
        result = engine.setVerbosity(1)
        self.assertIs(result, engine)

    def testSetVerbosityWithZero(self):
        """
        Accept zero as a valid verbosity level in setVerbosity.

        Validates that the silent verbosity level (0) is accepted without
        error and that the engine is still usable.
        """
        engine = self._getEngine()
        result = engine.setVerbosity(0)
        self.assertIsInstance(result, TestingEngine)

    def testSetVerbosityWithTwo(self):
        """
        Accept two as a valid verbosity level in setVerbosity.

        Validates that the detailed verbosity level (2) is accepted
        without error.
        """
        engine = self._getEngine()
        result = engine.setVerbosity(2)
        self.assertIsInstance(result, TestingEngine)

    # ------------------------------------------------ setFailFast

    def testSetFailFastReturnsSelf(self):
        """
        Return the same engine instance from setFailFast.

        Validates that setFailFast supports fluent method chaining by
        returning 'self'.
        """
        engine = self._getEngine()
        result = engine.setFailFast(fail_fast=True)
        self.assertIs(result, engine)

    def testSetFailFastWithFalseReturnsSelf(self):
        """
        Return self from setFailFast when fail_fast is False.

        Validates that disabling fail-fast mode also returns the engine
        instance for chaining.
        """
        engine = self._getEngine()
        result = engine.setFailFast(fail_fast=False)
        self.assertIs(result, engine)

    # ------------------------------------------------ setStartDir

    def testSetStartDirReturnsSelf(self):
        """
        Return the same engine instance from setStartDir.

        Validates that setStartDir supports fluent method chaining by
        returning 'self'.
        """
        engine = self._getEngine()
        result = engine.setStartDir("tests")
        self.assertIs(result, engine)

    def testSetStartDirAcceptsArbitraryString(self):
        """
        Accept any string value as the start directory in setStartDir.

        Validates that setStartDir stores whatever path string is provided
        without raising an error at assignment time.
        """
        engine = self._getEngine()
        result = engine.setStartDir("tests/test")
        self.assertIsInstance(result, TestingEngine)

    # ------------------------------------------------ setFilePattern

    def testSetFilePatternReturnsSelf(self):
        """
        Return the same engine instance from setFilePattern.

        Validates that setFilePattern supports fluent method chaining by
        returning 'self'.
        """
        engine = self._getEngine()
        result = engine.setFilePattern("test_*.py")
        self.assertIs(result, engine)

    def testSetFilePatternAcceptsGlobPattern(self):
        """
        Accept a glob pattern string as the file pattern in setFilePattern.

        Validates that setFilePattern stores the provided pattern without
        raising an error at assignment time.
        """
        engine = self._getEngine()
        result = engine.setFilePattern("test_*.py")
        self.assertIsInstance(result, TestingEngine)

    # ------------------------------------------------ setMethodPattern

    def testSetMethodPatternReturnsSelf(self):
        """
        Return the same engine instance from setMethodPattern.

        Validates that setMethodPattern supports fluent method chaining by
        returning 'self'.
        """
        engine = self._getEngine()
        original = CoreTestCase._TestCase__method_pattern
        try:
            result = engine.setMethodPattern("test*")
            self.assertIs(result, engine)
        finally:
            CoreTestCase.setMethodPattern(original)

    def testSetMethodPatternAlsoUpdatesTestCase(self):
        """
        Update TestCase's method pattern when setMethodPattern is called.

        Validates that the side-effect of setMethodPattern propagates the
        new pattern to the TestCase class so test discovery is consistent.
        """
        engine = self._getEngine()
        original = CoreTestCase._TestCase__method_pattern
        try:
            engine.setMethodPattern("check*")
            self.assertEqual(
                CoreTestCase._TestCase__method_pattern, "check*"
            )
        finally:
            CoreTestCase.setMethodPattern(original)

    # ------------------------------------------------ method chaining

    def testFluentChainingAllSetters(self):
        """
        Support chaining all setter methods in a single expression.

        Validates that every setter returns 'self', enabling a fully
        fluent configuration style.
        """
        original = CoreTestCase._TestCase__method_pattern
        try:
            engine = (
                self._getEngine()
                .setVerbosity(0)
                .setFailFast(fail_fast=False)
                .setStartDir("tests/test")
                .setFilePattern("test_*.py")
                .setMethodPattern("test*")
            )
            self.assertIsInstance(engine, TestingEngine)
        finally:
            CoreTestCase.setMethodPattern(original)

    # ------------------------------------------------ discover

    def testDiscoverReturnsTestSuite(self):
        """
        Return a unittest.TestSuite from discover.

        Validates that calling discover() on the engine produces the
        expected type regardless of which tests are found.
        """
        engine = self._getEngine()
        engine.setStartDir("tests/test")
        result = engine.discover()
        self.assertIsInstance(result, unittest.TestSuite)

    def testDiscoverWithKnownDirReturnsNonEmptySuite(self):
        """
        Return a non-empty TestSuite when tests exist in the start directory.

        Validates that discover() finds at least one test in the
        'tests/test' directory where our test files reside.
        """
        engine = self._getEngine()
        engine.setStartDir("tests/test").setFilePattern("test_*.py")
        result = engine.discover()
        test_count = result.countTestCases()
        self.assertGreater(test_count, 0)

    def testDiscoverWithNonExistentPatternReturnsEmptySuite(self):
        """
        Return an empty TestSuite when no files match the file pattern.

        Validates that discover() produces an empty suite when the file
        pattern does not match any existing test files.
        """
        engine = self._getEngine()
        engine.setStartDir("tests/test").setFilePattern("nonexistent_*.py")
        result = engine.discover()
        test_count = result.countTestCases()
        self.assertEqual(test_count, 0)

    # ------------------------------------------------ run

    async def testRunReturnsListOfTestResult(self):
        """
        Return a list of TestResult objects from run.

        Validates that run() produces a list where every element is an
        instance of TestResult with a valid status.
        """
        engine = self._getEngine()
        engine.setStartDir("tests/test/").setFilePattern("test_status.py")
        results = await engine.run()
        self.assertIsInstance(results, list)
        for item in results:
            self.assertIsInstance(item, TestResult)

    async def testRunReturnsNonEmptyListForKnownTestFile(self):
        """
        Return a list with at least one result when tests are discovered.

        Validates that run() actually executes discovered tests and
        produces at least one result entry.
        """
        engine = self._getEngine()
        engine.setStartDir("tests/test/").setFilePattern("test_status.py")
        results = await engine.run()
        self.assertGreater(len(results), 0)
