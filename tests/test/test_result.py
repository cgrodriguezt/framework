import dataclasses
from orionis.test import TestCase
from orionis.test.entities.result import TestResult
from orionis.test.enums.status import TestStatus

# ------------------------------------------------ helpers

def _minimal_result(**overrides) -> TestResult:
    """Return a TestResult with only the required fields set."""
    defaults = {
        "id": 1,
        "name": "test_example",
        "status": TestStatus.PASSED,
        "execution_time": 0.001,
    }
    defaults.update(overrides)
    return TestResult(**defaults)

class TestTestResultInstantiation(TestCase):

    # ------------------------------------------------ required fields

    def testInstantiationWithRequiredFieldsSucceeds(self):
        """
        Create a TestResult instance with only the required fields.

        Validates that providing id, name, status, and execution_time
        is sufficient to construct a valid TestResult.
        """
        result = _minimal_result()
        self.assertIsInstance(result, TestResult)

    def testIdFieldStoredCorrectly(self):
        """
        Store the id field with the value provided at construction.

        Validates that the id attribute on the created instance
        equals the value passed as a keyword argument.
        """
        result = _minimal_result(id=42)
        self.assertEqual(result.id, 42)

    def testNameFieldStoredCorrectly(self):
        """
        Store the name field with the string provided at construction.

        Validates that the name attribute on the created instance
        equals the value passed as a keyword argument.
        """
        result = _minimal_result(name="test_something")
        self.assertEqual(result.name, "test_something")

    def testStatusFieldStoredCorrectly(self):
        """
        Store the status field with the TestStatus value provided.

        Validates that the status attribute on the created instance
        equals the TestStatus member passed as a keyword argument.
        """
        result = _minimal_result(status=TestStatus.FAILED)
        self.assertEqual(result.status, TestStatus.FAILED)

    def testExecutionTimeFieldStoredCorrectly(self):
        """
        Store the execution_time field with the float provided.

        Validates that the execution_time attribute equals the value
        passed as a keyword argument.
        """
        result = _minimal_result(execution_time=1.234)
        self.assertAlmostEqual(result.execution_time, 1.234)

    # ------------------------------------------------ optional fields default to None

    def testErrorMessageDefaultsToNone(self):
        """
        Default the error_message field to None when not provided.

        Validates that omitting error_message at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.error_message)

    def testTracebackDefaultsToNone(self):
        """
        Default the traceback field to None when not provided.

        Validates that omitting traceback at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.traceback)

    def testClassNameDefaultsToNone(self):
        """
        Default the class_name field to None when not provided.

        Validates that omitting class_name at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.class_name)

    def testMethodDefaultsToNone(self):
        """
        Default the method field to None when not provided.

        Validates that omitting method at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.method)

    def testModuleDefaultsToNone(self):
        """
        Default the module field to None when not provided.

        Validates that omitting module at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.module)

    def testFilePathDefaultsToNone(self):
        """
        Default the file_path field to None when not provided.

        Validates that omitting file_path at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.file_path)

    def testDocStringDefaultsToNone(self):
        """
        Default the doc_string field to None when not provided.

        Validates that omitting doc_string at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.doc_string)

    def testExceptionDefaultsToNone(self):
        """
        Default the exception field to None when not provided.

        Validates that omitting exception at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.exception)

    def testLineNoDefaultsToNone(self):
        """
        Default the line_no field to None when not provided.

        Validates that omitting line_no at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.line_no)

    def testSourceCodeDefaultsToNone(self):
        """
        Default the source_code field to None when not provided.

        Validates that omitting source_code at construction results
        in a None value on the created instance.
        """
        result = _minimal_result()
        self.assertIsNone(result.source_code)

    # ------------------------------------------------ optional fields: explicit values

    def testErrorMessageStoresProvidedValue(self):
        """
        Store an explicit error_message string when provided.

        Validates that the error_message attribute equals the value
        supplied at construction time.
        """
        result = _minimal_result(error_message="assertion failed")
        self.assertEqual(result.error_message, "assertion failed")

    def testTracebackStoresProvidedValue(self):
        """
        Store an explicit traceback string when provided.

        Validates that the traceback attribute equals the value
        supplied at construction time.
        """
        result = _minimal_result(traceback="Traceback (most recent call last)...")
        self.assertIn("Traceback", result.traceback)

    def testClassNameStoresProvidedValue(self):
        """
        Store an explicit class_name string when provided.

        Validates that the class_name attribute equals the value
        supplied at construction time.
        """
        result = _minimal_result(class_name="MyTestClass")
        self.assertEqual(result.class_name, "MyTestClass")

    def testMethodStoresProvidedValue(self):
        """
        Store an explicit method name string when provided.

        Validates that the method attribute equals the value
        supplied at construction time.
        """
        result = _minimal_result(method="testSomething")
        self.assertEqual(result.method, "testSomething")

    def testModuleStoresProvidedValue(self):
        """
        Store an explicit module name string when provided.

        Validates that the module attribute equals the value
        supplied at construction time.
        """
        result = _minimal_result(module="tests.test_module")
        self.assertEqual(result.module, "tests.test_module")

    def testFilePathStoresProvidedValue(self):
        """
        Store an explicit file_path string when provided.

        Validates that the file_path attribute equals the value
        supplied at construction time.
        """
        result = _minimal_result(file_path="/path/to/test.py")
        self.assertEqual(result.file_path, "/path/to/test.py")

    def testLineNoStoresProvidedValue(self):
        """
        Store an explicit line_no integer when provided.

        Validates that the line_no attribute equals the integer value
        supplied at construction time.
        """
        result = _minimal_result(line_no=42)
        self.assertEqual(result.line_no, 42)

    def testSourceCodeStoresProvidedList(self):
        """
        Store an explicit source_code list of tuples when provided.

        Validates that the source_code attribute equals the list of
        (line_no, code_line) tuples supplied at construction time.
        """
        code = [(10, "    self.fail()"), (11, "")]
        result = _minimal_result(source_code=code)
        self.assertEqual(result.source_code, code)

    # ------------------------------------------------ frozen behaviour

    def testFrozenPreventsAttributeAssignment(self):
        """
        Raise FrozenInstanceError when modifying a frozen TestResult.

        Validates that the frozen=True dataclass option prevents any
        attribute from being overwritten after construction.
        """
        result = _minimal_result()
        with self.assertRaises(dataclasses.FrozenInstanceError):
            result.name = "modified"  # type: ignore[misc]

    def testFrozenPreventsAttributeDeletion(self):
        """
        Raise FrozenInstanceError when deleting an attribute from a frozen result.

        Validates that the frozen=True option also blocks attribute
        deletion attempts.
        """
        result = _minimal_result()
        with self.assertRaises(dataclasses.FrozenInstanceError):
            del result.name  # type: ignore[misc]

    # ------------------------------------------------ kw_only behaviour

    def testKwOnlyRejectsPositionalArguments(self):
        """
        Raise TypeError when positional arguments are used with TestResult.

        Validates that the kw_only=True dataclass option forces all
        fields to be passed as keyword arguments.
        """
        with self.assertRaises(TypeError):
            TestResult(1, "name", TestStatus.PASSED, 0.1)  # type: ignore[call-arg]

    # ------------------------------------------------ equality and hashing

    def testTwoIdenticalResultsAreEqual(self):
        """
        Compare two TestResult instances with identical fields as equal.

        Validates that the dataclass auto-generated __eq__ method
        considers two results equal when all fields match.
        """
        r1 = _minimal_result(id=5, name="t", execution_time=0.5)
        r2 = _minimal_result(id=5, name="t", execution_time=0.5)
        self.assertEqual(r1, r2)

    def testResultsWithDifferentStatusAreNotEqual(self):
        """
        Compare two TestResult instances with different statuses as unequal.

        Validates that changing the status field makes two otherwise
        identical results not equal.
        """
        r1 = _minimal_result(status=TestStatus.PASSED)
        r2 = _minimal_result(status=TestStatus.FAILED)
        self.assertNotEqual(r1, r2)

    def testFrozenDataclassIsHashable(self):
        """
        Confirm that a frozen TestResult instance is hashable.

        Validates that frozen dataclasses generate a __hash__ method,
        making instances usable as dictionary keys or set members.
        """
        result = _minimal_result()
        result_hash = hash(result)
        self.assertIsInstance(result_hash, int)

class TestTestResultIntegration(TestCase):

    def testAllStatusValuesCanBeStored(self):
        """
        Store every TestStatus member as the status of a TestResult.

        Validates that TestResult accepts each of the four TestStatus
        members for the required status field without error.
        """
        for status in TestStatus:
            result = TestResult(
                id=1,
                name="test",
                status=status,
                execution_time=0.0,
            )
            self.assertEqual(result.status, status)

    def testIdAcceptsNonIntegerTypes(self):
        """
        Accept any type for the id field of a TestResult.

        Validates that the id field annotation is 'Any', allowing
        strings, objects, or other types in addition to integers.
        """
        for id_val in ["uuid-abc", 99, object()]:
            result = TestResult(
                id=id_val,
                name="test",
                status=TestStatus.PASSED,
                execution_time=0.0,
            )
            self.assertEqual(result.id, id_val)

    def testExecutionTimeAcceptsZero(self):
        """
        Accept zero as a valid execution_time value for TestResult.

        Validates that zero (instant execution) is allowed for the
        required execution_time field.
        """
        result = TestResult(
            id=1,
            name="test",
            status=TestStatus.PASSED,
            execution_time=0.0,
        )
        self.assertEqual(result.execution_time, 0.0)
