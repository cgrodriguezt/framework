from __future__ import annotations
from typing import TYPE_CHECKING
import msgspec
from orionis.schemas.exception_parser import ValidationErrorParser
from orionis.schemas.exceptions.validation import ValidationException
from orionis.schemas.rules_executor import RulesExecutor

if TYPE_CHECKING:
    from orionis.schemas.schema import Schema

class Schema:

    @staticmethod
    def validate(payload: object, schema: type[Schema]) -> Schema:
        """
        Validate a payload against a schema and return its typed instance.

        Parameters
        ----------
        payload : object
            Input data to convert and validate.
        schema : type[Schema]
            Schema type used for conversion and validation.

        Returns
        -------
        Schema
            Converted schema instance after successful validation.

        Raises
        ------
        ValidationException
            Raised when payload conversion or validation fails.
        """
        # Convert the payload into a schema instance using msgspec.
        try:
            instance = msgspec.convert(
                payload,
                type=schema,
            )

        # Catch msgspec validation errors and re-raise them as framework exceptions.
        except msgspec.ValidationError as exc:
            error_msg = ValidationErrorParser.parse(exc)
            raise ValidationException(
                error_msg,
            ) from exc

        # After conversion, execute any custom validation rules defined on the schema.
        RulesExecutor.execute(instance)

        # If all validation passes, return the converted instance.
        return instance
