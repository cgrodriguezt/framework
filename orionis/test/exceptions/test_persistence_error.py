class OrionisTestPersistenceError(Exception):
    """
    Custom exception for persistence errors in tests within the Orionis framework.

    This exception is used to indicate issues related to data persistence during test execution,
    providing a descriptive message to help identify and resolve the error.

    Args:
        msg (str): A descriptive message explaining the cause of the persistence error.

    Example:
        raise OrionisTestPersistenceError("Failed to save test state to the database.")
    """

    def __init__(self, msg: str):
        """
        Initializes the OrionisTestConfigException with a specific error message.

        Args:
            msg (str): A descriptive error message explaining the cause of the exception.
        """
        super().__init__(msg)

    def __str__(self) -> str:
        """
        Returns a formatted string representation of the exception.

        The string includes the exception name and the error message, providing
        a clear and concise description of the issue.

        Returns:
            str: A formatted string describing the exception.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
