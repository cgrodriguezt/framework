from orionis.schemas.contracts.constraint import IRule
from orionis.schemas.entities.failure import ValidationFailure

class Rule(IRule):

    __slots__ = ("_message", "_resolved_code", "_resolved_default_message")

    def __init__(self, *, message: str | None = None) -> None:
        """
        Initialize the rule with an optional custom failure message.

        Parameters
        ----------
        message : str | None, optional
            Override message used when validation fails.

        Returns
        -------
        None
            Return ``None`` after storing the provided message.
        """
        # Store the provided message for use during validation failures.
        self._message = message

        # Resolve class-level attributes once at construction time.
        klass = type(self)
        self._resolved_code: str = getattr(klass, "__code__", klass.__name__.lower())
        self._resolved_default_message: str | None = getattr(klass, "__message__", None)

    def enforce(
        self,
        field: str,
        value: object,
        instance: object,
    ) -> bool:
        """
        Evaluate whether the current value satisfies this rule.

        Parameters
        ----------
        field : str
            Field name associated with ``value``.
        value : object
            Current field value to validate.
        instance : object
            Schema instance that owns the field value.

        Returns
        -------
        bool
            Return ``True`` when the value passes validation.
        """
        error_msg = "Subclasses must implement the enforce method."
        raise NotImplementedError(error_msg)

    def validate(
        self,
        field: str,
        value: object,
        instance: object,
    ) -> ValidationFailure | None:
        """
        Validate the field value and return a failure when invalid.

        Parameters
        ----------
        field : str
            Field name associated with ``value``.
        value : object
            Current field value to validate.
        instance : object
            Schema instance that owns the field value.

        Returns
        -------
        ValidationFailure | None
            Failure details when validation fails; otherwise ``None``.
        """
        if not self.enforce(field, value, instance):
            return ValidationFailure(
                field=field,
                rule=self._resolved_code,
                message=self._message or self._resolved_default_message,
            )

        return None
