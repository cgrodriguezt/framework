class OrionisEnvironmentValueException(Exception):
    """
    Exception raised for invalid or unexpected environment values within the Orionis framework.
    This exception is intended to signal issues encountered when an environment variable,
    configuration value, or similar parameter does not meet the expected criteria or format.
    It provides a clear and descriptive error message to facilitate debugging and error handling.
    Attributes:
        raise OrionisEnvironmentValueException("Invalid value for ORIONIS_MODE: expected 'production' or 'development'.")
        msg (str): The error message describing the specific value-related exception.
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
            str: A formatted string with the exception class name and its first argument.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
