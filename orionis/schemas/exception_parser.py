from __future__ import annotations
import re
from typing import TYPE_CHECKING
from orionis.schemas.entities.failure import ValidationFailure

if TYPE_CHECKING:
    import msgspec

PATH_RE = re.compile(r"(?P<message>.+?) - at `\$(?P<path>.*?)`$")

class ValidationErrorParser:
    """Parse validation errors into :class:`ValidationFailure` objects."""

    @classmethod
    def parse(
        cls,
        error: msgspec.ValidationError,
    ) -> list[ValidationFailure]:
        """
        Parse a msgspec validation error into framework failures.

        Parameters
        ----------
        error : msgspec.ValidationError
            Provide the original validation exception.

        Returns
        -------
        list[ValidationFailure]
            Return a single-item list describing the parsed validation failure.
        """
        text = str(error)

        match = PATH_RE.match(text)

        if match is None:
            return [
                ValidationFailure(
                    field="",
                    rule="invalid",
                    message=text,
                ),
            ]

        message = match.group("message")

        field = match.group("path").lstrip(".")

        return [
            ValidationFailure(
                field=field,
                rule=cls._detectRule(message),
                message=message,
            ),
        ]

    # Infer a coarse validation rule from the parser message text.
    @staticmethod
    def _detectRule(
        message: str,
    ) -> str:
        """
        Detect the validation rule category from an error message.

        Parameters
        ----------
        message : str
            Provide the validation message text.

        Returns
        -------
        str
            Return ``"type"`` for expected-type messages, else ``"invalid"``.
        """
        if message.startswith("Expected"):
            return "type"

        return "invalid"
