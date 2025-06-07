class OrionisCoroutineException(Exception):
    """
    Exception raised for errors related to coroutine operations in the Orionis framework.
    This exception is intended to signal issues encountered during asynchronous
    operations, providing a clear and descriptive error message to facilitate debugging.
        msg (str): A detailed message describing the cause of the exception.
    Example:
        raise OrionisCoroutineException("Coroutine execution failed due to timeout.")
    """

    def __init__(self, msg: str):
        """
        Initialize the exception with a custom error message.
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
