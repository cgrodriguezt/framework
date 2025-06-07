class OrionisTestRuntimeError(Exception):
    """
    Exception raised for errors that occur during the runtime of Orionis tests.
    This exception is intended to provide a clear and descriptive error message
    when a runtime error is encountered in the Orionis testing framework.
    Attributes:
    Example:
        raise OrionisTestRuntimeError("An unexpected runtime error occurred during testing.")
    """

    def __init__(self, msg: str):
        """
        Initializes the exception with a given error message.
        Args:
            msg (str): The error message describing the runtime error.
        """
        super().__init__(msg)

    def __str__(self) -> str:
        """
        Return a string representation of the exception, including the class name and the first argument.

        Returns:
            str: A string in the format '<ClassName>: <first argument>'.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
