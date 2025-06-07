class OrionisCoroutineException(Exception):

    def __init__(self, msg: str):
        """
        Parameters
        ----------
        msg : str
            The error message describing the exception.
        """
        super().__init__(msg)

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            A formatted string with the exception class name and its first argument.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
