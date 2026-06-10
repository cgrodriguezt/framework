class Final(type):

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

        Performance note
        ----------------
        ``base.__dict__.get`` is used instead of ``getattr`` to avoid the full
        MRO traversal that ``getattr`` triggers.  ``__is_final__`` is always set
        directly on the class object (never inherited), so checking ``__dict__``
        is both correct and faster.
        """
        # Prevent inheritance from any class marked as final.
        # ``__dict__.get`` avoids the MRO traversal cost of ``getattr``.
        for base in bases:
            if base.__dict__.get("__is_final__", False):
                error_msg = f"Cannot inherit from orionis final class '{base.__name__}'"
                raise TypeError(error_msg)

        # Mark the class as final and create it.
        cls = super().__new__(metacls, name, bases, namespace)
        type.__setattr__(cls, "__is_final__", True)
        return cls
