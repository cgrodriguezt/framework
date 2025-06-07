class OrionisTestConfigException(Exception):

    def __init__(self, msg: str):
        """
        Parameters
        ----------
        msg : str
            Descriptive error message explaining the cause of the exception.
        """
        super().__init__(msg)

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            Formatted string describing the exception, including the exception name and error message.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
