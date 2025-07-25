class CustomError(Exception):
    """
    Custom exception class for handling errors with an optional error code.

    Parameters
    ----------
    message : str
        The error message describing the exception.
    code : any, optional
        An optional error code associated with the exception.

    Attributes
    ----------
    code : any
        Stores the optional error code associated with the exception.

    """

    def __init__(self, message, code=None):
        """
        Initialize the CustomError instance with a message and an optional error code.

        Parameters
        ----------
        message : str
            The error message describing the exception.
        code : any, optional
            An optional error code associated with the exception. Default is None.

        Returns
        -------
        None
            This method does not return a value. It initializes the instance.

        Notes
        -----
        The error message is passed to the base Exception class. The optional error code is stored as an instance attribute.
        """

        # Initialize the base Exception with the provided message
        super().__init__(message)

        # Store the optional error code in the instance
        self.code = code