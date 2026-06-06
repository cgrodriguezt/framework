from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.schemas.contracts.rule import Rule
from orionis.schemas.exceptions.validation import ValidationException

if TYPE_CHECKING:
    from orionis.schemas.entities.failure import ValidationFailure

class RulesExecutor:

    @staticmethod
    def execute(instance: object) -> None:
        """
        Validate an instance using its declared metadata rules.

        Parameters
        ----------
        instance : object
            Instance whose fields and rules will be validated.

        Returns
        -------
        None
            Return ``None`` when validation succeeds.

        Raises
        ------
        ValidationException
            Raise when one or more validation failures are found.
        """
        # Collect all failures before raising a single exception.
        failures: list[ValidationFailure] = []

        # Read rule metadata attached to the instance class.
        metadata = getattr(instance.__class__, "__orionis_meta__", {})

        # Validate each field value against its configured rules.
        for field, items in metadata.items():

            value = getattr(instance, field)

            for item in items:

                if not isinstance(item, Rule):
                    continue

                failures.extend(
                    item.validate(
                        field=field,
                        value=value,
                        instance=instance,
                    ),
                )

        # Raise a single exception with all collected failures.
        if failures:
            raise ValidationException(
                failures,
            )
