from __future__ import annotations
from orionis.test import TestCase
from orionis.services.environment.enums.value_type import EnvironmentValueType
from orionis.services.environment.validators.types import ValidateTypes

# ---------------------------------------------------------------------------
# TestValidateTypesInference
# ---------------------------------------------------------------------------

class TestValidateTypesInference(TestCase):

    def testInfersStrType(self):
        """
        Infer 'str' when the value is a plain string with no type hint.

        Validates that a string value causes the validator to return the
        string 'str' as the inferred type name.
        """
        self.assertEqual(ValidateTypes(value="hello"), "str")

    def testInfersIntType(self):
        """
        Infer 'int' when the value is an integer with no type hint.

        Validates that an integer value causes the validator to return
        'int' as the inferred type name.
        """
        self.assertEqual(ValidateTypes(value=42), "int")

    def testInfersFloatType(self):
        """
        Infer 'float' when the value is a float with no type hint.

        Validates that a floating-point value causes the validator to
        return 'float' as the inferred type name.
        """
        self.assertEqual(ValidateTypes(value=3.14), "float")

    def testInfersBoolType(self):
        """
        Infer 'bool' when the value is a boolean with no type hint.

        Validates that a boolean value correctly infers 'bool' rather than
        'int', since bool is a subclass of int but type() resolves precisely.
        """
        self.assertEqual(ValidateTypes(value=True), "bool")

    def testInfersBoolFalseType(self):
        """
        Infer 'bool' when the value is False with no type hint.

        Confirms that False is recognized as bool, not int, when the type
        is inferred directly from the value.
        """
        self.assertEqual(ValidateTypes(value=False), "bool")

    def testInfersListType(self):
        """
        Infer 'list' when the value is a list with no type hint.

        Validates that a list value causes the validator to return 'list'
        as the inferred type name.
        """
        self.assertEqual(ValidateTypes(value=[1, 2, 3]), "list")

    def testInfersDictType(self):
        """
        Infer 'dict' when the value is a dictionary with no type hint.

        Validates that a dict value causes the validator to return 'dict'
        as the inferred type name.
        """
        self.assertEqual(ValidateTypes(value={"key": "val"}), "dict")

    def testInfersTupleType(self):
        """
        Infer 'tuple' when the value is a tuple with no type hint.

        Validates that a tuple value causes the validator to return 'tuple'
        as the inferred type name.
        """
        self.assertEqual(ValidateTypes(value=(1, 2)), "tuple")

    def testInfersSetType(self):
        """
        Infer 'set' when the value is a set with no type hint.

        Validates that a set value causes the validator to return 'set'
        as the inferred type name.
        """
        self.assertEqual(ValidateTypes(value={1, 2, 3}), "set")

# ---------------------------------------------------------------------------
# TestValidateTypesWithStringHint
# ---------------------------------------------------------------------------

class TestValidateTypesWithStringHint(TestCase):

    def testStringHintStr(self):
        """
        Return 'str' when a lowercase string hint 'str' is provided.

        Validates that valid string hints are normalized via the enum and
        the correct lowercase value string is returned.
        """
        result = ValidateTypes(value="hello", type_hint="str")
        self.assertEqual(result, "str")

    def testStringHintInt(self):
        """
        Return 'int' when the string hint 'int' is provided.

        Validates that the string hint is resolved through the enum member
        name lookup and the canonical value is returned.
        """
        result = ValidateTypes(value=42, type_hint="int")
        self.assertEqual(result, "int")

    def testStringHintFloat(self):
        """
        Return 'float' when the string hint 'float' is provided.

        Confirms that float-typed hints are accepted and resolved correctly.
        """
        result = ValidateTypes(value=1.5, type_hint="float")
        self.assertEqual(result, "float")

    def testStringHintBool(self):
        """
        Return 'bool' when the string hint 'bool' is provided.

        Validates that a boolean type hint resolves to the 'bool' enum value.
        """
        result = ValidateTypes(value=True, type_hint="bool")
        self.assertEqual(result, "bool")

    def testStringHintList(self):
        """
        Return 'list' when the string hint 'list' is provided.

        Validates that list type hints are accepted and the canonical value
        string is returned.
        """
        result = ValidateTypes(value=[1, 2], type_hint="list")
        self.assertEqual(result, "list")

    def testStringHintDict(self):
        """
        Return 'dict' when the string hint 'dict' is provided.

        Confirms dict type hints are resolved to the 'dict' enum value.
        """
        result = ValidateTypes(value={"a": 1}, type_hint="dict")
        self.assertEqual(result, "dict")

    def testStringHintTuple(self):
        """
        Return 'tuple' when the string hint 'tuple' is provided.

        Validates that tuple hints are forwarded through enum lookup and the
        canonical string is returned.
        """
        result = ValidateTypes(value=(1,), type_hint="tuple")
        self.assertEqual(result, "tuple")

    def testStringHintSet(self):
        """
        Return 'set' when the string hint 'set' is provided.

        Validates that set hints are resolved to the expected enum value.
        """
        result = ValidateTypes(value={1}, type_hint="set")
        self.assertEqual(result, "set")

    def testStringHintBase64(self):
        """
        Return 'base64' when the string hint 'base64' is provided.

        Confirms that the base64 hint is accepted and returned as-is from
        the enum value.
        """
        result = ValidateTypes(value="aGVsbG8=", type_hint="base64")
        self.assertEqual(result, "base64")

    def testStringHintPath(self):
        """
        Return 'path' when the string hint 'path' is provided.

        Validates that the path type hint is resolved correctly through
        the EnvironmentValueType enum.
        """
        result = ValidateTypes(value="/some/path", type_hint="path")
        self.assertEqual(result, "path")

    def testStringHintUppercaseNormalized(self):
        """
        Accept uppercase string hints and normalize them to lowercase.

        Validates that 'STR' resolves through EnvironmentValueType['STR']
        and returns the lowercase canonical value 'str'.
        """
        result = ValidateTypes(value="x", type_hint="STR")
        self.assertEqual(result, "str")

    def testStringHintMixedCaseNormalized(self):
        """
        Accept mixed-case string hints and normalize them to lowercase.

        Validates that 'Int' is uppercased to 'INT' before enum lookup so
        the canonical value 'int' is returned.
        """
        result = ValidateTypes(value=1, type_hint="Int")
        self.assertEqual(result, "int")

# ---------------------------------------------------------------------------
# TestValidateTypesWithEnumHint
# ---------------------------------------------------------------------------

class TestValidateTypesWithEnumHint(TestCase):

    def testEnumHintStr(self):
        """
        Return 'str' when EnvironmentValueType.STR is the type hint.

        Validates that enum instances are directly resolved to their value
        without going through name-based lookup.
        """
        result = ValidateTypes(value="x", type_hint=EnvironmentValueType.STR)
        self.assertEqual(result, "str")

    def testEnumHintInt(self):
        """
        Return 'int' when EnvironmentValueType.INT is the type hint.

        Confirms enum-typed hints produce the correct canonical string.
        """
        result = ValidateTypes(value=1, type_hint=EnvironmentValueType.INT)
        self.assertEqual(result, "int")

    def testEnumHintFloat(self):
        """
        Return 'float' when EnvironmentValueType.FLOAT is the type hint.

        Validates that EnvironmentValueType.FLOAT resolves to 'float'.
        """
        result = ValidateTypes(value=1.0, type_hint=EnvironmentValueType.FLOAT)
        self.assertEqual(result, "float")

    def testEnumHintBool(self):
        """
        Return 'bool' when EnvironmentValueType.BOOL is the type hint.

        Validates that the BOOL enum member resolves to the string 'bool'.
        """
        result = ValidateTypes(value=True, type_hint=EnvironmentValueType.BOOL)
        self.assertEqual(result, "bool")

    def testEnumHintList(self):
        """
        Return 'list' when EnvironmentValueType.LIST is the type hint.

        Validates that the LIST enum member resolves to the string 'list'.
        """
        result = ValidateTypes(value=[1], type_hint=EnvironmentValueType.LIST)
        self.assertEqual(result, "list")

    def testEnumHintDict(self):
        """
        Return 'dict' when EnvironmentValueType.DICT is the type hint.

        Validates that the DICT enum member resolves to the string 'dict'.
        """
        result = ValidateTypes(value={"k": 1}, type_hint=EnvironmentValueType.DICT)
        self.assertEqual(result, "dict")

    def testEnumHintTuple(self):
        """
        Return 'tuple' when EnvironmentValueType.TUPLE is the type hint.

        Validates that the TUPLE enum member resolves to the string 'tuple'.
        """
        result = ValidateTypes(value=(1,), type_hint=EnvironmentValueType.TUPLE)
        self.assertEqual(result, "tuple")

    def testEnumHintSet(self):
        """
        Return 'set' when EnvironmentValueType.SET is the type hint.

        Validates that the SET enum member resolves to the string 'set'.
        """
        result = ValidateTypes(value={1}, type_hint=EnvironmentValueType.SET)
        self.assertEqual(result, "set")

    def testEnumHintBase64(self):
        """
        Return 'base64' when EnvironmentValueType.BASE64 is the type hint.

        Validates that the BASE64 enum member resolves to the string 'base64'.
        """
        result = ValidateTypes(value="aGk=", type_hint=EnvironmentValueType.BASE64)
        self.assertEqual(result, "base64")

    def testEnumHintPath(self):
        """
        Return 'path' when EnvironmentValueType.PATH is the type hint.

        Validates that the PATH enum member resolves to the string 'path'.
        """
        result = ValidateTypes(value="/tmp", type_hint=EnvironmentValueType.PATH)
        self.assertEqual(result, "path")

# ---------------------------------------------------------------------------
# TestValidateTypesTypeError
# ---------------------------------------------------------------------------

class TestValidateTypesTypeError(TestCase):

    def testRaisesTypeErrorForBytes(self):
        """
        Raise TypeError when bytes are passed as the value.

        Validates that bytes objects are not in the allowed type set and
        cause an appropriate TypeError to be raised.
        """
        with self.assertRaises(TypeError):
            ValidateTypes(value=b"hello")

    def testRaisesTypeErrorForNone(self):
        """
        Raise TypeError when None is passed as the value.

        Confirms that None is not a supported value type and causes a
        TypeError with a descriptive message.
        """
        with self.assertRaises(TypeError):
            ValidateTypes(value=None)

    def testRaisesTypeErrorForObject(self):
        """
        Raise TypeError when an arbitrary object instance is the value.

        Validates that custom class instances are rejected as unsupported
        value types.
        """
        with self.assertRaises(TypeError):
            ValidateTypes(value=object())

    def testRaisesTypeErrorForInvalidTypeHintType(self):
        """
        Raise TypeError when type_hint is neither a string nor EnvironmentValueType.

        Validates that passing an integer as type_hint is caught before enum
        lookup and a TypeError is raised.
        """
        with self.assertRaises(TypeError):
            ValidateTypes(value="hello", type_hint=42)

    def testRaisesTypeErrorForListTypeHint(self):
        """
        Raise TypeError when a list is passed as the type_hint argument.

        Confirms that non-string, non-enum type hints raise a TypeError
        with a message that identifies the actual received type.
        """
        with self.assertRaises(TypeError):
            ValidateTypes(value="x", type_hint=["str"])

    def testTypeErrorMessageContainsTypeName(self):
        """
        Include the unsupported type name in the TypeError message.

        Ensures the error message is actionable for debugging by reporting
        the exact type that was rejected.
        """
        try:
            ValidateTypes(value=b"data")
            self.fail("Expected TypeError was not raised")
        except TypeError as exc:
            self.assertIn("bytes", str(exc))

# ---------------------------------------------------------------------------
# TestValidateTypesRuntimeError
# ---------------------------------------------------------------------------

class TestValidateTypesRuntimeError(TestCase):

    def testRaisesRuntimeErrorForUnknownStringHint(self):
        """
        Raise RuntimeError when the string hint has no matching enum member.

        Validates that a hint like 'unknown' fails the EnvironmentValueType
        key lookup and a RuntimeError is raised instead of a KeyError.
        """
        with self.assertRaises(RuntimeError):
            ValidateTypes(value="hello", type_hint="unknown")

    def testRaisesRuntimeErrorForNumericStringHint(self):
        """
        Raise RuntimeError when a numeric string is used as the hint.

        Confirms that strings that do not correspond to any enum member name
        are rejected with a RuntimeError.
        """
        with self.assertRaises(RuntimeError):
            ValidateTypes(value=42, type_hint="123")

    def testRuntimeErrorMessageContainsAllowedTypes(self):
        """
        Include the list of allowed types in the RuntimeError message.

        Validates that the error message is informative and helps the caller
        identify valid type hint values to use instead.
        """
        try:
            ValidateTypes(value="x", type_hint="notavalidtype")
            self.fail("Expected RuntimeError was not raised")
        except RuntimeError as exc:
            self.assertIn("str", str(exc))

# ---------------------------------------------------------------------------
# TestValidateTypesNoneHint
# ---------------------------------------------------------------------------

class TestValidateTypesNoneHint(TestCase):

    def testNoneHintFallsBackToInference(self):
        """
        Fall back to type inference when type_hint is None.

        Validates that explicitly passing type_hint=None produces the same
        result as omitting the argument entirely.
        """
        result = ValidateTypes(value="hello", type_hint=None)
        self.assertEqual(result, "str")

    def testNoneHintInfersInt(self):
        """
        Fall back to 'int' inference when type_hint=None and value is int.

        Confirms that None is treated as absent and the value type drives
        the returned type string.
        """
        result = ValidateTypes(value=10, type_hint=None)
        self.assertEqual(result, "int")

# ---------------------------------------------------------------------------
# TestValidateTypesReturnType
# ---------------------------------------------------------------------------

class TestValidateTypesReturnType(TestCase):

    def testAlwaysReturnsString(self):
        """
        Confirm that the return value is always a string instance.

        Validates the return type contract for all inferred and hinted
        cases using a representative sample.
        """
        cases = [
            ValidateTypes(value="x"),
            ValidateTypes(value=1),
            ValidateTypes(value=1.0),
            ValidateTypes(value=True),
            ValidateTypes(value=[]),
            ValidateTypes(value={}),
            ValidateTypes(value=()),
            ValidateTypes(value=set()),
        ]
        for result in cases:
            self.assertIsInstance(result, str)
