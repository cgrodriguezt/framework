class OrionisTestValueError(Exception):
    """
    Custom exception class for handling value errors in the Orionis test framework.
    This exception should be raised when a value-related error occurs during testing.
    It provides a formatted string representation that includes the class name and the error message.
    Example:
        raise OrionisTestValueError("Invalid value provided.")
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
            str: A formatted string in the form 'ClassName: message'.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
