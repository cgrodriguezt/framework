class SkeletomIntegrityException(Exception):
    """
    Exception raised when an integrity violation is detected within the Orionis framework configuration.
    This exception is specifically designed to highlight issues such as duplicate identifiers, missing required fields,
    or other inconsistencies that compromise the integrity of the framework's setup. By providing a clear and descriptive
    error message, it assists developers in quickly identifying and resolving configuration problems, thereby ensuring
    the reliability and correctness of the framework.
        msg (str): A detailed, human-readable description of the integrity error encountered.
        raise SkeletomIntegrityException("Duplicate test case identifier found in configuration.")
        msg (str): The error message describing the specific integrity violation.
    """

    def __init__(self, msg: str):
        """
        Initializes the exception with a custom error message.

        Args:
            msg (str): The error message describing the exception.
        """
        super().__init__(msg)

    def __str__(self) -> str:
        """
        Return a string representation of the exception, including the class name and the first argument.

        Returns:
            str: A string in the format '<ClassName>: <first argument>'.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
