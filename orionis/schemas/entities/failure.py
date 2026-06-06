from dataclasses import dataclass
from orionis.support.entities.base import BaseEntity

@dataclass(slots=True, frozen=True)
class ValidationFailure(BaseEntity):
    """
    Represent a validation failure.

    Attributes
    ----------
    field : str
        Identify the field that failed validation.
    rule : str
        Identify the validation rule that failed.
    message : str
        Describe the validation failure.

    Returns
    -------
    ValidationFailure
        Return a new immutable validation failure instance when instantiated.
    """

    # Store validation failure details.
    field: str
    rule: str
    message: str
