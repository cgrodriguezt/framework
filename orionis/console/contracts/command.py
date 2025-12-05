from abc import ABC, abstractmethod
from orionis.console.entities.command import Command as CommandEntity

class ICommand(ABC):

    @abstractmethod
    def timestamp(self, *, enabled: bool = True) -> "ICommand":
        """
        Configure timestamp display for command output.

        Enable or disable timestamps in command results.

        Parameters
        ----------
        enabled : bool, default=True
            Enable or disable timestamp display.

        Returns
        -------
        Command
            Returns self for method chaining.

        Raises
        ------
        TypeError
            If enabled is not a boolean.
        """

    def description(self, desc: str) -> "ICommand":
        """
        Set description for the command.

        Assign a descriptive text for help and documentation.

        Parameters
        ----------
        desc : str
            Description text for the command.

        Returns
        -------
        Command
            Returns self for method chaining.

        Raises
        ------
        TypeError
            If desc is not a string.
        """

    @abstractmethod
    def arguments(self, args: list) -> "ICommand":
        """
        Set CLI arguments for the command.

        Configure accepted command-line arguments.

        Parameters
        ----------
        args : list
            List of CLIArgument instances.

        Returns
        -------
        Command
            Returns self for method chaining.

        Raises
        ------
        TypeError
            If args is not a list or contains non-CLIArgument elements.
        """

    @abstractmethod
    def get(self) -> tuple[str, CommandEntity]:
        """
        Retrieve configured Command entity.

        Construct and return CommandEntity with all configuration.

        Returns
        -------
        tuple of (str, CommandEntity)
            Command signature and CommandEntity instance.
        """
