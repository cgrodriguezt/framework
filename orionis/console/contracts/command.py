from abc import ABC, abstractmethod
from orionis.console.entities.command import Command as CommandEntity

class ICommand(ABC):

    @abstractmethod
    def timestamp(self, *, enabled: bool = True) -> "ICommand":
        """
        Configure timestamp display for command output.

        Add or remove timestamps in command execution results. Use this to
        toggle timestamp visibility for the command.

        Parameters
        ----------
        enabled : bool, default=True
            Enable or disable timestamp display.

        Returns
        -------
        ICommand
            The current ICommand instance for method chaining.

        Raises
        ------
        TypeError
            If enabled is not a boolean.
        """

    @abstractmethod
    def description(self, desc: str) -> "ICommand":
        """
        Set the command description.

        Assign a brief text describing the command's purpose. Used for help
        and documentation.

        Parameters
        ----------
        desc : str
            Description text for the command.

        Returns
        -------
        ICommand
            The current ICommand instance for method chaining.

        Raises
        ------
        TypeError
            If desc is not a string.
        """

    @abstractmethod
    def arguments(self, args: list) -> "ICommand":
        """
        Set CLI arguments for the command.

        Configure the list of accepted command-line arguments. Each argument
        must be a valid CLIArgument instance.

        Parameters
        ----------
        args : list
            List of CLIArgument instances.

        Returns
        -------
        ICommand
            The current ICommand instance for method chaining.

        Raises
        ------
        TypeError
            If args is not a list or contains non-CLIArgument elements.
        """

    @abstractmethod
    def get(self) -> tuple[str, CommandEntity]:
        """
        Retrieve the configured Command entity.

        Return a tuple containing the command signature and its CommandEntity
        configuration.

        Returns
        -------
        tuple of (str, CommandEntity)
            The command signature and CommandEntity object.
        """
