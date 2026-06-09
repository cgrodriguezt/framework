from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.schemas.entities.failure import ValidationFailure

class ValidationException(Exception):

    def __init__(self, failure: ValidationFailure) -> None:
        """
        Initialize the exception with a single validation failure.

        Parameters
        ----------
        failure : ValidationFailure
            Provide a validation failure to attach to the exception.

        Returns
        -------
        None
            Return ``None`` after storing the failure and setting the message.
        """
        self.failure = failure
        super().__init__(failure.message)

    def error(self) -> dict:
        """
        Return the validation failure details as a dictionary.

        Returns
        -------
        dict
            Return a dictionary containing the validation failure details.
        """
        return self.failure.toDict()
