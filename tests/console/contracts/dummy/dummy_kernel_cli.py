from orionis.console.contracts.kernel import IKernelCLI

class DummyKernelCLI(IKernelCLI):
    """
    Dummy implementation of IKernelCLI for testing purposes.

    This class provides a simple implementation of the IKernelCLI interface,
    intended for use in unit tests or as a placeholder. It records the arguments
    passed to its `handle` method for later inspection.

    Methods
    -------
    handle(args)
        Stores the provided arguments for testing purposes.

    Attributes
    ----------
    handled_args : list or None
        Stores the arguments passed to the `handle` method.
    """
    def __init__(self):
        """
        Initializes a new instance of DummyKernelCLI.

        This constructor sets the `handled_args` attribute to None, indicating that no arguments
        have been handled yet. The attribute will later store the arguments passed to the `handle`
        method for testing and inspection purposes.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It initializes the `handled_args` attribute.
        """
        # Initialize handled_args to None; will be updated when handle() is called
        self.handled_args = None

    def handle(self, args: list) -> None:
        """
        Stores the provided arguments for testing purposes.

        Parameters
        ----------
        args : list
            The list of arguments to be handled.

        Returns
        -------
        None
            This method does not return any value. It updates the `handled_args`
            attribute with the provided arguments.
        """
        # Store the arguments for later inspection
        self.handled_args = args