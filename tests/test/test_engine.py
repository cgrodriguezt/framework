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
        self.assertEqual(len(ITestingEngine.__abstractmethods__), 8)

    # ------------------------------------------------ concrete subclass contract

    def testConcreteSubclassImplementingAllMethodsCanBeInstantiated(self):
        """
        Allow instantiation of a concrete subclass implementing all methods.

        Validates that providing implementations for all abstract methods
        is sufficient to construct an engine instance.
        """
        class MinimalEngine(ITestingEngine):
            def setVerbosity(self, _verbosity):
                return self

            def setFailFast(self, *, fail_fast=False):  # noqa: ARG002
                return self

            def setStartDir(self, _start_dir):
                return self

            def setFilePattern(self, _file_pattern):
                return self

            def setMethodPattern(self, _method_pattern):
                return self

            def withoutPanel(self):
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

    async def _getEngine(self) -> TestingEngine:
        """Return a TestingEngine built from the live Application instance."""
        app = await Application.resolve()
        return TestingEngine(app)

    # ------------------------------------------------ instantiation

    async def testInstantiationWithApplicationSucceeds(self) -> None:
        """
        Create a TestingEngine instance using the live application.

        Validates that TestingEngine can be constructed from a valid
        IApplication instance without raising any error.
        """
        engine = await self._getEngine()
        self.assertIsInstance(engine, TestingEngine)

    async def testIsInstanceOfITestingEngine(self) -> None:
        """
        Confirm the created engine satisfies the ITestingEngine interface.

        Validates the polymorphic contract so that TestingEngine can be
        used wherever an ITestingEngine is expected.
        """
        engine = await self._getEngine()
        self.assertIsInstance(engine, ITestingEngine)

    # ------------------------------------------------ setVerbosity

    async def testSetVerbosityReturnsSelf(self) -> None:
        """
        Return the same engine instance from setVerbosity.

        Validates that setVerbosity supports fluent method chaining by
        returning 'self'.
        """
        engine = await self._getEngine()
        result = engine.setVerbosity(1)
        self.assertIs(result, engine)

    async def testSetVerbosityWithZero(self) -> None:
        """
        Accept zero as a valid verbosity level in setVerbosity.

        Validates that the silent verbosity level (0) is accepted without
        error and that the engine is still usable.
        """
        engine = await self._getEngine()
        result = engine.setVerbosity(0)
        self.assertIsInstance(result, TestingEngine)

    async def testSetVerbosityWithTwo(self) -> None:
        """
        Accept two as a valid verbosity level in setVerbosity.

        Validates that the detailed verbosity level (2) is accepted
        without error.
        """
        engine = await self._getEngine()
        result = engine.setVerbosity(2)
        self.assertIsInstance(result, TestingEngine)

    # ------------------------------------------------ setFailFast

    async def testSetFailFastReturnsSelf(self) -> None:
        """
        Return the same engine instance from setFailFast.

        Validates that setFailFast supports fluent method chaining by
        returning 'self'.
        """
        engine = await self._getEngine()
        result = engine.setFailFast(fail_fast=True)
        self.assertIs(result, engine)

    async def testSetFailFastWithFalseReturnsSelf(self) -> None:
        """
        Return self from setFailFast when fail_fast is False.

        Validates that disabling fail-fast mode also returns the engine
        instance for chaining.
        """
        engine = await self._getEngine()
        result = engine.setFailFast(fail_fast=False)
        self.assertIs(result, engine)

    # ------------------------------------------------ setStartDir

    async def testSetStartDirReturnsSelf(self) -> None:
        """
        Return the same engine instance from setStartDir.

        Validates that setStartDir supports fluent method chaining by
        returning 'self'.
        """
        engine = await self._getEngine()
        result = engine.setStartDir("tests")
        self.assertIs(result, engine)

    async def testSetStartDirAcceptsArbitraryString(self) -> None:
        """
        Accept any string value as the start directory in setStartDir.

        Validates that setStartDir stores whatever path string is provided
        without raising an error at assignment time.
        """
        engine = await self._getEngine()
        result = engine.setStartDir("tests/test")
        self.assertIsInstance(result, TestingEngine)

    # ------------------------------------------------ setFilePattern

    async def testSetFilePatternReturnsSelf(self) -> None:
        """
        Return the same engine instance from setFilePattern.

        Validates that setFilePattern supports fluent method chaining by
        returning 'self'.
        """
        engine = await self._getEngine()
        result = engine.setFilePattern("test_*.py")
        self.assertIs(result, engine)

    async def testSetFilePatternAcceptsGlobPattern(self) -> None:
        """
        Accept a glob pattern string as the file pattern in setFilePattern.

        Validates that setFilePattern stores the provided pattern without
        raising an error at assignment time.
        """
        engine = await self._getEngine()
        result = engine.setFilePattern("test_*.py")
        self.assertIsInstance(result, TestingEngine)

    # ------------------------------------------------ setMethodPattern

    async def testSetMethodPatternReturnsSelf(self) -> None:
        """
        Return the same engine instance from setMethodPattern.

        Validates that setMethodPattern supports fluent method chaining by
        returning 'self'.
        """
        engine = await self._getEngine()
        try:
            result = engine.setMethodPattern("test*")
            self.assertIs(result, engine)
        finally:
            CoreTestCase.setMethodPattern("test*")

    async def testSetMethodPatternAlsoUpdatesTestCase(self) -> None:
        """
        Update TestCase's method pattern when setMethodPattern is called.

        Validates that the side-effect of setMethodPattern propagates the
        new pattern to the TestCase class so test discovery is consistent.
        """
        engine = await self._getEngine()
        try:
            engine.setMethodPattern("check*")
            self.assertIsNotNone(
                CoreTestCase._method_regex.match("checkSomething"),
            )
            self.assertIsNone(
                CoreTestCase._method_regex.match("testSomething"),
            )
        finally:
            CoreTestCase.setMethodPattern("test*")

    # ------------------------------------------------ method chaining

    async def testFluentChainingAllSetters(self) -> None:
        """
        Support chaining all setter methods in a single expression.

        Validates that every setter returns 'self', enabling a fully
        fluent configuration style.
        """
        try:
            engine = await self._getEngine()
            engine = (
                engine
                .setVerbosity(0)
                .setFailFast(fail_fast=False)
                .setStartDir("tests/test")
                .setFilePattern("test_*.py")
                .setMethodPattern("test*")
            )
            self.assertIsInstance(engine, TestingEngine)
        finally:
            CoreTestCase.setMethodPattern("test*")

    # ------------------------------------------------ discover

    async def testDiscoverReturnsTestSuite(self) -> None:
        """
        Return a unittest.TestSuite from discover.

        Validates that calling discover() on the engine produces the
        expected type regardless of which tests are found.
        """
        engine = await self._getEngine()
        engine.setStartDir("tests/test")
        result = engine.discover()
        self.assertIsInstance(result, unittest.TestSuite)

    async def testDiscoverWithKnownDirReturnsNonEmptySuite(self) -> None:
        """
        Return a non-empty TestSuite when tests exist in the start directory.

        Validates that discover() finds at least one test in the
        'tests/test' directory where our test files reside.
        """
        engine = await self._getEngine()
        engine.setStartDir("tests/test").setFilePattern("test_*.py")
        result = engine.discover()
        test_count = result.countTestCases()
        self.assertGreater(test_count, 0)

    async def testDiscoverWithNonExistentPatternReturnsEmptySuite(self) -> None:
        """
        Return an empty TestSuite when no files match the file pattern.

        Validates that discover() produces an empty suite when the file
        pattern does not match any existing test files.
        """
        engine = await self._getEngine()
        engine.setStartDir("tests/test").setFilePattern("nonexistent_*.py")
        result = engine.discover()
        test_count = result.countTestCases()
        self.assertEqual(test_count, 0)

    # ------------------------------------------------ run

    async def testRunReturnsListOfTestResult(self) -> None:
        """
        Return a list of TestResult objects from run.

        Validates that run() produces a list where every element is an
        instance of TestResult with a valid status.
        """
        engine = await self._getEngine()
        engine.setStartDir("tests/test/")\
              .setFilePattern("test_status.py")\
              .withoutPanel()\
              .setVerbosity(0)
        results = await engine.run()
        self.assertIsInstance(results, list)
        for item in results:
            self.assertIsInstance(item, TestResult)

    async def testRunReturnsNonEmptyListForKnownTestFile(self) -> None:
        """
        Return a list with at least one result when tests are discovered.

        Validates that run() actually executes discovered tests and
        produces at least one result entry.
        """
        engine = await self._getEngine()
        engine.setStartDir("tests/test/")\
              .setFilePattern("test_status.py")\
              .withoutPanel()\
              .setVerbosity(0)
        results = await engine.run()
        self.assertGreater(len(results), 0)
