from __future__ import annotations
from pathlib import Path
from orionis.test import TestCase
from orionis.services.environment.dynamic.caster import EnvironmentCaster
from orionis.services.environment.enums.value_type import EnvironmentValueType

# ---------------------------------------------------------------------------
# TestEnvironmentCasterSupportedTypes
# ---------------------------------------------------------------------------

class TestEnvironmentCasterSupportedTypes(TestCase):

    def testSupportedTypesReturnsSet(self):
        """
        Verify that supportedTypes returns a set instance.

        Checks that the static method's return type is exactly ``set``.
        """
        result = EnvironmentCaster.supportedTypes()
        self.assertIsInstance(result, set)

    def testSupportedTypesContainsExpectedValues(self):
        """
        Verify that supportedTypes contains all expected type name strings.

        Ensures every EnvironmentValueType member's value is represented
        in the returned set.
        """
        result = EnvironmentCaster.supportedTypes()
        expected = {e.value for e in EnvironmentValueType}
        self.assertEqual(result, expected)

# ---------------------------------------------------------------------------
# TestEnvironmentCasterInit
# ---------------------------------------------------------------------------

class TestEnvironmentCasterInit(TestCase):

    def testInitWithPlainString(self):
        """
        Initialize with a plain string and return it unchanged via get().

        Confirms that a string with no recognized type-hint prefix is stored
        as the raw value and returned without conversion.
        """
        self.assertEqual(EnvironmentCaster("hello").get(), "hello")

    def testInitWithTypedString(self):
        """
        Initialize with a typed string and dispatch to the correct parser.

        Confirms that 'int:42' extracts the type hint and converts the value
        to the expected integer.
        """
        self.assertEqual(EnvironmentCaster("int:42").get(), 42)

    def testInitWithLeadingWhitespaceAndTypeHint(self):
        """
        Initialize with leading whitespace before the typed string.

        Verifies that lstrip normalizes the input so the type hint is still
        detected and the value converted correctly.
        """
        self.assertEqual(EnvironmentCaster("  int:42").get(), 42)

    def testInitWithUppercaseTypeHint(self):
        """
        Initialize with an uppercase type hint prefix.

        Ensures the parser is case-insensitive when extracting type hints
        and converts the value as if the hint were lowercase.
        """
        self.assertEqual(EnvironmentCaster("INT:42").get(), 42)

    def testInitWithInvalidTypeHintBeforeColon(self):
        """
        Initialize with an unrecognized prefix and treat the input as raw.

        Confirms that the entire string is kept as the raw value when the
        prefix before the colon is not a supported type hint.
        """
        self.assertEqual(EnvironmentCaster("invalid:42").get(), "invalid:42")

    def testInitWithNonStringInt(self):
        """
        Initialize with an integer and store it as raw value unchanged.

        Ensures that non-string inputs bypass type hint detection and are
        passed through get() without any conversion.
        """
        self.assertEqual(EnvironmentCaster(99).get(), 99)

    def testInitWithNonStringPath(self):
        """
        Initialize with a Path object and store it as raw value unchanged.

        Ensures that Path instances bypass string-based type hint detection
        and are returned as-is by get().
        """
        p = Path("/some/dir")
        self.assertEqual(EnvironmentCaster(p).get(), p)

    def testInitWithEmptyValueAfterColonRaisesError(self):
        """
        Raise an error when get() is called after init with an empty value.

        Confirms that 'str:' sets value_raw to None and that attempting to
        process a None value raises ValueError.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("str:").get()

    def testInitWithColonInValuePreservesRemainder(self):
        """
        Split only at the first colon and preserve subsequent colons as value.

        Validates that 'str:hello:world' stores 'hello:world' as the value
        and returns it unchanged through get().
        """
        self.assertEqual(EnvironmentCaster("str:hello:world").get(), "hello:world")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetRaw
# -----------------------------------------------
class TestEnvironmentCasterGetRaw(TestCase):

    def testGetRawStringNoTypeHint(self):
        """
        Return a plain string unchanged when no type hint is present.

        Confirms that strings without a recognized type-hint prefix are
        returned exactly as provided.
        """
        self.assertEqual(EnvironmentCaster("hello").get(), "hello")

    def testGetRawNonString(self):
        """
        Return a non-string raw value unchanged when no type hint is set.

        Checks that integer inputs pass through get() without modification.
        """
        self.assertEqual(EnvironmentCaster(42).get(), 42)

    def testGetRawUnrecognizedTypeHint(self):
        """
        Return the entire string unchanged when the type hint is unrecognized.

        Validates that unsupported prefix strings are not processed or split.
        """
        self.assertEqual(EnvironmentCaster("foo:bar").get(), "foo:bar")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetStr
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetStr(TestCase):

    def testGetStrBasic(self):
        """
        Return the value from a str-typed input with no excess whitespace.

        Checks basic parsing of the 'str:' prefix for a simple string.
        """
        self.assertEqual(EnvironmentCaster("str:hello").get(), "hello")

    def testGetStrWithLeadingWhitespace(self):
        """
        Strip leading whitespace from the value portion of a str-typed input.

        Validates that both __init__ lstrip and __parseStr lstrip cooperate
        to remove any leading whitespace from the value.
        """
        self.assertEqual(
            EnvironmentCaster("str:  hello world").get(),
            "hello world",
        )

    def testGetStrWithColonInValue(self):
        """
        Preserve colons within the value portion after the first delimiter.

        Ensures the first colon is used as the type-hint delimiter only, so
        subsequent colons remain intact in the returned string.
        """
        self.assertEqual(
            EnvironmentCaster("str:hello:world").get(),
            "hello:world",
        )

    def testGetStrEmptyValueRaisesError(self):
        """
        Raise ValueError when the str type hint is followed by an empty value.

        Confirms that an empty value part sets value_raw to None, which
        triggers a ValueError when get() attempts to process it.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("str:").get()

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetInt
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetInt(TestCase):

    def testGetIntBasic(self):
        """
        Convert a well-formed int-typed string to an integer.

        Validates standard integer parsing through the 'int:' prefix.
        """
        self.assertEqual(EnvironmentCaster("int:42").get(), 42)

    def testGetIntNegative(self):
        """
        Convert a negative int-typed string to a negative integer.

        Ensures the parser handles negative integer literals correctly.
        """
        self.assertEqual(EnvironmentCaster("int:-7").get(), -7)

    def testGetIntWithWhitespace(self):
        """
        Parse an integer value that has surrounding whitespace.

        Confirms that strip() inside __parseInt handles extra spaces around
        the numeric value.
        """
        self.assertEqual(EnvironmentCaster("int: 42 ").get(), 42)

    def testGetIntInvalidRaisesError(self):
        """
        Raise ValueError when the int-typed value is not a valid integer.

        Validates that non-numeric strings trigger the appropriate error
        during parsing.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("int:abc").get()

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetFloat
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetFloat(TestCase):

    def testGetFloatBasic(self):
        """
        Convert a well-formed float-typed string to a floating-point number.

        Validates standard float parsing through the 'float:' prefix.
        """
        self.assertAlmostEqual(EnvironmentCaster("float:3.14").get(), 3.14)

    def testGetFloatNegative(self):
        """
        Convert a negative float-typed string to a negative float.

        Ensures the parser handles negative floating-point literals.
        """
        self.assertAlmostEqual(EnvironmentCaster("float:-1.5").get(), -1.5)

    def testGetFloatFromIntegerString(self):
        """
        Promote an integer string to float under the float prefix.

        Confirms that integer-like strings are returned as float instances
        rather than ints.
        """
        result = EnvironmentCaster("float:10").get()
        self.assertIsInstance(result, float)
        self.assertEqual(result, 10.0)

    def testGetFloatInvalidRaisesError(self):
        """
        Raise ValueError when the float-typed value is not numeric.

        Validates that non-numeric strings trigger the appropriate error.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("float:abc").get()

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetBool
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetBool(TestCase):

    def testGetBoolTrue(self):
        """
        Recognize 'true' as boolean True.

        Validates that the lowercase 'true' literal maps to Python True.
        """
        self.assertIs(EnvironmentCaster("bool:true").get(), True)

    def testGetBoolFalse(self):
        """
        Recognize 'false' as boolean False.

        Validates that the lowercase 'false' literal maps to Python False.
        """
        self.assertIs(EnvironmentCaster("bool:false").get(), False)

    def testGetBoolOne(self):
        """
        Recognize '1' as boolean True.

        Validates the numeric truthy representation.
        """
        self.assertIs(EnvironmentCaster("bool:1").get(), True)

    def testGetBoolZero(self):
        """
        Recognize '0' as boolean False.

        Validates the numeric falsy representation.
        """
        self.assertIs(EnvironmentCaster("bool:0").get(), False)

    def testGetBoolYes(self):
        """
        Recognize 'yes' as boolean True.

        Validates the 'yes' string representation.
        """
        self.assertIs(EnvironmentCaster("bool:yes").get(), True)

    def testGetBoolNo(self):
        """
        Recognize 'no' as boolean False.

        Validates the 'no' string representation.
        """
        self.assertIs(EnvironmentCaster("bool:no").get(), False)

    def testGetBoolOn(self):
        """
        Recognize 'on' as boolean True.

        Validates the 'on' string representation.
        """
        self.assertIs(EnvironmentCaster("bool:on").get(), True)

    def testGetBoolOff(self):
        """
        Recognize 'off' as boolean False.

        Validates the 'off' string representation.
        """
        self.assertIs(EnvironmentCaster("bool:off").get(), False)

    def testGetBoolEnabled(self):
        """
        Recognize 'enabled' as boolean True.

        Validates the 'enabled' string representation.
        """
        self.assertIs(EnvironmentCaster("bool:enabled").get(), True)

    def testGetBoolDisabled(self):
        """
        Recognize 'disabled' as boolean False.

        Validates the 'disabled' string representation.
        """
        self.assertIs(EnvironmentCaster("bool:disabled").get(), False)

    def testGetBoolUppercaseValueIsCaseInsensitive(self):
        """
        Recognize uppercase 'TRUE' as boolean True.

        Validates that the bool parser lowercases the value before matching,
        making the comparison case-insensitive.
        """
        self.assertIs(EnvironmentCaster("bool:TRUE").get(), True)

    def testGetBoolInvalidRaisesError(self):
        """
        Raise ValueError when the bool-typed value is not a recognized token.

        Confirms that arbitrary strings that do not map to a known boolean
        representation trigger the appropriate error.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("bool:maybe").get()

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetList
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetList(TestCase):

    def testGetListBasic(self):
        """
        Parse a list-typed string into a Python list of integers.

        Validates standard list parsing through the 'list:' prefix.
        """
        self.assertEqual(EnvironmentCaster("list:[1, 2, 3]").get(), [1, 2, 3])

    def testGetListOfStrings(self):
        """
        Parse a list of string literals from a list-typed input.

        Confirms that string elements inside a list literal are parsed
        correctly via ast.literal_eval.
        """
        self.assertEqual(
            EnvironmentCaster("list:['a', 'b', 'c']").get(),
            ["a", "b", "c"],
        )

    def testGetListEmpty(self):
        """
        Parse an empty list literal from a list-typed input.

        Verifies that '[]' is correctly evaluated to an empty Python list.
        """
        self.assertEqual(EnvironmentCaster("list:[]").get(), [])

    def testGetListInvalidRaisesError(self):
        """
        Raise an error when the list-typed value is not a valid list literal.

        Validates that non-list strings trigger an error during ast evaluation.
        """
        with self.assertRaises((ValueError, TypeError)):
            EnvironmentCaster("list:notalist").get()

    def testGetListWrongTypeRaisesError(self):
        """
        Raise an error when the evaluated literal is a tuple, not a list.

        Confirms that type checking after evaluation rejects non-list types
        and propagates the failure as ValueError or TypeError.
        """
        with self.assertRaises((ValueError, TypeError)):
            EnvironmentCaster("list:(1, 2, 3)").get()

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetDict
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetDict(TestCase):

    def testGetDictBasic(self):
        """
        Parse a dict-typed string into a Python dictionary.

        Validates standard dictionary parsing through the 'dict:' prefix.
        """
        self.assertEqual(
            EnvironmentCaster("dict:{'a': 1}").get(),
            {"a": 1},
        )

    def testGetDictEmpty(self):
        """
        Parse an empty dict literal from a dict-typed input.

        Verifies that '{}' is correctly evaluated to an empty Python dict.
        """
        self.assertEqual(EnvironmentCaster("dict:{}").get(), {})

    def testGetDictInvalidRaisesError(self):
        """
        Raise ValueError when the dict-typed value is not a valid dict literal.

        Validates that non-dict strings trigger an error during parsing.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("dict:notadict").get()

    def testGetDictWrongTypeRaisesError(self):
        """
        Raise ValueError when the evaluated literal is a list, not a dict.

        Confirms that type checking after evaluation rejects non-dict types
        and normalizes the failure to ValueError.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("dict:[1, 2]").get()

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetTuple
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetTuple(TestCase):

    def testGetTupleBasic(self):
        """
        Parse a tuple-typed string into a Python tuple.

        Validates standard tuple parsing through the 'tuple:' prefix.
        """
        self.assertEqual(
            EnvironmentCaster("tuple:(1, 2, 3)").get(),
            (1, 2, 3),
        )

    def testGetTupleEmpty(self):
        """
        Parse an empty tuple literal from a tuple-typed input.

        Verifies that '()' is correctly evaluated to an empty Python tuple.
        """
        self.assertEqual(EnvironmentCaster("tuple:()").get(), ())

    def testGetTupleInvalidRaisesError(self):
        """
        Raise ValueError when the tuple-typed value is not a valid literal.

        Validates that non-tuple strings trigger an error during parsing.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("tuple:notatuple").get()

    def testGetTupleWrongTypeRaisesError(self):
        """
        Raise ValueError when the evaluated literal is a list, not a tuple.

        Confirms that type checking after evaluation rejects non-tuple types
        and normalizes the failure to ValueError.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("tuple:[1, 2]").get()

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetSet
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetSet(TestCase):

    def testGetSetBasic(self):
        """
        Parse a set-typed string into a Python set.

        Validates standard set parsing through the 'set:' prefix using a
        non-empty set literal supported by ast.literal_eval.
        """
        self.assertEqual(
            EnvironmentCaster("set:{1, 2, 3}").get(),
            {1, 2, 3},
        )

    def testGetSetInvalidRaisesError(self):
        """
        Raise ValueError when the set-typed value is not a valid set literal.

        Validates that non-set strings trigger an error during parsing.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("set:notaset").get()

    def testGetSetEmptyBracesRaisesError(self):
        """
        Raise ValueError when '{}' is provided for a set-typed value.

        Confirms that empty braces evaluate to a dict in Python, causing the
        isinstance(parsed, set) check to fail and raise ValueError.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("set:{}").get()

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetBase64
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetBase64(TestCase):

    def testGetBase64ValidEncoded(self):
        """
        Decode a valid Base64 string to its original UTF-8 value.

        Confirms that the standard base64 encoding of 'hello' (aGVsbG8=)
        is correctly decoded back to the string 'hello'.
        """
        result = EnvironmentCaster("base64:aGVsbG8=").get()
        self.assertEqual(result, "hello")

    def testGetBase64InvalidRaisesError(self):
        """
        Raise ValueError when the base64-typed value has invalid characters.

        Validates that malformed Base64 input (non-alphabet characters) is
        rejected and triggers an appropriate ValueError.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("base64:!@#$").get()

# ---------------------------------------------------------------------------
# TestEnvironmentCasterGetPath
# ---------------------------------------------------------------------------

class TestEnvironmentCasterGetPath(TestCase):

    def testGetPathForwardSlashes(self):
        """
        Return a normalized POSIX path string from a path-typed input.

        Validates that a forward-slash path is returned exactly as a POSIX
        string without any transformation.
        """
        result = EnvironmentCaster("path:/home/user/file.txt").get()
        self.assertEqual(result, "/home/user/file.txt")

    def testGetPathBackslashesNormalized(self):
        """
        Normalize backslashes to forward slashes in path-typed values.

        Verifies that Windows-style separators in a relative path are
        converted to POSIX forward slashes.
        """
        result = EnvironmentCaster(r"path:relative\subdir").get()
        self.assertEqual(result, "relative/subdir")

    def testGetPathRelativePreserved(self):
        """
        Return a relative path as a POSIX string without resolving it.

        Confirms that __parsePath does not convert relative paths to
        absolute paths — it only normalizes separators.
        """
        result = EnvironmentCaster("path:some/relative/path").get()
        self.assertEqual(result, "some/relative/path")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToStr
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToStr(TestCase):

    def testToStr(self):
        """
        Serialize a string value with the 'str' type hint prefix.

        Validates that to('str') produces the 'str:<value>' format.
        """
        self.assertEqual(EnvironmentCaster("hello").to("str"), "str:hello")

    def testToStrWithEnumHint(self):
        """
        Serialize a string using an EnvironmentValueType enum as the hint.

        Confirms that enum hints are accepted and produce the same result
        as the equivalent string hint.
        """
        result = EnvironmentCaster("hello").to(EnvironmentValueType.STR)
        self.assertEqual(result, "str:hello")

    def testToStrRaisesErrorForNonString(self):
        """
        Raise ValueError when a non-string value is serialized with str hint.

        Validates that the type enforcement in __toStr is propagated through
        to() as ValueError.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster(42).to("str")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToInt
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToInt(TestCase):

    def testToIntFromInt(self):
        """
        Serialize an integer value with the 'int' type hint prefix.

        Validates that to('int') produces the 'int:<value>' format.
        """
        self.assertEqual(EnvironmentCaster(42).to("int"), "int:42")

    def testToIntFromString(self):
        """
        Serialize a numeric string value with the 'int' type hint prefix.

        Confirms that string representations of integers are converted and
        serialized correctly.
        """
        self.assertEqual(EnvironmentCaster("42").to("int"), "int:42")

    def testToIntFromFloat(self):
        """
        Serialize a float value truncated to int under the 'int' hint.

        Validates that float values representable as integers are accepted
        and the fractional part is discarded.
        """
        self.assertEqual(EnvironmentCaster(3.0).to("int"), "int:3")

    def testToIntInvalidStringRaisesError(self):
        """
        Raise ValueError when a non-numeric string is serialized as int.

        Confirms that conversion errors inside __toInt are propagated
        correctly as ValueError.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("abc").to("int")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToFloat
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToFloat(TestCase):

    def testToFloatFromFloat(self):
        """
        Serialize a float value with the 'float' type hint prefix.

        Validates that to('float') produces the 'float:<value>' format.
        """
        self.assertEqual(EnvironmentCaster(3.14).to("float"), "float:3.14")

    def testToFloatFromString(self):
        """
        Serialize a numeric string value with the 'float' type hint prefix.

        Confirms that string representations of floats are converted and
        serialized correctly.
        """
        self.assertEqual(EnvironmentCaster("3.14").to("float"), "float:3.14")

    def testToFloatFromInt(self):
        """
        Serialize an integer value promoted to float under the 'float' hint.

        Validates that integer inputs are promoted to float and the resulting
        serialized string reflects the float representation.
        """
        self.assertEqual(EnvironmentCaster(10).to("float"), "float:10.0")

    def testToFloatInvalidStringRaisesError(self):
        """
        Raise ValueError when a non-numeric string is serialized as float.

        Confirms that conversion errors inside __toFloat are propagated
        correctly as ValueError.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("abc").to("float")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToBool
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToBool(TestCase):

    def testToBoolFromTrue(self):
        """
        Serialize Python True to the 'bool:true' string.

        Validates that the boolean True literal is lowercased in the output.
        """
        self.assertEqual(EnvironmentCaster(True).to("bool"), "bool:true")

    def testToBoolFromFalse(self):
        """
        Serialize Python False to the 'bool:false' string.

        Validates that the boolean False literal is lowercased in the output.
        """
        self.assertEqual(EnvironmentCaster(False).to("bool"), "bool:false")

    def testToBoolFromTrueString(self):
        """
        Serialize a recognized truthy string to 'bool:true'.

        Confirms that 'yes' is normalized to the canonical 'true' form.
        """
        self.assertEqual(EnvironmentCaster("yes").to("bool"), "bool:true")

    def testToBoolFromFalseString(self):
        """
        Serialize a recognized falsy string to 'bool:false'.

        Confirms that 'no' is normalized to the canonical 'false' form.
        """
        self.assertEqual(EnvironmentCaster("no").to("bool"), "bool:false")

    def testToBoolFromNumericOne(self):
        """
        Serialize the string '1' to 'bool:true'.

        Validates that the numeric truthy string representation is accepted
        and normalized correctly.
        """
        self.assertEqual(EnvironmentCaster("1").to("bool"), "bool:true")

    def testToBoolInvalidStringRaisesError(self):
        """
        Raise ValueError when an unrecognized string is serialized as bool.

        Confirms that invalid boolean strings trigger the appropriate error
        inside __toBool, propagated as ValueError through to().
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("maybe").to("bool")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToList
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToList(TestCase):

    def testToList(self):
        """
        Serialize a list value with the 'list' type hint prefix.

        Validates that to('list') produces the 'list:<repr>' format using
        the repr of the list.
        """
        self.assertEqual(EnvironmentCaster([1, 2, 3]).to("list"), "list:[1, 2, 3]")

    def testToListRaisesErrorForNonList(self):
        """
        Raise ValueError when a non-list value is serialized with list hint.

        Confirms that type enforcement in __toList is propagated as ValueError
        through to().
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("hello").to("list")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToDict
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToDict(TestCase):

    def testToDict(self):
        """
        Serialize a dict value with the 'dict' type hint prefix.

        Validates that to('dict') produces the 'dict:<repr>' format using
        the repr of the dictionary.
        """
        self.assertEqual(
            EnvironmentCaster({"a": 1}).to("dict"),
            "dict:{'a': 1}",
        )

    def testToDictRaisesErrorForNonDict(self):
        """
        Raise ValueError when a non-dict value is serialized with dict hint.

        Confirms that type enforcement in __toDict is propagated as ValueError
        through to().
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("hello").to("dict")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToTuple
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToTuple(TestCase):

    def testToTuple(self):
        """
        Serialize a tuple value with the 'tuple' type hint prefix.

        Validates that to('tuple') produces the 'tuple:<repr>' format using
        the repr of the tuple.
        """
        self.assertEqual(
            EnvironmentCaster((1, 2, 3)).to("tuple"),
            "tuple:(1, 2, 3)",
        )

    def testToTupleRaisesErrorForNonTuple(self):
        """
        Raise ValueError when a non-tuple value is serialized with tuple hint.

        Confirms that type enforcement in __toTuple is propagated as ValueError
        through to().
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("hello").to("tuple")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToSet
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToSet(TestCase):

    def testToSet(self):
        """
        Serialize a set value with the 'set' type hint prefix.

        Uses a single-element set to avoid repr ordering non-determinism
        across different Python implementations.
        """
        self.assertEqual(EnvironmentCaster({42}).to("set"), "set:{42}")

    def testToSetRaisesErrorForNonSet(self):
        """
        Raise ValueError when a non-set value is serialized with set hint.

        Confirms that type enforcement in __toSet is propagated as ValueError
        through to().
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("hello").to("set")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToBase64
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToBase64(TestCase):

    def testToBase64Encode(self):
        """
        Encode a plain string value to Base64 with the 'base64' prefix.

        Validates that 'hello' is Base64-encoded to 'aGVsbG8=' and the
        result is prefixed with the type hint.
        """
        result = EnvironmentCaster("hello").to("base64")
        self.assertEqual(result, "base64:aGVsbG8=")

    def testToBase64PreservesAlreadyEncodedValue(self):
        """
        Preserve a value that is already valid Base64 without re-encoding.

        Confirms that a well-formed Base64 string passed as input is detected
        as valid and left unchanged in the serialized output.
        """
        result = EnvironmentCaster("aGVsbG8=").to("base64")
        self.assertEqual(result, "base64:aGVsbG8=")

    def testToBase64RaisesErrorForNonStringOrBytes(self):
        """
        Raise ValueError when a non-string/non-bytes value is Base64-encoded.

        Validates that the type check in __toBase64 rejects integer inputs
        and the error is propagated as ValueError through to().
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster(42).to("base64")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToPath
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToPath(TestCase):

    def testToPathAbsolute(self):
        """
        Serialize an absolute path string with the 'path' prefix.

        Uses the current working directory to construct a guaranteed absolute
        path and verifies the serialized output starts with 'path:' and
        contains the expected directory name.
        """
        abs_path = Path.cwd().as_posix()
        result = EnvironmentCaster(abs_path).to("path")
        self.assertTrue(result.startswith("path:"))
        self.assertIn(Path.cwd().name, result)

    def testToPathRelativeMadeAbsolute(self):
        """
        Resolve a relative path to an absolute form during serialization.

        Confirms that relative inputs are joined with the current working
        directory so the output always contains a full absolute path.
        """
        result = EnvironmentCaster("subdir/file.txt").to("path")
        self.assertTrue(result.startswith("path:"))
        self.assertTrue(result.endswith("/subdir/file.txt"))

    def testToPathFromPathObject(self):
        """
        Serialize a Path object with the 'path' type hint prefix.

        Validates that Path instances are accepted by __toPath and serialized
        in normalized POSIX format.
        """
        abs_path = Path.cwd()
        result = EnvironmentCaster(abs_path).to("path")
        self.assertTrue(result.startswith("path:"))
        self.assertIn(abs_path.name, result)

    def testToPathRaisesErrorForNonStringOrPath(self):
        """
        Raise ValueError when a non-string/non-Path value is used as path.

        Confirms that the type check in __toPath rejects integer inputs and
        the error is propagated as ValueError through to().
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster(42).to("path")

# ---------------------------------------------------------------------------
# TestEnvironmentCasterToInvalidType
# ---------------------------------------------------------------------------

class TestEnvironmentCasterToInvalidType(TestCase):

    def testToInvalidTypeHintRaisesError(self):
        """
        Raise ValueError when an unsupported type hint is passed to to().

        Validates that invalid type hint strings are rejected before dispatch
        and the caller receives a descriptive ValueError.
        """
        with self.assertRaises(ValueError):
            EnvironmentCaster("hello").to("invalid")

    def testToBase64RoundTrip(self):
        """
        Verify that encoding and decoding a string via Base64 is symmetric.

        Encodes a value through to('base64'), extracts the encoded portion,
        then decodes it with get() and confirms the original value is restored.
        """
        original = "round-trip test"
        encoded_repr = EnvironmentCaster(original).to("base64")
        # encoded_repr is "base64:<b64value>"; pass it to get() for decoding
        decoded = EnvironmentCaster(encoded_repr).get()
        self.assertEqual(decoded, original)
