from typing import Annotated
import msgspec
from orionis.schemas.exception_parser import ValidationErrorParser
from orionis.schemas.entities.failure import ValidationFailure
from orionis.schemas.schema import Schema
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Minimal schema fixtures for parser tests
# ---------------------------------------------------------------------------

class _SimpleSchema(Schema):
    name: str
    age: int

class _NestedChild(Schema):
    code: str

class _ParentSchema(Schema):
    child: _NestedChild
    value: int

class TestValidationErrorParser(TestCase):

    def testParseTypeErrorWithPath(self) -> None:
        """
        Parse a msgspec ValidationError carrying a field path.

        Validates that the parser extracts the field name and returns
        a ValidationFailure with a non-empty field attribute.
        """
        try:
            msgspec.convert({"name": "Alice", "age": "not_int"}, type=_SimpleSchema)
            self.fail("Expected msgspec.ValidationError was not raised")
        except msgspec.ValidationError as exc:
            failure = ValidationErrorParser.parse(exc, _SimpleSchema)
            self.assertIsInstance(failure, ValidationFailure)
            self.assertEqual(failure.field, "age")

    def testParseMissingRequiredField(self) -> None:
        """
        Parse a msgspec ValidationError for a missing required field.

        Validates that the parser extracts the missing field name and
        sets the failure field attribute accordingly.
        """
        try:
            msgspec.convert({}, type=_SimpleSchema)
            self.fail("Expected msgspec.ValidationError was not raised")
        except msgspec.ValidationError as exc:
            failure = ValidationErrorParser.parse(exc, _SimpleSchema)
            self.assertIsInstance(failure, ValidationFailure)
            self.assertIn(failure.field, ("name", "age", ""))

    def testParseReturnsValidationFailureInstance(self) -> None:
        """
        Return a ValidationFailure instance for any msgspec ValidationError.

        Validates that the parser always produces a ValidationFailure
        regardless of the specific error kind.
        """
        try:
            msgspec.convert({"name": 123, "age": 30}, type=_SimpleSchema)
            self.fail("Expected msgspec.ValidationError was not raised")
        except msgspec.ValidationError as exc:
            failure = ValidationErrorParser.parse(exc, _SimpleSchema)
            self.assertIsInstance(failure, ValidationFailure)

    def testParseWithoutSchemaStillReturnsFailure(self) -> None:
        """
        Return a ValidationFailure when no schema argument is supplied.

        Validates that the parser handles schema=None gracefully and
        still produces a structurally valid failure object.
        """
        try:
            msgspec.convert({"name": 1, "age": 30}, type=_SimpleSchema)
            self.fail("Expected msgspec.ValidationError was not raised")
        except msgspec.ValidationError as exc:
            failure = ValidationErrorParser.parse(exc)
            self.assertIsInstance(failure, ValidationFailure)
            self.assertIsInstance(failure.message, str)

    def testParseNestedFieldPath(self) -> None:
        """
        Parse a msgspec ValidationError for a nested field.

        Validates that the parser correctly resolves a dotted field path
        and returns a failure with the leaf field name.
        """
        try:
            msgspec.convert(
                {"child": {"code": 999}, "value": 1},
                type=_ParentSchema,
            )
            self.fail("Expected msgspec.ValidationError was not raised")
        except msgspec.ValidationError as exc:
            failure = ValidationErrorParser.parse(exc, _ParentSchema)
            self.assertIsInstance(failure, ValidationFailure)
            self.assertIn("code", failure.field)

    def testParseRuleIsTypeForPlainTypeError(self) -> None:
        """
        Set the rule attribute to 'type' for a plain type mismatch.

        Validates that when the error message matches the 'Expected' pattern
        the resulting rule key is 'type'.
        """
        try:
            msgspec.convert({"name": 42, "age": 1}, type=_SimpleSchema)
            self.fail("Expected msgspec.ValidationError was not raised")
        except msgspec.ValidationError as exc:
            failure = ValidationErrorParser.parse(exc, _SimpleSchema)
            self.assertEqual(failure.rule, "type")

    def testParseConstraintKeyMinLength(self) -> None:
        """
        Identify 'min_length' rule from a msgspec min-length error message.

        Validates that the parser extracts the correct constraint key when
        a string is too short.
        """

        class _LenSchema(Schema):
            token: Annotated[str, msgspec.Meta(min_length=5)]

        try:
            msgspec.convert({"token": "ab"}, type=_LenSchema)
            self.fail("Expected msgspec.ValidationError was not raised")
        except msgspec.ValidationError as exc:
            failure = ValidationErrorParser.parse(exc, _LenSchema)
            self.assertEqual(failure.rule, "min_length")

    def testParseConstraintKeyMaxLength(self) -> None:
        """
        Identify 'max_length' rule from a msgspec max-length error message.

        Validates that the parser extracts the correct constraint key when
        a string is too long.
        """

        class _MaxLenSchema(Schema):
            tag: Annotated[str, msgspec.Meta(max_length=3)]

        try:
            msgspec.convert({"tag": "toolong"}, type=_MaxLenSchema)
            self.fail("Expected msgspec.ValidationError was not raised")
        except msgspec.ValidationError as exc:
            failure = ValidationErrorParser.parse(exc, _MaxLenSchema)
            self.assertEqual(failure.rule, "max_length")

    def testMatchConstraintKeyReturnsNoneForUnknownMessage(self) -> None:
        """
        Return None when no known pattern matches the constraint message.

        Validates the _matchConstraintKey helper returns None for a
        message that does not match any registered pattern.
        """
        result = ValidationErrorParser._matchConstraintKey(
            "some completely unknown error format xyz",
        )
        self.assertIsNone(result)

    def testMatchConstraintKeyDetectsGt(self) -> None:
        """
        Return 'gt' when the message contains ' > '.

        Validates that the constraint pattern index correctly identifies
        the greater-than constraint key.
        """
        result = ValidationErrorParser._matchConstraintKey(
            "Expected `int` satisfying x > 0",
        )
        self.assertEqual(result, "gt")

    def testMatchConstraintKeyDetectsLt(self) -> None:
        """
        Return 'lt' when the message contains ' < '.

        Validates that the constraint pattern index correctly identifies
        the less-than constraint key.
        """
        result = ValidationErrorParser._matchConstraintKey(
            "Expected `int` satisfying x < 100",
        )
        self.assertEqual(result, "lt")
