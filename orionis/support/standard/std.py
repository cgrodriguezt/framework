from __future__ import annotations
from orionis.support.standard.contracts.std import IStdClass

class StdClass(IStdClass):

    def __hash__(self) -> int:
        """
        Compute the hash value of the object based on its attributes.

        Returns
        -------
        int
            Hash value computed from the object's attributes.
        """
        # Use a tuple of sorted items to ensure consistent hash value
        return hash(tuple(sorted(self.__dict__.items())))

    def __init__(self, **kwargs: object) -> None:
        """
        Initialize attributes from keyword arguments.

        Parameters
        ----------
        **kwargs : object
            Arbitrary keyword arguments to set as attributes.

        Returns
        -------
        None
            This method does not return a value. The object is initialized in-place.
        """
        # Set attributes from keyword arguments
        self.update(**kwargs)

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation for debugging.

        Returns
        -------
        str
            String representation of the object with its attributes.
        """
        # Show class name and attributes for debugging
        return f"{self.__class__.__name__}({self.__dict__})"

    def __str__(self) -> str:
        """
        Return a readable string representation of the object.

        Returns
        -------
        str
            String showing the object's attributes.
        """
        # Show attributes as a string
        return str(self.__dict__)

    def __eq__(self, other: object) -> bool:
        """
        Compare this object with another for attribute equality.

        Parameters
        ----------
        other : object
            Object to compare with.

        Returns
        -------
        bool
            True if both objects have the same attributes and values, otherwise False.
        """
        # Only compare if other is StdClass
        if not isinstance(other, StdClass):
            return False
        return self.__dict__ == other.__dict__

    def toDict(self) -> dict:
        """
        Convert the object's attributes to a dictionary.

        Returns
        -------
        dict
            A shallow copy of the object's attributes.
        """
        # Return a copy to avoid external modifications
        return self.__dict__.copy()

    def update(self, **kwargs: object) -> None:
        """
        Update the object's attributes dynamically.

        Parameters
        ----------
        **kwargs : object
            Key-value pairs to update or add as attributes.

        Returns
        -------
        None
            This method does not return a value. Attributes are updated in-place.

        Raises
        ------
        OrionisStdValueException
            If an attribute name is reserved or conflicts with a class method.
        """
        for key, value in kwargs.items():
            # Prevent setting reserved or conflicting attribute names
            if key.startswith("__") and key.endswith("__"):
                error_msg = f"Cannot set attribute with reserved name: {key}"
                raise ValueError(error_msg)
            if hasattr(self.__class__, key):
                error_msg = (
                    f"Cannot set attribute '{key}' as it conflicts with a class method"
                )
                raise ValueError(error_msg)
            setattr(self, key, value)

    def remove(self, *attributes: str) -> None:
        """
        Remove one or more attributes from the object.

        Parameters
        ----------
        *attributes : str
            Names of the attributes to remove.

        Returns
        -------
        None
            This method does not return a value. Attributes are removed in-place.

        Raises
        ------
        AttributeError
            If any of the specified attributes do not exist.
        """
        for attr in attributes:
            # Raise error if attribute does not exist
            if not hasattr(self, attr):
                error_msg = f"Attribute '{attr}' not found"
                raise AttributeError(error_msg)
            delattr(self, attr)

    @classmethod
    def fromDict(cls, dictionary: dict) -> StdClass:
        """
        Create a StdClass instance from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing attribute names and values.

        Returns
        -------
        StdClass
            A new StdClass instance with attributes set from the dictionary.
        """
        # Instantiate StdClass from dictionary
        return cls(**dictionary)
