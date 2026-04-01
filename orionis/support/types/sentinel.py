class _MISSING_TYPE: # NOSONAR
    """
    Represent a sentinel type for missing values.

    Methods
    -------
    __repr__() -> str
        Return a string representation of the sentinel.
    __bool__() -> bool
        Return False to indicate the sentinel is falsy.
    """

    def __repr__(self) -> str:
        """
        Return a string representation of the sentinel.

        Returns
        -------
        str
            The string "<MISSING>" representing the sentinel.
        """
        return "<MISSING>"

    def __bool__(self) -> bool:
        """
        Return False to indicate the sentinel is falsy.

        Returns
        -------
        bool
            Always returns False.
        """
        return False

# Instance representing a missing value sentinel.
MISSING = _MISSING_TYPE()