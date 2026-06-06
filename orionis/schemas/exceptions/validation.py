from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.schemas.entities.failure import ValidationFailure

class ValidationException(Exception):

    def __init__(self, failures: list[ValidationFailure]) -> None:
        """
        Initialize the exception with collected validation failures.

        Parameters
        ----------
        failures : list[ValidationFailure]
            Provide validation failures to attach to the exception.

        Returns
        -------
        None
            Return ``None`` after storing failures and setting the message.
        """
        self.failures = failures
        error_msg = failures[0].message if failures else "Validation failed."

        super().__init__(error_msg)

    # Group all failure messages by their field names.
    def errors(self) -> dict[str, list[str]]:
        """
        Build a dictionary of failure messages grouped by field.

        Returns
        -------
        dict[str, list[str]]
            Return field names mapped to their collected error messages.
        """
        result: dict[str, list[str]] = {}
        for failure in self.failures:
            result.setdefault(failure.field, []).append(failure.message)
        return result
