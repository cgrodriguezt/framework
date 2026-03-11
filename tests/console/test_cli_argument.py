import argparse
from orionis.console.args.argument import Argument
from orionis.console.enums.actions import ArgumentAction
from orionis.test.cases.case import TestCase
from unittest.mock import patch

class TestCLIArgument(TestCase):

    def testCreateArgumentWithName(self) -> None:
        """
        Create a positional argument using the name parameter.

        Verifies that Argument can be created with a positional name and
        basic type specification.

        Returns
        -------
        None
            This method does not return a value. It asserts correctness of
            Argument initialization.
        """
        # Create a Argument with a positional name and check its attributes
        argument = Argument(
            name="input_file",
            type=str,
            help="Input file path",
        )

        self.assertEqual(argument.name, "input_file")
        self.assertEqual(argument.type, str)
        self.assertEqual(argument.help, "Input file path")
        self.assertFalse(argument.required)

    def testCreateArgumentWithFlags(self) -> None:
        """
        Create an optional argument using the flags parameter.

        Verifies that Argument can be created with optional flags in both
        short and long format.

        Returns
        -------
        None
            This method does not return a value. It asserts correctness of
            Argument initialization.
        """
        # Create a Argument with both long and short flags
        argument = Argument(
            flags=["--output", "-o"],
            type=str,
            help="Output file path",
            required=True,
        )

        self.assertEqual(argument.flags, ["--output", "-o"])
        self.assertEqual(argument.type, str)
        self.assertEqual(argument.help, "Output file path")
        self.assertTrue(argument.required)

    def testCreateArgumentWithSingleFlag(self) -> None:
        """
        Create argument with a single flag as a string.

        Converts a single string flag to a list during argument construction.

        Returns
        -------
        None
            This method asserts correctness of Argument initialization.
        """
        # Create a Argument with a single flag string
        argument = Argument(
            flags="--verbose",
            type=bool,
            help="Enable verbose output",
        )

        self.assertEqual(argument.flags, "--verbose")
        self.assertEqual(argument.type, bool)

    def testCreateArgumentWithDefaults(self) -> None:
        """
        Create an argument with default values.

        Verifies that default values are correctly assigned and stored in the
        Argument instance.

        Returns
        -------
        None
            This method does not return a value. It asserts the correctness of
            Argument initialization with defaults.
        """
        # Create a Argument with default value and check its attributes
        argument = Argument(
            flags=["--count", "-c"],
            type=int,
            default=10,
            help="Number of items",
        )

        self.assertEqual(argument.default, 10)
        self.assertEqual(argument.action, ArgumentAction.STORE.value)
        self.assertFalse(argument.required)

    def testCreateArgumentWithChoices(self) -> None:
        """
        Create argument with predefined choices.

        Create a Argument with a set of allowed choices and verify that the
        choices and default value are correctly stored.

        Returns
        -------
        None
            This method does not return a value. It asserts the correctness of
            Argument initialization with choices.
        """
        # Define allowed choices for the argument
        choices: list[str] = ["debug", "info", "warning", "error"]
        argument = Argument(
            flags=["--log-level"],
            type=str,
            choices=choices,
            default="info",
            help="Set logging level",
        )

        self.assertEqual(argument.choices, choices)
        self.assertEqual(argument.default, "info")

    def testCreateArgumentWithAction(self) -> None:
        """
        Create an argument with a specific action.

        Verifies that different argument actions can be specified and stored
        in the Argument instance.

        Returns
        -------
        None
            This method does not return a value. It asserts the correctness of
            Argument initialization with a specific action.
        """
        # Create a Argument with a specific action and check its attribute
        argument = Argument(
            flags=["--enable-feature"],
            type=bool,
            action=ArgumentAction.STORE_TRUE,
            help="Enable the feature",
        )

        self.assertEqual(argument.action, ArgumentAction.STORE_TRUE)

    def testCreateArgumentWithNargs(self) -> None:
        """
        Create argument with nargs specification.

        Create a Argument with the nargs parameter to accept multiple values.

        Parameters
        ----------
        self : TestCLIArgument
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. It asserts correctness of
            Argument initialization with nargs.
        """
        # Create a Argument with nargs to accept multiple values
        argument = Argument(
            flags=["--files"],
            type=str,
            nargs="+",
            help="List of files to process",
        )

        self.assertEqual(argument.nargs, "+")

    def testCreateArgumentWithMetavar(self) -> None:
        """
        Create argument with custom metavar.

        Set a custom metavar for display in help messages.

        Parameters
        ----------
        self : TestCLIArgument
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. It asserts correctness of
            Argument initialization with a custom metavar.
        """
        # Create a Argument with a custom metavar and verify its attribute
        argument = Argument(
            flags=["--input", "-i"],
            type=str,
            metavar="FILE",
            help="Input file",
        )

        self.assertEqual(argument.metavar, "FILE")

    def testCreateArgumentWithDest(self) -> None:
        """
        Create argument with custom destination.

        Create a Argument with a custom destination name for argument storage.

        Parameters
        ----------
        self : TestCLIArgument
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. It asserts correctness of
            Argument initialization with a custom destination.
        """
        # Create a Argument with a custom dest and verify its attribute
        argument = Argument(
            flags=["--output-file"],
            type=str,
            dest="output",
            help="Output file path",
        )

        self.assertEqual(argument.dest, "output")

    def testAddToParserSuccess(self) -> None:
        """
        Add argument to parser successfully.

        Add a valid Argument to an ArgumentParser instance and verify
        that it is present in the parser's actions.

        Parameters
        ----------
        self : TestCLIArgument
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. It asserts that the argument
            is successfully added to the parser.
        """
        parser = argparse.ArgumentParser()
        argument = Argument(
            flags=["--test"],
            type=str,
            help="Test argument",
        )

        # Should not raise any exception when adding argument to parser
        argument.addToParser(parser)

        # Verify that the argument was added to the parser's actions
        self.assertIn(
            "test",
            [action.dest for action in parser._actions if hasattr(action, "dest")],
        )

    def testAddToParserWithoutFlags(self) -> None:
        """
        Test raising ValueError when adding argument without flags.

        Attempts to add a Argument without properly defined flags and expects
        a ValueError to be raised.

        Returns
        -------
        None
            This method does not return a value. It asserts that a ValueError
            is raised.
        """
        # Attempt to create a Argument without flags and expect ValueError
        with self.assertRaises(ValueError):
            Argument(type=str)

    def testAddToParserTypeError(self) -> None:
        """
        Test error handling for type errors during argument addition.

        Patch the ArgumentParser's add_argument method to raise a TypeError,
        and verify that the Argument's addToParser method properly catches
        and re-raises the error with additional context.

        Returns
        -------
        None
            This method asserts that a TypeError is raised with the expected
            error message context.
        """
        parser: argparse.ArgumentParser = argparse.ArgumentParser()

        # Patch add_argument to simulate a TypeError during argument addition
        with patch.object(
            argparse.ArgumentParser,
            'add_argument',
            side_effect=TypeError("Invalid type")
        ):
            argument: Argument = Argument(flags=["--test"], type=str)

            with self.assertRaises(TypeError) as cm:
                argument.addToParser(parser)

            # Ensure the error message contains the expected context
            self.assertIn("Type error adding argument", str(cm.exception))
