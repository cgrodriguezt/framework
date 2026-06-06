import re
from orionis.schemas.contracts.rule import Rule
from orionis.schemas.entities.failure import ValidationFailure

class StrongPassword(Rule):
    """Validate that a password satisfies minimum strength requirements."""

    # ruff: noqa: ARG002

    MIN_PASSWORD_LENGTH = 8
    DEFAULT_MESSAGE = (
        "Password must be at least "
        f"{MIN_PASSWORD_LENGTH} characters long, "
        "contain an uppercase letter, a lowercase letter, and a digit."
    )

    @property
    def code(self) -> str:
        """Return the unique code for this validation rule.

        Returns
        -------
        str
            Rule identifier used in validation failures.
        """
        return "strong_password"

    def __init__(self, *, message: str | None = None) -> None:
        """Initialize the rule with an optional custom failure message.

        Parameters
        ----------
        message : str | None, optional
            Message used for all password requirement failures. If ``None``,
            default messages are used.
        """
        self.__message = message

    def validate(
        self,
        field: str,
        value: object,
        instance: object,
    ) -> ValidationFailure | None:
        """
        Validate a field value as a strong password.

        Parameters
        ----------
        field : str
            Field name associated with the value.
        value : object
            Value to validate.
        instance : object
            Owning object instance. This argument is accepted for
            interface compatibility.

        Returns
        -------
        ValidationFailure | None
            Validation failure for unmet password requirements,
            or None if the password is valid.
        """
        # Ignore non-string values for this rule.
        if not isinstance(value, str):
            return None

        # Check password strength requirements and return a failure if any are not met.
        if (
            len(value) < self.MIN_PASSWORD_LENGTH or
            not re.search(r"[A-Z]", value) or
            not re.search(r"[a-z]", value) or
            not re.search(r"\d", value)
        ):
            return ValidationFailure(
                field=field,
                rule=self.code,
                message=self.__message or self.DEFAULT_MESSAGE,
            )

        # All requirements are met, so return None to indicate validation success.
        return None
