class OrionisEnvironmentValueError(Exception):

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
