from __future__ import annotations
import io
import sys
from unittest.mock import MagicMock, patch
from orionis.console.dynamic.contracts.progress_bar import IProgressBar
from orionis.console.output.console import Console
from orionis.test import TestCase


class TestConsole(TestCase):

    # ------------------------------------------------------------------ #
    #  Instantiation & property                                          #
    # ------------------------------------------------------------------ #

    def testInstantiation(self) -> None:
        """
        Verify that Console can be instantiated without arguments.

        Ensures the constructor does not raise any exception and returns
        a valid Console instance.
        """
        console = Console()
        self.assertIsInstance(console, Console)

    def testProgressBarReturnsIProgressBarInstance(self) -> None:
        """
        Verify that the progressBar property returns an IProgressBar instance.

        Ensures that every access to the property produces a new object
        that satisfies the IProgressBar interface contract.
        """
        console = Console()
        pb = console.progressBar
        self.assertIsInstance(pb, IProgressBar)

    def testProgressBarReturnsFreshInstanceOnEachAccess(self) -> None:
        """
        Verify that progressBar returns a new instance on every access.

        Ensures the property does not cache the object so callers always
        obtain an independent ProgressBar.
        """
        console = Console()
        self.assertIsNot(console.progressBar, console.progressBar)

    # ------------------------------------------------------------------ #
    #  Background-color output methods                                   #
    # ------------------------------------------------------------------ #

    def testSuccessCallsPrintWithoutError(self) -> None:
        """
        Verify that success() prints without raising any exception.

        Ensures the method completes under normal conditions using a
        standard message string.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.success("Operation completed")
            mock_print.assert_called_once()

    def testSuccessWithTimestampFalse(self) -> None:
        """
        Verify that success() respects the timestamp=False parameter.

        Ensures the method still prints exactly once when timestamp is
        disabled, confirming the flag does not suppress output.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.success("msg", timestamp=False)
            mock_print.assert_called_once()

    def testInfoCallsPrint(self) -> None:
        """
        Verify that info() prints without raising any exception.

        Ensures the method delegates to print for a standard message.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.info("Some info")
            mock_print.assert_called_once()

    def testWarningCallsPrint(self) -> None:
        """
        Verify that warning() prints without raising any exception.

        Ensures the method delegates to print for a standard message.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.warning("A warning")
            mock_print.assert_called_once()

    def testFailCallsPrint(self) -> None:
        """
        Verify that fail() prints without raising any exception.

        Ensures the method delegates to print for a standard message.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.fail("Failure occurred")
            mock_print.assert_called_once()

    def testErrorCallsPrint(self) -> None:
        """
        Verify that error() prints without raising any exception.

        Ensures the method delegates to print for a standard message.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.error("An error")
            mock_print.assert_called_once()

    # ------------------------------------------------------------------ #
    #  Colored text output methods                                       #
    # ------------------------------------------------------------------ #

    def testTextSuccessCallsPrint(self) -> None:
        """
        Verify that textSuccess() calls print exactly once.

        Ensures the method produces exactly one line of colored output
        for any non-empty message string.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textSuccess("ok")
            mock_print.assert_called_once()

    def testTextSuccessBoldCallsPrint(self) -> None:
        """
        Verify that textSuccessBold() calls print exactly once.

        Ensures bold variant produces output without raising exceptions.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textSuccessBold("ok")
            mock_print.assert_called_once()

    def testTextInfoCallsPrint(self) -> None:
        """
        Verify that textInfo() calls print exactly once.

        Ensures the informational text method produces a single line
        of output for a standard message.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textInfo("note")
            mock_print.assert_called_once()

    def testTextInfoBoldCallsPrint(self) -> None:
        """
        Verify that textInfoBold() calls print exactly once.

        Ensures bold informational variant completes without errors.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textInfoBold("note")
            mock_print.assert_called_once()

    def testTextWarningCallsPrint(self) -> None:
        """
        Verify that textWarning() calls print exactly once.

        Ensures the warning text method produces output without raising
        any exceptions.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textWarning("warn")
            mock_print.assert_called_once()

    def testTextWarningBoldCallsPrint(self) -> None:
        """
        Verify that textWarningBold() calls print exactly once.

        Ensures bold warning variant completes and calls print.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textWarningBold("warn")
            mock_print.assert_called_once()

    def testTextErrorCallsPrint(self) -> None:
        """
        Verify that textError() calls print exactly once.

        Ensures the error text method delegates to print for a
        standard message.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textError("err")
            mock_print.assert_called_once()

    def testTextErrorBoldCallsPrint(self) -> None:
        """
        Verify that textErrorBold() calls print exactly once.

        Ensures the bold error variant completes without exceptions.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textErrorBold("err")
            mock_print.assert_called_once()

    def testTextMutedCallsPrint(self) -> None:
        """
        Verify that textMuted() calls print exactly once.

        Ensures the muted (gray) text variant produces output without errors.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textMuted("muted")
            mock_print.assert_called_once()

    def testTextMutedBoldCallsPrint(self) -> None:
        """
        Verify that textMutedBold() calls print exactly once.

        Ensures the bold muted text variant produces output without errors.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textMutedBold("muted bold")
            mock_print.assert_called_once()

    def testTextUnderlineCallsPrint(self) -> None:
        """
        Verify that textUnderline() calls print exactly once.

        Ensures the underlined text variant delegates to print for
        a standard message.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.textUnderline("underlined")
            mock_print.assert_called_once()

    # ------------------------------------------------------------------ #
    #  Screen / line control methods                                     #
    # ------------------------------------------------------------------ #

    def testClearCallsOsSystem(self) -> None:
        """
        Verify that clear() calls os.system once.

        Ensures the implementation delegates the screen-clearing action
        to the OS command (cls on Windows, clear elsewhere).
        """
        console = Console()
        with patch("os.system") as mock_sys:
            console.clear()
            mock_sys.assert_called_once()

    def testClearLineWritesToStdout(self) -> None:
        """
        Verify that clearLine() writes the carriage-return sequence to stdout.

        Ensures the cursor-reset escape sequence is written to the
        standard output stream.
        """
        console = Console()
        fake_stdout = io.StringIO()
        with patch.object(sys, "stdout", fake_stdout):
            console.clearLine()
        self.assertIn("\r", fake_stdout.getvalue())

    def testLineCallsPrint(self) -> None:
        """
        Verify that line() calls print exactly once with a newline.

        Ensures a visual separator is produced by a single print call.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.line()
            mock_print.assert_called_once()

    def testNewLineDefaultCount(self) -> None:
        """
        Verify that newLine() calls print once with the default count of 1.

        Ensures the default parameter produces exactly one print call.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.newLine()
            mock_print.assert_called_once()

    def testNewLineCustomCount(self) -> None:
        """
        Verify that newLine(3) calls print once with three newline characters.

        Ensures a count greater than 1 still results in a single print
        containing the requested number of newlines.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.newLine(3)
            mock_print.assert_called_once()

    def testNewLineZeroRaisesValueError(self) -> None:
        """
        Verify that newLine(0) raises a ValueError.

        Ensures the boundary condition of count=0 is rejected as an
        invalid value.
        """
        console = Console()
        with self.assertRaises(ValueError):
            console.newLine(0)

    def testNewLineNegativeRaisesValueError(self) -> None:
        """
        Verify that newLine with a negative count raises a ValueError.

        Ensures that any non-positive count is rejected to prevent
        nonsensical output.
        """
        console = Console()
        with self.assertRaises(ValueError):
            console.newLine(-5)

    # ------------------------------------------------------------------ #
    #  write / writeLine                                                 #
    # ------------------------------------------------------------------ #

    def testWriteCallsPrint(self) -> None:
        """
        Verify that write() delegates to the built-in print function.

        Ensures output is produced for a basic string argument.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.write("hello")
            mock_print.assert_called_once()

    def testWritePassesSeparatorAndEnd(self) -> None:
        """
        Verify that write() forwards sep and end to print.

        Ensures custom separator and end characters are passed through
        correctly so callers can control output formatting.
        """
        console = Console()
        buf = io.StringIO()
        console.write("a", "b", sep="-", end="!", file=buf)
        self.assertEqual(buf.getvalue(), "a-b!")

    def testWriteLineCallsPrint(self) -> None:
        """
        Verify that writeLine() calls print exactly once.

        Ensures a single message is forwarded to print with a trailing
        newline as expected.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.writeLine("a line")
            mock_print.assert_called_once()

    # ------------------------------------------------------------------ #
    #  Input methods                                                     #
    # ------------------------------------------------------------------ #

    def testAskReturnsUserInput(self) -> None:
        """
        Verify that ask() returns the text entered by the user.

        Ensures the user's response is forwarded as the return value
        without any transformation.
        """
        console = Console()
        with patch("builtins.input", return_value="my answer"):
            result = console.ask("What is your name?")
        self.assertEqual(result, "my answer")

    def testConfirmReturnsTrueForY(self) -> None:
        """
        Verify that confirm() returns True when the user enters 'Y'.

        Ensures correct interpretation of an affirmative response.
        """
        console = Console()
        with patch("builtins.input", return_value="Y"):
            result = console.confirm("Continue?")
        self.assertTrue(result)

    def testConfirmReturnsTrueForYes(self) -> None:
        """
        Verify that confirm() returns True when the user enters 'YES'.

        Ensures both the short and long form of affirmation are accepted.
        """
        console = Console()
        with patch("builtins.input", return_value="yes"):
            result = console.confirm("Continue?")
        self.assertTrue(result)

    def testConfirmReturnsFalseForN(self) -> None:
        """
        Verify that confirm() returns False when the user enters 'N'.

        Ensures a negative response yields False regardless of default.
        """
        console = Console()
        with patch("builtins.input", return_value="N"):
            result = console.confirm("Continue?")
        self.assertFalse(result)

    def testConfirmUsesDefaultWhenEmpty(self) -> None:
        """
        Verify that confirm() returns the default value on empty input.

        Ensures that pressing Enter (empty string) falls back to the
        supplied default parameter.
        """
        console = Console()
        with patch("builtins.input", return_value=""):
            result_false = console.confirm("Continue?", default=False)
            result_true  = console.confirm("Continue?", default=True)
        self.assertFalse(result_false)
        self.assertTrue(result_true)

    def testSecretReturnsHiddenInput(self) -> None:
        """
        Verify that secret() returns the value provided by getpass.

        Ensures the method delegates to getpass.getpass and returns
        the hidden input without modification.
        """
        console = Console()
        with patch("getpass.getpass", return_value="s3cr3t"):
            result = console.secret("Password:")
        self.assertEqual(result, "s3cr3t")

    # ------------------------------------------------------------------ #
    #  table                                                             #
    # ------------------------------------------------------------------ #

    def testTablePrintsWithValidData(self) -> None:
        """
        Verify that table() prints without raising for valid input.

        Ensures the method completes successfully and calls print
        for a minimal 1-column, 1-row table.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.table(["Name"], [["Alice"]])
            self.assertTrue(mock_print.called)

    def testTableRaisesForEmptyHeaders(self) -> None:
        """
        Verify that table() raises ValueError when headers are empty.

        Ensures the guard against empty column definitions is active
        and provides useful feedback to the caller.
        """
        console = Console()
        with self.assertRaises(ValueError):
            console.table([], [["Alice"]])

    def testTableRaisesForEmptyRows(self) -> None:
        """
        Verify that table() raises ValueError when rows are empty.

        Ensures the guard against empty row data is active and provides
        useful feedback to the caller.
        """
        console = Console()
        with self.assertRaises(ValueError):
            console.table(["Name"], [])

    def testTableMultipleColumnsAndRows(self) -> None:
        """
        Verify that table() handles multiple columns and multiple rows.

        Ensures the method produces output for a 2-column, 2-row table
        without raising any exception.
        """
        console = Console()
        with patch("builtins.print") as mock_print:
            console.table(
                ["ID", "Value"],
                [["1", "alpha"], ["2", "beta"]],
            )
            self.assertTrue(mock_print.called)

    # ------------------------------------------------------------------ #
    #  anticipate                                                        #
    # ------------------------------------------------------------------ #

    def testAnticipateReturnsMatchingOption(self) -> None:
        """
        Verify that anticipate() returns the first matching option.

        Ensures the autocomplete logic selects the correct option when
        user input is a prefix of one of the available choices.
        """
        console = Console()
        with patch("builtins.input", return_value="Py"):
            result = console.anticipate("Language?", ["Python", "PHP", "Ruby"])
        self.assertEqual(result, "Python")

    def testAnticipateReturnsDefaultWhenNoMatch(self) -> None:
        """
        Verify that anticipate() returns the default when no option matches.

        Ensures that unrecognised input falls back to the caller-supplied
        default value instead of raising an exception.
        """
        console = Console()
        with patch("builtins.input", return_value="Go"):
            result = console.anticipate("Language?", ["Python", "PHP"], default="unknown")
        self.assertEqual(result, "unknown")

    def testAnticipateReturnsInputWhenNoMatchAndNoDefault(self) -> None:
        """
        Verify that anticipate() returns raw input when no match and no default.

        Ensures the method falls back to the user's input string when neither
        a matching option nor a default value is available.
        """
        console = Console()
        with patch("builtins.input", return_value="Rust"):
            result = console.anticipate("Language?", ["Python", "PHP"])
        self.assertEqual(result, "Rust")

    # ------------------------------------------------------------------ #
    #  choice                                                            #
    # ------------------------------------------------------------------ #

    def testChoiceReturnsSelectedOption(self) -> None:
        """
        Verify that choice() returns the correctly selected option.

        Ensures that entering a valid 1-based index returns the
        corresponding item from the choices list.
        """
        console = Console()
        with patch("builtins.input", return_value="2"):
            result = console.choice("Pick one:", ["alpha", "beta", "gamma"])
        self.assertEqual(result, "beta")

    def testChoiceReturnsDefaultOnEmptyInput(self) -> None:
        """
        Verify that choice() returns the default option on empty input.

        Ensures pressing Enter (empty string) selects the item at
        default_index without requiring explicit confirmation.
        """
        console = Console()
        with patch("builtins.input", return_value=""):
            result = console.choice("Pick one:", ["alpha", "beta"], default_index=1)
        self.assertEqual(result, "beta")

    def testChoiceRaisesForEmptyList(self) -> None:
        """
        Verify that choice() raises ValueError for an empty choices list.

        Ensures the guard against an empty option set is active so callers
        receive actionable feedback.
        """
        console = Console()
        with self.assertRaises(ValueError):
            console.choice("Pick one:", [])

    def testChoiceRaisesForOutOfRangeDefaultIndex(self) -> None:
        """
        Verify that choice() raises ValueError for an invalid default_index.

        Ensures that a default_index outside the valid range is rejected
        before any user interaction occurs.
        """
        console = Console()
        with self.assertRaises(ValueError):
            console.choice("Pick one:", ["alpha"], default_index=5)

    def testChoiceLoopsOnInvalidInput(self) -> None:
        """
        Verify that choice() re-prompts for invalid input before accepting valid.

        Ensures the while-loop guard rejects non-numeric and out-of-range
        input and eventually returns the correct selection.
        """
        console = Console()
        # First two responses are invalid; third is valid
        with patch("builtins.input", side_effect=["abc", "99", "1"]):
            result = console.choice("Pick one:", ["alpha", "beta"])
        self.assertEqual(result, "alpha")

    # ------------------------------------------------------------------ #
    #  exception                                                         #
    # ------------------------------------------------------------------ #

    def testExceptionPrintsTracebackForValidException(self) -> None:
        """
        Verify that exception() prints traceback for a valid Exception.

        Ensures the method completes without error when given a properly
        raised exception, delegating rendering to the Rich console.
        """
        console = Console()
        try:
            raise ValueError("something went wrong")
        except ValueError as exc:
            captured = exc
        # Should not raise
        with patch("orionis.console.output.console.RichConsole") as MockRich:
            mock_instance = MagicMock()
            MockRich.return_value = mock_instance
            console.exception(captured)
            mock_instance.print.assert_called_once()

    def testExceptionRaisesTypeErrorForNonException(self) -> None:
        """
        Verify that exception() raises TypeError when given a non-Exception.

        Ensures the type guard is active so callers receive meaningful
        feedback when a non-exception object is passed.
        """
        console = Console()
        with self.assertRaises(TypeError):
            console.exception("not an exception")  # type: ignore[arg-type]

    # ------------------------------------------------------------------ #
    #  exitSuccess / exitError                                           #
    # ------------------------------------------------------------------ #

    def testExitSuccessCallsSysExit(self) -> None:
        """
        Verify that exitSuccess() calls sys.exit(0).

        Ensures the method always invokes sys.exit with exit code 0,
        regardless of whether a message is provided.
        """
        console = Console()
        with patch("sys.exit") as mock_exit, patch("os._exit"):
            console.exitSuccess()
        mock_exit.assert_called_once_with(0)

    def testExitSuccessWithMessage(self) -> None:
        """
        Verify that exitSuccess() prints the success message before exiting.

        Ensures the optional message is displayed to the user prior to the
        process termination call.
        """
        console = Console()
        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit, patch("os._exit"):
            console.exitSuccess("Done!")
        mock_exit.assert_called_once_with(0)
        mock_print.assert_called()

    def testExitErrorCallsSysExit(self) -> None:
        """
        Verify that exitError() calls sys.exit(1).

        Ensures the method always invokes sys.exit with exit code 1
        upon invocation.
        """
        console = Console()
        with patch("sys.exit") as mock_exit, patch("os._exit"):
            console.exitError()
        mock_exit.assert_called_once_with(1)

    def testExitErrorWithMessage(self) -> None:
        """
        Verify that exitError() prints the error message before exiting.

        Ensures the error output is produced before the system exit is
        triggered.
        """
        console = Console()
        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit, patch("os._exit"):
            console.exitError("Fatal error!")
        mock_exit.assert_called_once_with(1)
        mock_print.assert_called()

    # ------------------------------------------------------------------ #
    #  dump                                                              #
    # ------------------------------------------------------------------ #

    def testDumpDoesNotRaiseForSimpleValue(self) -> None:
        """
        Verify that dump() completes without raising for a simple value.

        Ensures the VarDumper chain executes end-to-end when given a
        single basic Python object.
        """
        console = Console()
        with patch("orionis.console.output.console.VarDumper") as MockDumper:
            mock_chain = MagicMock()
            MockDumper.return_value = mock_chain
            # Chain all fluent methods and the final .print()
            mock_chain.showTypes.return_value = mock_chain
            mock_chain.showIndex.return_value = mock_chain
            mock_chain.expandAll.return_value = mock_chain
            mock_chain.maxDepth.return_value = mock_chain
            mock_chain.modulePath.return_value = mock_chain
            mock_chain.lineNumber.return_value = mock_chain
            mock_chain.redirectOutput.return_value = mock_chain
            mock_chain.forceExit.return_value = mock_chain
            mock_chain.values.return_value = mock_chain
            mock_chain.print.return_value = None
            console.dump(42)
            mock_chain.print.assert_called_once()

    def testDumpForwardsOptions(self) -> None:
        """
        Verify that dump() forwards all keyword options to VarDumper.

        Ensures that non-default values supplied by the caller are passed
        through the fluent builder chain to the underlying VarDumper.
        """
        console = Console()
        with patch("orionis.console.output.console.VarDumper") as MockDumper:
            mock_chain = MagicMock()
            MockDumper.return_value = mock_chain
            mock_chain.showTypes.return_value = mock_chain
            mock_chain.showIndex.return_value = mock_chain
            mock_chain.expandAll.return_value = mock_chain
            mock_chain.maxDepth.return_value = mock_chain
            mock_chain.modulePath.return_value = mock_chain
            mock_chain.lineNumber.return_value = mock_chain
            mock_chain.redirectOutput.return_value = mock_chain
            mock_chain.forceExit.return_value = mock_chain
            mock_chain.values.return_value = mock_chain
            mock_chain.print.return_value = None
            console.dump(
                "data",
                show_types=False,
                show_index=True,
                expand_all=False,
                max_depth=3,
                module_path="/some/path.py",
                line_number=10,
                force_exit=True,
                redirect_output=True,
                insert_line=True,
            )
            mock_chain.showTypes.assert_called_once_with(show=False)
            mock_chain.showIndex.assert_called_once_with(show=True)
            mock_chain.forceExit.assert_called_once_with(force=True)
