class OrionisTestPersistenceError(Exception):

    def __init__(self, msg: str):
        """
        Initialize the OrionisTestPersistenceError with a specific error message.

        Parameters
        ----------
        msg : str
            Descriptive error message explaining the cause of the exception.
        """
        super().__init__(msg)

    def __str__(self) -> str:
        """
        Returns a formatted string representation of the exception.

        Returns
        -------
        str
            A formatted string describing the exception, including the exception
            name and the error message.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
