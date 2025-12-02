from abc import ABC, abstractmethod

class IKernelCLI(ABC):

    @abstractmethod
    def handle(self, args: list) -> None:
        """
        Process command line arguments.

        Parameters
        ----------
        args : list
            List of command line arguments, usually from sys.argv.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        NotImplementedError
            Raised if the method is not implemented by a subclass.
        """
        error_msg = (
            "This method should be overridden by subclasses."
        )
        raise NotImplementedError(error_msg)
