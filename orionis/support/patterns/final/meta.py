from __future__ import annotations

class Final(type):
    """
    Enforce that subclasses cannot inherit from final classes.
    """

    def __new__(
        metacls: type,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
    ) -> type:
        """
        Create a new class and enforce final class inheritance rules.

        Parameters
        ----------
        metacls : type
            The metaclass type.
        name : str
            The name of the new class.
        bases : tuple of type
            The base classes of the new class.
        namespace : dict of str to object
            The namespace containing class attributes.

        Returns
        -------
        type
            The newly created class object.

        Raises
        ------
        TypeError
            If attempting to inherit from a final class.
        """
        # Prevent inheritance from any class marked as final.
        for base in bases:
            if getattr(base, "__is_final__", False):
                error_msg = (
                    f"Cannot inherit from final class '{base.__name__}'"
                )
                raise TypeError(error_msg)

        # Mark the class as final and create it.
        cls = super().__new__(metacls, name, bases, namespace)
        cls.__is_final__ = True
        return cls