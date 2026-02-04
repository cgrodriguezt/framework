from __future__ import annotations

class Final(type):

    def __new__(
        metacls: type,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
    ) -> type:
        """
        Create a new class and prevent inheritance from final classes.

        Parameters
        ----------
        metacls : type
            The metaclass itself.
        name : str
            The name of the class being created.
        bases : tuple of type
            The base classes of the class being created.
        namespace : dict[str, object]
            The namespace containing class attributes.

        Returns
        -------
        type
            The newly created class object.

        Raises
        ------
        TypeError
            If any base class is already final.
        """
        # Check if any base class uses the Final metaclass
        for base in bases:
            # Raise error if inheriting from a final class
            if isinstance(base, Final):
                error_msg = (
                    f"Cannot inherit from final class '{base.__name__}'"
                )
                raise TypeError(error_msg)
        # Create and return the new class object
        return super().__new__(metacls, name, bases, namespace)
