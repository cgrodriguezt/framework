class Final(type):

    def __new__(
        metacls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object]
    ):
        """
        Prevent inheriting from classes using this metaclass.

        Parameters
        ----------
        metacls : type
            The metaclass itself.
        name : str
            The name of the class being created.
        bases : tuple of type
            The base classes of the class being created.
        namespace : dict of str to object
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
