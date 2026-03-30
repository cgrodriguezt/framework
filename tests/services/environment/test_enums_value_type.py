from __future__ import annotations
from enum import Enum
from orionis.test import TestCase
from orionis.services.environment.enums.value_type import EnvironmentValueType

# ---------------------------------------------------------------------------
# TestEnvironmentValueTypeMembers
# ---------------------------------------------------------------------------

class TestEnvironmentValueTypeMembers(TestCase):

    def testIsEnumSubclass(self):
        """
        Confirm that EnvironmentValueType is a subclass of Enum.

        Validates that the class follows the standard enum contract so it
        can be used with enum-specific APIs such as iteration and lookup.
        """
        self.assertTrue(issubclass(EnvironmentValueType, Enum))

    def testTotalMemberCount(self):
        """
        Verify that exactly ten members are defined.

        Ensures that the enum covers the complete set of supported type
        hints without unexpected additions or omissions.
        """
        self.assertEqual(len(EnvironmentValueType), 10)

    def testMemberBase64Exists(self):
        """
        Confirm that the BASE64 member is defined.

        Checks that the enum exposes Base64 as a supported type hint.
        """
        self.assertIn("BASE64", EnvironmentValueType.__members__)

    def testMemberPathExists(self):
        """
        Confirm that the PATH member is defined.

        Checks that the enum exposes the file system path type.
        """
        self.assertIn("PATH", EnvironmentValueType.__members__)

    def testMemberStrExists(self):
        """
        Confirm that the STR member is defined.

        Checks that the enum provides the string type hint.
        """
        self.assertIn("STR", EnvironmentValueType.__members__)

    def testMemberIntExists(self):
        """
        Confirm that the INT member is defined.

        Checks that the enum provides the integer type hint.
        """
        self.assertIn("INT", EnvironmentValueType.__members__)

    def testMemberFloatExists(self):
        """
        Confirm that the FLOAT member is defined.

        Checks that the enum provides the floating-point type hint.
        """
        self.assertIn("FLOAT", EnvironmentValueType.__members__)

    def testMemberBoolExists(self):
        """
        Confirm that the BOOL member is defined.

        Checks that the enum provides the boolean type hint.
        """
        self.assertIn("BOOL", EnvironmentValueType.__members__)

    def testMemberListExists(self):
        """
        Confirm that the LIST member is defined.

        Checks that the enum provides the list type hint.
        """
        self.assertIn("LIST", EnvironmentValueType.__members__)

    def testMemberDictExists(self):
        """
        Confirm that the DICT member is defined.

        Checks that the enum provides the dictionary type hint.
        """
        self.assertIn("DICT", EnvironmentValueType.__members__)

    def testMemberTupleExists(self):
        """
        Confirm that the TUPLE member is defined.

        Checks that the enum provides the tuple type hint.
        """
        self.assertIn("TUPLE", EnvironmentValueType.__members__)

    def testMemberSetExists(self):
        """
        Confirm that the SET member is defined.

        Checks that the enum provides the set type hint.
        """
        self.assertIn("SET", EnvironmentValueType.__members__)

# ---------------------------------------------------------------------------
# TestEnvironmentValueTypeValues
# ---------------------------------------------------------------------------

class TestEnvironmentValueTypeValues(TestCase):

    def testBase64Value(self):
        """
        Verify that BASE64 holds the string value 'base64'.

        Ensures the serialized form of the type hint matches the expected
        lowercase string used in environment variable prefixes.
        """
        self.assertEqual(EnvironmentValueType.BASE64.value, "base64")

    def testPathValue(self):
        """
        Verify that PATH holds the string value 'path'.

        Ensures the serialized form matches the prefix used by the caster.
        """
        self.assertEqual(EnvironmentValueType.PATH.value, "path")

    def testStrValue(self):
        """
        Verify that STR holds the string value 'str'.

        Ensures the serialized form matches the prefix used by the caster.
        """
        self.assertEqual(EnvironmentValueType.STR.value, "str")

    def testIntValue(self):
        """
        Verify that INT holds the string value 'int'.

        Ensures the serialized form matches the prefix used by the caster.
        """
        self.assertEqual(EnvironmentValueType.INT.value, "int")

    def testFloatValue(self):
        """
        Verify that FLOAT holds the string value 'float'.

        Ensures the serialized form matches the prefix used by the caster.
        """
        self.assertEqual(EnvironmentValueType.FLOAT.value, "float")

    def testBoolValue(self):
        """
        Verify that BOOL holds the string value 'bool'.

        Ensures the serialized form matches the prefix used by the caster.
        """
        self.assertEqual(EnvironmentValueType.BOOL.value, "bool")

    def testListValue(self):
        """
        Verify that LIST holds the string value 'list'.

        Ensures the serialized form matches the prefix used by the caster.
        """
        self.assertEqual(EnvironmentValueType.LIST.value, "list")

    def testDictValue(self):
        """
        Verify that DICT holds the string value 'dict'.

        Ensures the serialized form matches the prefix used by the caster.
        """
        self.assertEqual(EnvironmentValueType.DICT.value, "dict")

    def testTupleValue(self):
        """
        Verify that TUPLE holds the string value 'tuple'.

        Ensures the serialized form matches the prefix used by the caster.
        """
        self.assertEqual(EnvironmentValueType.TUPLE.value, "tuple")

    def testSetValue(self):
        """
        Verify that SET holds the string value 'set'.

        Ensures the serialized form matches the prefix used by the caster.
        """
        self.assertEqual(EnvironmentValueType.SET.value, "set")

# ---------------------------------------------------------------------------
# TestEnvironmentValueTypeLookup
# ---------------------------------------------------------------------------

class TestEnvironmentValueTypeLookup(TestCase):

    def testLookupByValueBase64(self):
        """
        Retrieve the BASE64 member by its string value.

        Validates that EnvironmentValueType('base64') resolves to the
        correct enum member.
        """
        self.assertIs(EnvironmentValueType("base64"), EnvironmentValueType.BASE64)

    def testLookupByValueStr(self):
        """
        Retrieve the STR member by its string value.

        Validates that EnvironmentValueType('str') resolves to the correct
        enum member.
        """
        self.assertIs(EnvironmentValueType("str"), EnvironmentValueType.STR)

    def testLookupByValueInt(self):
        """
        Retrieve the INT member by its string value.

        Validates that EnvironmentValueType('int') resolves to the correct
        enum member.
        """
        self.assertIs(EnvironmentValueType("int"), EnvironmentValueType.INT)

    def testLookupByValueFloat(self):
        """
        Retrieve the FLOAT member by its string value.

        Validates that EnvironmentValueType('float') resolves to the correct
        enum member.
        """
        self.assertIs(EnvironmentValueType("float"), EnvironmentValueType.FLOAT)

    def testLookupByValueBool(self):
        """
        Retrieve the BOOL member by its string value.

        Validates that EnvironmentValueType('bool') resolves to the correct
        enum member.
        """
        self.assertIs(EnvironmentValueType("bool"), EnvironmentValueType.BOOL)

    def testLookupByValueList(self):
        """
        Retrieve the LIST member by its string value.

        Validates that EnvironmentValueType('list') resolves to the correct
        enum member.
        """
        self.assertIs(EnvironmentValueType("list"), EnvironmentValueType.LIST)

    def testLookupByValueDict(self):
        """
        Retrieve the DICT member by its string value.

        Validates that EnvironmentValueType('dict') resolves to the correct
        enum member.
        """
        self.assertIs(EnvironmentValueType("dict"), EnvironmentValueType.DICT)

    def testLookupByValueTuple(self):
        """
        Retrieve the TUPLE member by its string value.

        Validates that EnvironmentValueType('tuple') resolves to the correct
        enum member.
        """
        self.assertIs(EnvironmentValueType("tuple"), EnvironmentValueType.TUPLE)

    def testLookupByValueSet(self):
        """
        Retrieve the SET member by its string value.

        Validates that EnvironmentValueType('set') resolves to the correct
        enum member.
        """
        self.assertIs(EnvironmentValueType("set"), EnvironmentValueType.SET)

    def testLookupByValuePath(self):
        """
        Retrieve the PATH member by its string value.

        Validates that EnvironmentValueType('path') resolves to the correct
        enum member.
        """
        self.assertIs(EnvironmentValueType("path"), EnvironmentValueType.PATH)

    def testLookupInvalidValueRaisesError(self):
        """
        Raise ValueError when an unsupported string is used as a lookup key.

        Confirms that the enum does not silently accept unrecognized values
        and raises the standard Python enum error.
        """
        with self.assertRaises(ValueError):
            EnvironmentValueType("unknown")

# ---------------------------------------------------------------------------
# TestEnvironmentValueTypeUniqueness
# ---------------------------------------------------------------------------

class TestEnvironmentValueTypeUniqueness(TestCase):

    def testAllValuesAreUnique(self):
        """
        Confirm that no two members share the same string value.

        Ensures there are no accidental duplicate values that would cause
        enum lookup ambiguity.
        """
        values = [m.value for m in EnvironmentValueType]
        self.assertEqual(len(values), len(set(values)))

    def testAllValuesAreStrings(self):
        """
        Confirm that every member value is a plain string.

        Validates the type contract expected by the caster and other
        components that consume enum values as strings.
        """
        for member in EnvironmentValueType:
            self.assertIsInstance(member.value, str)

    def testAllValuesAreLowercase(self):
        """
        Confirm that every member value is entirely lowercase.

        The caster normalizes type hints to lowercase before lookup, so
        enum values must follow the same convention.
        """
        for member in EnvironmentValueType:
            self.assertEqual(member.value, member.value.lower())

    def testIterationYieldsAllTenMembers(self):
        """
        Verify that iterating the enum yields exactly ten members.

        Provides a secondary coverage check that complements the
        testTotalMemberCount test using the iteration protocol.
        """
        members = list(EnvironmentValueType)
        self.assertEqual(len(members), 10)
