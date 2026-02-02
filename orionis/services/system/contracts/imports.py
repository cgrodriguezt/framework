from __future__ import annotations
from abc import ABC, abstractmethod

class IImports(ABC):

    @abstractmethod
    def collect(self) -> IImports:
        """
        Collect information about user-defined Python modules currently loaded.

        Iterates through all modules in `sys.modules` and gathers details for each
        qualifying module: module name, relative file path, and list of symbols
        (functions, classes, or submodules) defined in the module.

        Parameters
        ----------
        None

        Returns
        -------
        Imports
            The current instance of `Imports` with the `imports` attribute updated
            to include information about the collected modules.
        """

    @abstractmethod
    def display(self) -> None:
        """
        Display a formatted table of collected import statements.

        Shows a summary of all collected user-defined Python modules. If imports
        are not yet collected, calls `self.collect()` automatically. The output
        is rendered as a table inside a styled panel in the console, listing each
        module's name, relative file path, and defined symbols.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method outputs the formatted table to the console and does not
            return any value.
        """

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all entries from the collected imports list.

        Removes all items from the `imports` attribute, resetting its state.

        Returns
        -------
        None
            This method does not return any value. The `imports` list is emptied.
        """
