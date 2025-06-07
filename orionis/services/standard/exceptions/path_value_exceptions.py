class OrionisStdValueException(Exception):
    """
    Exception raised for standard value errors in the Orionis framework.

    Args:
        msg (str): A detailed message describing the value error.

    Example:
        raise OrionisStdValueException("Invalid value for parameter 'timeout'.")
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
            str: A formatted string with the exception class name and the first argument.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
