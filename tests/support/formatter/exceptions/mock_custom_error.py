class CustomError(Exception):
    """
    Custom exception for errors with an optional error code.

    Parameters
    ----------
    message : str
        Description of the error.
    code : any, optional
        Optional error code associated with the exception.

    Attributes
    ----------
    code : any
        The optional error code associated with the exception.
    """

    def __init__(self, message, code=None):
        """
        Initialize CustomError with a message and optional error code.

        Parameters
        ----------
        message : str
            Description of the error.
        code : any, optional
            Optional error code associated with the exception. Default is None.
        """
        # Initialize the base Exception with the provided message
        super().__init__(message)

        # Store the optional error code in the instance
        self.code = code
