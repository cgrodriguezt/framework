from orionis.failure.contracts.catch import ICatch

class DummyCatch(ICatch):

    def __init__(self):
        """
        Initializes a DummyCatch instance with default state.

        Attributes
        ----------
        called : bool
            Indicates whether the exception handler has been invoked. Defaults to False.
        last_args : tuple or None
            Stores the last arguments passed to the exception handler. Defaults to None.
        """
        self.called = False  # Tracks if the exception handler was called
        self.last_args = None  # Stores the last arguments received

    def exception(self, kernel, request, e):
        """
        Handles an exception by marking the handler as called and storing the arguments.

        Parameters
        ----------
        kernel : object
            The kernel or application context in which the exception occurred.
        request : object
            The request object associated with the current operation.
        e : Exception
            The exception instance that was raised.

        Returns
        -------
        None
            This method does not return any value. It updates the internal state.
        """
        self.called = True  # Mark that the handler has been called
        self.last_args = (kernel, request, e)  # Store the arguments for later inspection
