from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

class IHelpCommand(ABC):

    @staticmethod
    @abstractmethod
    def parseActions(
        actions: list[argparse.Action],
    ) -> dict[str, Any]:
        """
        Parse argparse actions and categorize them.

        Parameters
        ----------
        actions : list of argparse.Action
            List of argparse actions to parse.

        Returns
        -------
        dict[str, Any]
            Dictionary containing categorized actions: help, positionals,
            optionals, and subcommands.
        """

    @staticmethod
    @abstractmethod
    def printActions(
        command_name: str,
        actions: list[argparse.Action],
    ) -> None:
        """
        Render CLI help information for a command.

        Parameters
        ----------
        command_name : str
            Name of the command to display help for.
        actions : list of argparse.Action
            List of argparse actions to render in the help output.

        Returns
        -------
        None
            This function prints help information to the console and returns None.
        """
