class DataclassValues:

    def __call__(self, dataclass_type: type) -> dict:
        """
        Extract attributes and their values from a given dataclass type.

        This method retrieves all attributes defined in the provided dataclass type,
        excluding special attributes (those whose names start with '__'). It returns
        a dictionary where the keys are the attribute names and the values are the
        corresponding attribute values.

        Parameters
        ----------
        dataclass_type : type
            The dataclass type from which to extract attributes.

        Returns
        -------
        dict
            A dictionary containing attribute names as keys and their corresponding
            values as values. Special attributes (those starting with '__') are excluded.
        """

        # Retrieve all attributes from the dataclass type's __dict__ attribute
        # Exclude special attributes (names starting with '__')
        values = {k: v for k, v in dataclass_type.__dict__.items() if not k.startswith("__")}
        return values

# Instantiate the DataclassValues callable
attributes = DataclassValues()