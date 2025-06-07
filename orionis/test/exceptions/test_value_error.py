class OrionisTestValueError(Exception):

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
            A formatted string in the form 'ClassName: message', including the class name and the first argument.
        """
        return f"{self.__class__.__name__}: {self.args[0]}"
