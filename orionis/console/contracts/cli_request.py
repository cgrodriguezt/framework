from abc import ABC, abstractmethod

class ICLIRequest(ABC):

    @abstractmethod
    def command(self) -> str:
        """
        Return the command name for this CLI request.

        This method provides the command string specified during initialization.
        The command identifies the main operation to execute.

        Returns
        -------
        str
            The command name as a string.
        """

    @abstractmethod
    def arguments(self) -> dict:
        """
        Return all command line arguments as a dictionary.

        This method provides access to all parsed CLI arguments.

        Returns
        -------
        dict
            Dictionary of argument names and their values.
        """

    @abstractmethod
    def argument(self, name: str, default: object = None) -> object:
        """
        Retrieve the value of a specific command line argument.

        This method returns the value associated with the provided argument name.
        If the argument is not present, it returns the specified default value.

        Parameters
        ----------
        name : str
            Name of the argument to retrieve.
        default : object, optional
            Value to return if the argument is not found. Defaults to None.

        Returns
        -------
        object
            Value of the argument if found, otherwise the default value.
        """
