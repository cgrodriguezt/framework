from __future__ import annotations
import re
from typing import TYPE_CHECKING
from orionis.schemas.entities.failure import ValidationFailure

if TYPE_CHECKING:
    import msgspec

PATH_RE = re.compile(r"(?P<message>.+?) - at `\$(?P<path>.*?)`$")

class ValidationErrorParser:

    @classmethod
    def parse(
        cls,
        error: msgspec.ValidationError,
    ) -> ValidationFailure:
        """
        Parse a msgspec validation error into framework failures.

        Parameters
        ----------
        error : msgspec.ValidationError
            Provide the original validation exception.

        Returns
        -------
        ValidationFailure
            Return a single validation failure describing the parsed error.
        """
        text = str(error)

        match = PATH_RE.match(text)

        if match is None:
            return ValidationFailure(
                field="",
                rule="invalid",
                message=text,
            )

        message = match.group("message")

        field = match.group("path").lstrip(".")

        return ValidationFailure(
            field=field,
            rule="type" if message.startswith("Expected") else "invalid",
            message=message,
        )
