from __future__ import annotations
from abc import ABC, abstractmethod

class IConsole(ABC):

    @abstractmethod
    def success(self, message: str, *, timestamp: bool = True) -> None:
        """
        Print a success message with a green background.

        Parameters
        ----------
        message : str
            Success message to print.
        timestamp : bool, optional
            If True, include a timestamp. Default is True.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def textSuccess(self, message: str) -> None:
        """
        Print a success message in green.

        Parameters
        ----------
        message : str
            Success message to print.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for non-bold success messages.
        """

    @abstractmethod
    def textSuccessBold(self, message: str) -> None:
        """
        Print a bold success message in green.

        Parameters
        ----------
        message : str
            Success message to print.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for bold success messages.
        """

    @abstractmethod
    def info(self, message: str, *, timestamp: bool = True) -> None:
        """
        Print informational message with blue background.

        Parameters
        ----------
        message : str
            Informational message to display.
        timestamp : bool, optional
            If True, include timestamp in output. Default is True.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for general informational output.
        """

    @abstractmethod
    def textInfo(self, message: str) -> None:
        """
        Print informational message in blue.

        Parameters
        ----------
        message : str
            Informational message to print.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for non-bold informational output.
        """

    @abstractmethod
    def textInfoBold(self, message: str) -> None:
        """
        Print bold informational message in blue.

        Parameters
        ----------
        message : str
            Informational message to print.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for bold informational output.
        """

    @abstractmethod
    def warning(self, message: str, *, timestamp: bool = True) -> None:
        """
        Print a warning message with a yellow background.

        Parameters
        ----------
        message : str
            Warning message to print.
        timestamp : bool, optional
            If True, include a timestamp. Default is True.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for general warning output.
        """

    @abstractmethod
    def textWarning(self, message: str) -> None:
        """
        Print warning message in yellow.

        Parameters
        ----------
        message : str
            Warning message to print.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def textWarningBold(self, message: str) -> None:
        """
        Print bold warning message in yellow.

        Parameters
        ----------
        message : str
            Warning message to print.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for bold warning output.
        """

    @abstractmethod
    def fail(self, message: str, *, timestamp: bool = True) -> None:
        """
        Print a failure message with a red background.

        Parameters
        ----------
        message : str
            Failure message to print.
        timestamp : bool, optional
            If True, include a timestamp. Default is True.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for general failure output.
        """

    @abstractmethod
    def error(self, message: str, *, timestamp: bool = True) -> None:
        """
        Print an error message with a red background.

        Parameters
        ----------
        message : str
            Error message to print.
        timestamp : bool, optional
            If True, include a timestamp. Default is True.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for general error output.
        """

    @abstractmethod
    def textError(self, message: str) -> None:
        """
        Print error message in red.

        Parameters
        ----------
        message : str
            Error message to print.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for non-bold error output.
        """

    @abstractmethod
    def textErrorBold(self, message: str) -> None:
        """
        Print a bold error message in red.

        Parameters
        ----------
        message : str
            Error message to print.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use for bold error output.
        """

    @abstractmethod
    def textMuted(self, message: str) -> None:
        """
        Print a muted (gray) message.

        Parameters
        ----------
        message : str
            Message to print.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def textMutedBold(self, message: str) -> None:
        """
        Print a bold muted (gray) message.

        Parameters
        ----------
        message : str
            Message to print.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def textUnderline(self, message: str) -> None:
        """
        Print an underlined message.

        Parameters
        ----------
        message : str
            Message to print.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the console screen.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def clearLine(self) -> None:
        """
        Clear the current line in the console.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def line(self) -> None:
        """
        Print a horizontal line in the console.

        Returns
        -------
        None
            This method does not return a value.
        """

    @abstractmethod
    def newLine(self, count: int = 1) -> None:
        """
        Print multiple new lines.

        Parameters
        ----------
        count : int, optional
            Number of new lines to print (default is 1).

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If count is less than or equal to 0.
        """

    @abstractmethod
    def write(self, message: str) -> None:
        """
        Print a message without moving to the next line.

        Parameters
        ----------
        message : str
            Message to print.

        Returns
        -------
        None
            No value is returned.

        """

    @abstractmethod
    def writeLine(self, message: str) -> None:
        """
        Print a message and move to the next line.

        Parameters
        ----------
        message : str
            Message to print.

        Returns
        -------
        None
            No value is returned.

        """

    @abstractmethod
    def ask(self, question: str) -> str:
        """
        Prompt the user for input and return the response.

        Parameters
        ----------
        question : str
            Question to display to the user.

        Returns
        -------
        str
            The user's input as a string.

        """

    @abstractmethod
    def confirm(self, question: str, *, default: bool = False) -> bool:
        """
        Ask for confirmation and return True or False.

        Parameters
        ----------
        question : str
            Confirmation prompt for the user.
        default : bool, optional
            Default response if user presses Enter. False means 'No'.

        Returns
        -------
        bool
            True if user confirms ('Y'), False otherwise.

        Notes
        -----
        The method prompts the user for a yes/no answer.
        """

    @abstractmethod
    def secret(self, question: str) -> str:
        """
        Prompt for hidden input from the user.

        Parameters
        ----------
        question : str
            The prompt to display to the user.

        Returns
        -------
        str
            The user's hidden input as a string.

        Notes
        -----
        Use this method for sensitive input such as passwords.
        """

    @abstractmethod
    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        """
        Print a formatted table with bold headers.

        Parameters
        ----------
        headers : list of str
            Column headers for the table.
        rows : list of list of str
            Table rows, each as a list of column values.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If headers or rows are empty.

        Notes
        -----
        The table adjusts column widths and uses box-drawing characters.
        Headers are bolded for emphasis.
        """

    @abstractmethod
    def anticipate(
        self,
        question: str,
        options: list[str],
        default: str | None = None,
    ) -> str:
        """
        Provide autocomplete suggestions for user input.

        Parameters
        ----------
        question : str
            Prompt displayed to the user.
        options : list of str
            List of possible autocomplete options.
        default : str or None, optional
            Value returned if no match is found. Defaults to None.

        Returns
        -------
        str
            Returns the selected option if matched, otherwise the
            default value or user input.

        Notes
        -----
        Matches the start of user input with available options.
        Returns the default value or user input if no match is found.
        """

    @abstractmethod
    def choice(self, question: str, choices: list[str], default_index: int = 0) -> str:
        """
        Prompt user to select an option from a list.

        Parameters
        ----------
        question : str
            Prompt displayed to the user.
        choices : list of str
            List of available choices.
        default_index : int, optional
            Index of the default choice (zero-based). Default is 0.

        Returns
        -------
        str
            Selected choice as a string.

        Raises
        ------
        ValueError
            If `default_index` is not a valid index for `choices`.

        Notes
        -----
        User is shown a numbered list and prompted to select by number.
        Invalid input prompts user again until a valid choice is made.
        """

    @abstractmethod
    def exception(self, e: Exception) -> None:
        """
        Print exception details and stack trace.

        Parameters
        ----------
        e : Exception
            Exception instance to display.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Shows exception type, message, and stack trace.
        """

    @abstractmethod
    def exitSuccess(self, message: str | None = None) -> None:
        """
        Exit the program with a success message.

        Parameters
        ----------
        message : str or None, optional
            Success message to print before exiting.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Use this method to terminate the program after successful execution.
        """

    @abstractmethod
    def exitError(self, message: str | None = None) -> None:
        """
        Exit the program with an error message.

        Parameters
        ----------
        message : str or None, optional
            Error message to print before exiting.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Terminates execution after displaying the error message.
        """

    # ruff: noqa: PLR0913
    @abstractmethod
    def dump(
        self,
        *args: object,
        show_types: bool = True,
        show_index: bool = False,
        expand_all: bool = True,
        max_depth: int | None = None,
        module_path: str | None = None,
        line_number: int | None = None,
        force_exit: bool = False,
        redirect_output: bool = False,
        insert_line: bool = False,
    ) -> str | None:
        """
        Display formatted debug information for variables using Rich.

        Parameters
        ----------
        *args : Any
            Objects to display for debugging.
        show_types : bool, optional
            If True, show type of each argument in panel title.
        show_index : bool, optional
            If True, show index number for each argument.
        expand_all : bool, optional
            If True, expand all nested data structures.
        max_depth : int or None, optional
            Maximum depth for nested structures.
        module_path : str or None, optional
            Module path shown in header.
        line_number : int or None, optional
            Line number shown in header.
        force_exit : bool, optional
            If True, terminate program after dumping.
        redirect_output : bool, optional
            If True, restore stdout/stderr during output.
        insert_line : bool, optional
            If True, insert blank line before and after output.

        Returns
        -------
        str or None
            The formatted debug output as a string if redirected, otherwise None.

        Notes
        -----
        Use Rich to display variables with type and index info.
        """
