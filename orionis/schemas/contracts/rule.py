from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.schemas.entities.failure import ValidationFailure

class Rule(ABC):

    @property
    @abstractmethod
    def code(self) -> str:
        """Return the unique code that identifies the validation rule.

        Returns
        -------
        str
            Unique rule code used to classify validation failures.
        """
        ...

    @abstractmethod
    def validate(
        self,
        field: str,
        value: object,
        instance: object,
    ) -> list[ValidationFailure]:
        """Validate the provided value and return validation failures.

        Parameters
        ----------
        field : str
            Name of the field being validated.
        value : object
            Current field value to validate.
        instance : object
            Object instance that owns the field.

        Returns
        -------
        list[ValidationFailure]
            Collected failures for this rule, or an empty list when valid.
        """
        ...
