import re
from orionis.schemas.contracts.rule import Rule
from orionis.schemas.entities.failure import ValidationFailure

class StrongPassword(Rule):
    """Validate that a password satisfies minimum strength requirements."""

    MIN_PASSWORD_LENGTH = 8

    # Expose the stable rule identifier.
    @property
    def code(self) -> str:
        """Return the unique code for this validation rule.

        Returns
        -------
        str
            Rule identifier used in validation failures.
        """
        return "strong_password"

    # Evaluate the provided value against password strength rules.
    def validate(
        self,
        field: str,
        value: object,
        instance: object,
    ) -> list[ValidationFailure]:
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
        list[ValidationFailure]
            Validation failures for unmet password requirements.
        """
        # Collect all requirement failures without short-circuiting.
        failures: list[ValidationFailure] = []

        # Ignore non-string values for this rule.
        if not isinstance(value, str):
            return failures

        # Enforce minimum password length.
        if len(value) < self.MIN_PASSWORD_LENGTH:
            failures.append(
                ValidationFailure(
                    field=field,
                    rule=self.code,
                    message=(
                        "Password must contain at least "
                        f"{self.MIN_PASSWORD_LENGTH} characters."
                    ),
                ),
            )

        # Require at least one uppercase letter.
        if not re.search(r"[A-Z]", value):
            failures.append(
                ValidationFailure(
                    field=field,
                    rule=self.code,
                    message="Password must contain an uppercase letter.",
                ),
            )

        # Require at least one lowercase letter.
        if not re.search(r"[a-z]", value):
            failures.append(
                ValidationFailure(
                    field=field,
                    rule=self.code,
                    message="Password must contain a lowercase letter.",
                ),
            )

        # Require at least one numeric digit.
        if not re.search(r"\d", value):
            failures.append(
                ValidationFailure(
                    field=field,
                    rule=self.code,
                    message="Password must contain a digit.",
                ),
            )

        return failures
