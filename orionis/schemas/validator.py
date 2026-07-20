from __future__ import annotations
from typing import TYPE_CHECKING
import msgspec
from orionis.schemas.exception_parser import ValidationErrorParser
from orionis.schemas.exceptions.validation import ValidationException
from orionis.schemas.rules_executor import _cache_get, _build_plan, _execute_with_plan

if TYPE_CHECKING:
    from orionis.schemas.schema import Schema

# Alias msgspec's convert function to avoid direct dependency on msgspec in the
# rest of the codebase.
_convert = msgspec.convert

# Alias msgspec's ValidationError to avoid direct
# dependency on msgspec in the rest of the codebase.
_ValidationError = msgspec.ValidationError

class Schema:

    @staticmethod
    def validate(payload: object, schema: type[Schema]) -> Schema:
        """
        Validate payload against a schema and return a typed instance.

        Parameters
        ----------
        payload : object
            Input data to convert and validate.
        schema : type[Schema]
            Schema class used for conversion and rule validation.

        Returns
        -------
        Schema
            Converted schema instance.

        Raises
        ------
        ValidationException
            If payload conversion fails or schema rules raise validation errors.
        """
        # Convert the payload into a schema instance using msgspec.
        try:
            instance = _convert(payload, type=schema)

        # Catch msgspec validation errors and re-raise them as framework exceptions.
        except _ValidationError as exc:
            raise ValidationException(
                ValidationErrorParser.parse(exc, schema),
            ) from exc

        # Use the known schema type directly — avoids a redundant type(instance)
        # call. Skip execution entirely when the plan is empty (the common case
        # for simple schemas with no custom rules).
        plan = _cache_get(schema)
        if plan is None:
            plan = _build_plan(schema)
        if plan:
            _execute_with_plan(plan, instance, "")

        return instance
