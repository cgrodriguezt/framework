from orionis.schemas.rule import Rule

class ZipCode(Rule):

    __message__ = "Invalid ZIP code format."
    __code__ = "zipcode"

    def enforce(
        self,
        field: str,
        value: object,
        instance: object,
    ) -> bool:
        """
        Validate a field value as a ZIP code.

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
        bool
            Return ``True`` when the value passes validation.
        """
        return (
            isinstance(value, str) and
            len(value) == 5 and
            value.isdigit() and
            int(value) >= 501 and
            int(value) <= 99950
        )
