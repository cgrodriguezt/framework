from orionis.console.contracts.console import IConsole

class DummyConsole(IConsole):

    def __init__(self):
        """
        Initializes a new instance of the DummyConsole class.

        This constructor sets up an empty list to store output messages.

        Returns
        -------
        None
        """
        self.output = []

    def newLine(self):
        """
        Appends a newline character to the output list.

        This method simulates adding a new line in the console output.

        Returns
        -------
        None
        """
        self.output.append("\n")

    def exception(self, exc):
        """
        Appends an exception message to the output list.

        Parameters
        ----------
        exc : Exception
            The exception to be recorded.

        Returns
        -------
        None
        """
        self.output.append(f"Exception: {exc}")

    def anticipate(self, *args, **kwargs):
        """
        Placeholder for anticipating user input.

        This method does nothing in the dummy implementation.

        Returns
        -------
        None
        """
        pass

    def ask(self, *args, **kwargs):
        """
        Simulates asking the user for input.

        Returns
        -------
        str
            An empty string, as no input is actually collected.
        """
        return ""

    def choice(self, *args, **kwargs):
        """
        Simulates presenting a choice to the user.

        Returns
        -------
        str
            An empty string, as no choice is actually made.
        """
        return ""

    def clear(self):
        """
        Placeholder for clearing the console.

        This method does nothing in the dummy implementation.

        Returns
        -------
        None
        """
        pass

    def clearLine(self):
        """
        Placeholder for clearing the current line in the console.

        This method does nothing in the dummy implementation.

        Returns
        -------
        None
        """
        pass

    def confirm(self, *args, **kwargs):
        """
        Simulates asking the user for confirmation.

        Returns
        -------
        bool
            Always returns True, as confirmation is assumed.
        """
        return True

    def error(self, msg):
        """
        Appends an error message to the output list.

        Parameters
        ----------
        msg : str
            The error message to be recorded.

        Returns
        -------
        None
        """
        self.output.append(f"Error: {msg}")

    def exitError(self, *args, **kwargs):
        """
        Placeholder for handling an error exit.

        This method does nothing in the dummy implementation.

        Returns
        -------
        None
        """
        pass

    def exitSuccess(self, *args, **kwargs):
        """
        Placeholder for handling a successful exit.

        This method does nothing in the dummy implementation.

        Returns
        -------
        None
        """
        pass

    def fail(self, msg):
        """
        Appends a failure message to the output list.

        Parameters
        ----------
        msg : str
            The failure message to be recorded.

        Returns
        -------
        None
        """
        self.output.append(f"Fail: {msg}")

    def info(self, msg):
        """
        Appends an informational message to the output list.

        Parameters
        ----------
        msg : str
            The informational message to be recorded.

        Returns
        -------
        None
        """
        self.output.append(f"Info: {msg}")

    def line(self, msg=""):
        """
        Appends a message to the output list.

        Parameters
        ----------
        msg : str, optional
            The message to be recorded. Defaults to an empty string.

        Returns
        -------
        None
        """
        self.output.append(msg)

    def secret(self, *args, **kwargs):
        """
        Simulates asking the user for secret input.

        Returns
        -------
        str
            An empty string, as no secret input is actually collected.
        """
        return ""

    def success(self, msg):
        """
        Appends a success message to the output list.

        Parameters
        ----------
        msg : str
            The success message to be recorded.

        Returns
        -------
        None
        """
        self.output.append(f"Success: {msg}")

    def table(self, *args, **kwargs):
        """
        Placeholder for displaying a table in the console.

        This method does nothing in the dummy implementation.

        Returns
        -------
        None
        """
        pass

    def textError(self, msg):
        """
        Formats an error message with an error tag.

        Parameters
        ----------
        msg : str
            The error message to be formatted.

        Returns
        -------
        str
            The formatted error message.
        """
        return f"[ERROR] {msg}"

    def textErrorBold(self, msg):
        """
        Formats an error message with a bold error tag.

        Parameters
        ----------
        msg : str
            The error message to be formatted.

        Returns
        -------
        str
            The formatted bold error message.
        """
        return f"[ERROR BOLD] {msg}"

    def textInfo(self, msg):
        """
        Formats an informational message with an info tag.

        Parameters
        ----------
        msg : str
            The informational message to be formatted.

        Returns
        -------
        str
            The formatted informational message.
        """
        return f"[INFO] {msg}"

    def textInfoBold(self, msg):
        """
        Formats an informational message with a bold info tag.

        Parameters
        ----------
        msg : str
            The informational message to be formatted.

        Returns
        -------
        str
            The formatted bold informational message.
        """
        return f"[INFO BOLD] {msg}"

    def textMuted(self, msg):
        """
        Formats a message with a muted tag.

        Parameters
        ----------
        msg : str
            The message to be formatted.

        Returns
        -------
        str
            The formatted muted message.
        """
        return f"[MUTED] {msg}"

    def textMutedBold(self, msg):
        """
        Formats a message with a bold muted tag.

        Parameters
        ----------
        msg : str
            The message to be formatted.

        Returns
        -------
        str
            The formatted bold muted message.
        """
        return f"[MUTED BOLD] {msg}"

    def textSuccess(self, msg):
        """
        Formats a success message with a success tag.

        Parameters
        ----------
        msg : str
            The success message to be formatted.

        Returns
        -------
        str
            The formatted success message.
        """
        return f"[SUCCESS] {msg}"

    def textSuccessBold(self, msg):
        """
        Formats a success message with a bold success tag.

        Parameters
        ----------
        msg : str
            The success message to be formatted.

        Returns
        -------
        str
            The formatted bold success message.
        """
        return f"[SUCCESS BOLD] {msg}"

    def textUnderline(self, msg):
        """
        Formats a message with an underline tag.

        Parameters
        ----------
        msg : str
            The message to be formatted.

        Returns
        -------
        str
            The formatted underlined message.
        """
        return f"[UNDERLINE] {msg}"

    def textWarning(self, msg):
        """
        Formats a warning message with a warning tag.

        Parameters
        ----------
        msg : str
            The warning message to be formatted.

        Returns
        -------
        str
            The formatted warning message.
        """
        return f"[WARNING] {msg}"

    def textWarningBold(self, msg):
        """
        Formats a warning message with a bold warning tag.

        Parameters
        ----------
        msg : str
            The warning message to be formatted.

        Returns
        -------
        str
            The formatted bold warning message.
        """
        return f"[WARNING BOLD] {msg}"

    def warning(self, msg):
        """
        Appends a warning message to the output list.

        Parameters
        ----------
        msg : str
            The warning message to be recorded.

        Returns
        -------
        None
        """
        self.output.append(f"Warning: {msg}")

    def write(self, msg):
        """
        Appends a message to the output list.

        Parameters
        ----------
        msg : str
            The message to be recorded.

        Returns
        -------
        None
        """
        self.output.append(msg)

    def writeLine(self, msg=""):
        """
        Appends a message followed by a newline character to the output list.

        Parameters
        ----------
        msg : str, optional
            The message to be recorded. Defaults to an empty string.

        Returns
        -------
        None
        """
        self.output.append(f"{msg}\n")