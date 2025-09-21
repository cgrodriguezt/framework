from orionis.console.contracts.console import IConsole

class DummyConsole(IConsole):
    """
    Dummy implementation of IConsole for testing purposes.

    This class provides a mock implementation of the IConsole interface, intended for use in unit tests.
    Each method records its invocation and arguments in the `calls` list, allowing test assertions on
    console interactions without producing actual output.

    Methods
    -------
    All methods record their calls and arguments to `self.calls` for later inspection.

    Returns
    -------
    None
        All methods return None unless otherwise specified (e.g., ask, confirm, secret, anticipate, choice).
    """
    def __init__(self):
        # Stores a list of tuples representing method calls and their arguments
        self.calls = []

    def success(self, message: str, timestamp: bool = True) -> None:
        # Record a success message call
        self.calls.append(('success', message, timestamp))

    def textSuccess(self, message: str) -> None:
        # Record a plain success text message call
        self.calls.append(('textSuccess', message))

    def textSuccessBold(self, message: str) -> None:
        # Record a bold success text message call
        self.calls.append(('textSuccessBold', message))

    def info(self, message: str, timestamp: bool = True) -> None:
        # Record an info message call
        self.calls.append(('info', message, timestamp))

    def textInfo(self, message: str) -> None:
        # Record a plain info text message call
        self.calls.append(('textInfo', message))

    def textInfoBold(self, message: str) -> None:
        # Record a bold info text message call
        self.calls.append(('textInfoBold', message))

    def warning(self, message: str, timestamp: bool = True) -> None:
        # Record a warning message call
        self.calls.append(('warning', message, timestamp))

    def textWarning(self, message: str) -> None:
        # Record a plain warning text message call
        self.calls.append(('textWarning', message))

    def textWarningBold(self, message: str) -> None:
        # Record a bold warning text message call
        self.calls.append(('textWarningBold', message))

    def fail(self, message: str, timestamp: bool = True) -> None:
        # Record a fail message call
        self.calls.append(('fail', message, timestamp))

    def error(self, message: str, timestamp: bool = True) -> None:
        # Record an error message call
        self.calls.append(('error', message, timestamp))

    def textError(self, message: str) -> None:
        # Record a plain error text message call
        self.calls.append(('textError', message))

    def textErrorBold(self, message: str) -> None:
        # Record a bold error text message call
        self.calls.append(('textErrorBold', message))

    def textMuted(self, message: str) -> None:
        # Record a muted text message call
        self.calls.append(('textMuted', message))

    def textMutedBold(self, message: str) -> None:
        # Record a bold muted text message call
        self.calls.append(('textMutedBold', message))

    def textUnderline(self, message: str) -> None:
        # Record an underlined text message call
        self.calls.append(('textUnderline', message))

    def clear(self) -> None:
        # Record a clear screen call
        self.calls.append(('clear',))

    def clearLine(self) -> None:
        # Record a clear line call
        self.calls.append(('clearLine',))

    def line(self) -> None:
        # Record a line separator call
        self.calls.append(('line',))

    def newLine(self, count: int = 1) -> None:
        # Record a new line call with the specified count
        self.calls.append(('newLine', count))

    def write(self, message: str) -> None:
        # Record a write message call
        self.calls.append(('write', message))

    def writeLine(self, message: str) -> None:
        # Record a write line message call
        self.calls.append(('writeLine', message))

    def ask(self, question: str) -> str:
        # Record an ask question call and return a dummy response
        self.calls.append(('ask', question))
        return 'dummy'

    def confirm(self, question: str, default: bool = False) -> bool:
        # Record a confirm question call and return the default value
        self.calls.append(('confirm', question, default))
        return default

    def secret(self, question: str) -> str:
        # Record a secret question call and return a dummy secret
        self.calls.append(('secret', question))
        return 'secret'

    def table(self, headers: list, rows: list) -> None:
        # Record a table display call with headers and rows
        self.calls.append(('table', headers, rows))

    def anticipate(self, question: str, options: list, default: str = None) -> str:
        # Record an anticipate question call and return the default or first option
        self.calls.append(('anticipate', question, options, default))
        return default or (options[0] if options else '')

    def choice(self, question: str, choices: list, default_index: int = 0) -> str:
        # Record a choice question call and return the selected choice
        self.calls.append(('choice', question, choices, default_index))
        return choices[default_index] if choices else ''

    def exception(self, e: Exception) -> None:
        # Record an exception call with the exception message
        self.calls.append(('exception', str(e)))

    def exitSuccess(self, message: str = None) -> None:
        # Record an exit success call with an optional message
        self.calls.append(('exitSuccess', message))

    def exitError(self, message: str = None) -> None:
        # Record an exit error call with an optional message
        self.calls.append(('exitError', message))