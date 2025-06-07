class OrionisTestRuntimeError(Exception):

    def __init__(self, msg: str):
        """
        Parameters
        ----------
        msg : str
            The error message describing the runtime error.
        """
        super().__init__(msg)

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            String representation of the exception in the format '<ClassName>: <first argument>'.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
