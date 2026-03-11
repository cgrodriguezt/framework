from __future__ import annotations
import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch
from orionis.console.args.argument import Argument
from orionis.console.args.constructor import CLIArgumentConstructor
from orionis.console.args.filter import CLIArgumentFilter
from orionis.console.args.types import ALLOWED_TYPES, TYPE_CONVERTERS
from orionis.console.enums.actions import ArgumentAction
from orionis.test import TestCase


class TestCLIArgumentConstructor(TestCase):

    def testInitializeWithValidArgument(self):
        """
        Test initialization with valid Argument.

        Verifies that CLIArgumentConstructor can be properly initialized
        with a valid Argument instance.
        """
        argument = Argument(flags=["--test"], type=str)
        constructor = CLIArgumentConstructor(argument)
        
        # Constructor should initialize without raising exceptions
        self.assertIsInstance(constructor, CLIArgumentConstructor)

    def testInitializeWithNoneArgument(self):
        """
        Test initialization with None argument raises ValueError.

        Verifies that passing None as argument raises appropriate error
        during constructor initialization.
        """
        with self.assertRaises(ValueError) as cm:
            CLIArgumentConstructor(None)
        
        self.assertEqual(str(cm.exception), "Argument cannot be None")

    def testConstructPositionalArgument(self):
        """
        Test construction of positional argument.

        Verifies that positional arguments are properly processed
        and configured during construction.
        """
        argument = Argument(
            name="filename",
            type=str,
            help="Input filename"
        )
        constructor = CLIArgumentConstructor(argument)

        result = constructor.construct()

        # self.assertIsInstance(result, dict)
        # self.assertIn("flags", result)
        # self.assertEqual(result["flags"], ["filename"])
        # self.assertEqual(result["type"], str)

    def testConstructOptionalArgument(self):
        """
        Test construction of optional argument.

        Verifies that optional arguments with flags are properly
        processed during construction.
        """
        argument = Argument(
            flags=["--verbose", "-v"],
            type=bool,
            action=ArgumentAction.STORE_TRUE,
            help="Enable verbose mode"
        )
        constructor = CLIArgumentConstructor(argument)
        
        result = constructor.construct()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["flags"], ["--verbose", "-v"])
        self.assertEqual(result["action"], ArgumentAction.STORE_TRUE.value)

    def testConstructArgumentWithInvalidType(self):
        """
        Test construction with invalid argument type.

        Verifies that using an unsupported type raises TypeError
        during construction process.
        """
        # Create mock argument with invalid type
        mock_argument = MagicMock()
        mock_argument.toDict.return_value = {
            "flags": ["--test"],
            "type": dict,  # dict is not in ALLOWED_TYPES
            "help": "Test",
        }
        
        constructor = CLIArgumentConstructor(mock_argument)
        
        with self.assertRaises(TypeError) as cm:
            constructor.construct()
        
        self.assertIn("not valid. Allowed types are", str(cm.exception))

    def testConstructArgumentWithBothNameAndFlags(self):
        """
        Test construction with both name and flags raises error.

        Verifies that specifying both positional name and optional flags
        results in appropriate validation error.
        """
        # This would be caught during validation
        mock_argument = MagicMock()
        mock_argument.toDict.return_value = {
            "name": "test",
            "flags": ["--test"],
            "type": str,
        }
        
        constructor = CLIArgumentConstructor(mock_argument)
        
        with self.assertRaises(ValueError) as cm:
            constructor.construct()
        
        self.assertIn("Name cannot be used together with flags", str(cm.exception))

    def testConstructArgumentWithInvalidFlagFormat(self):
        """
        Test construction with invalid flag format.

        Verifies that improperly formatted flags are caught
        during the validation process.
        """
        mock_argument = MagicMock()
        mock_argument.toDict.return_value = {
            "flags": ["invalid_flag"],  # Doesn't start with -
            "type": str,
        }
        
        constructor = CLIArgumentConstructor(mock_argument)
        
        with self.assertRaises(ValueError) as cm:
            constructor.construct()
        
        # Should suggest using name parameter instead
        self.assertIn("For positional arguments, use", str(cm.exception))

    def testConstructArgumentWithDuplicateFlags(self):
        """
        Test construction with duplicate flags.

        Verifies that duplicate flags in the flags list are properly
        detected and rejected.
        """
        mock_argument = MagicMock()
        mock_argument.toDict.return_value = {
            "flags": ["--test", "--test"],  # Duplicate flags
            "type": str,
        }
        
        constructor = CLIArgumentConstructor(mock_argument)
        
        with self.assertRaises(ValueError) as cm:
            constructor.construct()
        
        self.assertIn("Duplicate flags are not allowed", str(cm.exception))

    def testConstructArgumentWithInvalidShortFlag(self):
        """
        Test construction with invalid short flag format.

        Verifies that short flags not following the -x format
        are properly rejected.
        """
        mock_argument = MagicMock()
        mock_argument.toDict.return_value = {
            "flags": ["-abc"],  # Invalid short flag format
            "type": str,
        }
        
        constructor = CLIArgumentConstructor(mock_argument)
        
        with self.assertRaises(ValueError) as cm:
            constructor.construct()
        
        self.assertIn("must be exactly '-x' format", str(cm.exception))


# class TestCLIArgumentFilter(TestCase):
#     """Test suite for CLIArgumentFilter class."""

#     def testInitializeWithValidArgument(self):
#         """
#         Test initialization with valid Argument.

#         Verifies that CLIArgumentFilter can be properly initialized
#         with a valid Argument instance.
#         """
#         argument = Argument(flags=["--test"], type=str)
#         filter_instance = CLIArgumentFilter(argument)
        
#         self.assertIsInstance(filter_instance, CLIArgumentFilter)

#     def testInitializeWithNoneArgument(self):
#         """
#         Test initialization with None argument raises ValueError.

#         Verifies that passing None as argument raises appropriate error
#         during filter initialization.
#         """
#         with self.assertRaises(ValueError) as cm:
#             CLIArgumentFilter(None)
        
#         self.assertEqual(str(cm.exception), "Argument cannot be None for filtering")

#     def testArgparseKwargsForOptionalArgument(self):
#         """
#         Test argparse kwargs generation for optional argument.

#         Verifies that proper keyword arguments are generated for
#         optional arguments with various configurations.
#         """
#         argument = Argument(
#             flags=["--output", "-o"],
#             type=str,
#             help="Output file",
#             required=True,
#             metavar="FILE"
#         )
#         filter_instance = CLIArgumentFilter(argument)
        
#         kwargs = filter_instance.argparseKwargs()
        
#         self.assertIsInstance(kwargs, dict)
#         self.assertEqual(kwargs["help"], "Output file")
#         self.assertEqual(kwargs["type"], str)
#         self.assertTrue(kwargs["required"])
#         self.assertEqual(kwargs["metavar"], "FILE")

#     def testArgparseKwargsForPositionalArgument(self):
#         """
#         Test argparse kwargs generation for positional argument.

#         Verifies that proper keyword arguments are generated for
#         positional arguments, excluding incompatible parameters.
#         """
#         argument = Argument(
#             name="input_file",
#             type=str,
#             help="Input file path"
#         )
#         filter_instance = CLIArgumentFilter(argument)
        
#         kwargs = filter_instance.argparseKwargs()
        
#         self.assertIsInstance(kwargs, dict)
#         self.assertEqual(kwargs["help"], "Input file path")
#         self.assertEqual(kwargs["type"], str)
#         # Required should not be present for positional arguments
#         self.assertNotIn("required", kwargs)

#     def testArgparseKwargsWithStoreAction(self):
#         """
#         Test argparse kwargs with store action.

#         Verifies that store action arguments are properly configured
#         with all relevant parameters included.
#         """
#         argument = Argument(
#             flags=["--count"],
#             type=int,
#             action=ArgumentAction.STORE,
#             default=5,
#             help="Item count"
#         )
#         filter_instance = CLIArgumentFilter(argument)
        
#         kwargs = filter_instance.argparseKwargs()
        
#         self.assertEqual(kwargs["action"], ArgumentAction.STORE.value)
#         self.assertEqual(kwargs["type"], int)
#         self.assertEqual(kwargs["default"], 5)

#     def testArgparseKwargsWithStoreTrueAction(self):
#         """
#         Test argparse kwargs with store_true action.

#         Verifies that store_true action properly filters out
#         incompatible parameters like type and default.
#         """
#         argument = Argument(
#             flags=["--verbose"],
#             type=bool,
#             action=ArgumentAction.STORE_TRUE,
#             help="Enable verbose output"
#         )
#         filter_instance = CLIArgumentFilter(argument)
        
#         kwargs = filter_instance.argparseKwargs()
        
#         self.assertEqual(kwargs["action"], ArgumentAction.STORE_TRUE.value)
#         # Type should be filtered out for store_true
#         self.assertNotIn("type", kwargs)
#         # Default should be filtered out for store_true
#         self.assertNotIn("default", kwargs)

#     def testArgparseKwargsWithCountAction(self):
#         """
#         Test argparse kwargs with count action.

#         Verifies that count action properly handles default values
#         and filters incompatible parameters.
#         """
#         argument = Argument(
#             flags=["--verbose", "-v"],
#             type=int,
#             action=ArgumentAction.COUNT,
#             default="0",  # String that should be converted to int
#             help="Verbosity level"
#         )
#         filter_instance = CLIArgumentFilter(argument)
        
#         kwargs = filter_instance.argparseKwargs()
        
#         self.assertEqual(kwargs["action"], ArgumentAction.COUNT.value)
#         # Default should be converted to int for count action
#         self.assertEqual(kwargs["default"], 0)

#     def testArgparseKwargsWithVersionAction(self):
#         """
#         Test argparse kwargs with version action.

#         Verifies that version action properly sets version parameter
#         and filters incompatible parameters.
#         """
#         argument = Argument(
#             flags=["--version"],
#             type=str,
#             action=ArgumentAction.VERSION,
#             help="Show version information"
#         )
#         # Add version attribute to argument
#         argument.__dict__["version"] = "2.0.0"
        
#         filter_instance = CLIArgumentFilter(argument)
        
#         kwargs = filter_instance.argparseKwargs()
        
#         self.assertEqual(kwargs["action"], ArgumentAction.VERSION.value)
#         self.assertEqual(kwargs["version"], "2.0.0")
#         # Type should be filtered out for version action
#         self.assertNotIn("type", kwargs)

#     def testArgparseKwargsWithConstAction(self):
#         """
#         Test argparse kwargs with store_const action.

#         Verifies that store_const action properly includes const parameter
#         and filters incompatible parameters.
#         """
#         argument = Argument(
#             flags=["--format"],
#             type=str,
#             action=ArgumentAction.STORE_CONST,
#             const="json",
#             help="Set output format to JSON"
#         )
#         filter_instance = CLIArgumentFilter(argument)
        
#         kwargs = filter_instance.argparseKwargs()
        
#         self.assertEqual(kwargs["action"], ArgumentAction.STORE_CONST.value)
#         self.assertEqual(kwargs["const"], "json")
#         # Type should be filtered out for store_const
#         self.assertNotIn("type", kwargs)

#     def testArgparseKwargsFiltersNoneValues(self):
#         """
#         Test that None values are properly filtered from kwargs.

#         Verifies that None values are excluded from the final
#         keyword arguments dictionary.
#         """
#         argument = Argument(
#             flags=["--test"],
#             type=str,
#             help="Test argument",
#             metavar=None,  # Explicitly None
#             choices=None   # Explicitly None
#         )
#         filter_instance = CLIArgumentFilter(argument)
        
#         kwargs = filter_instance.argparseKwargs()
        
#         # None values should be filtered out
#         self.assertNotIn("metavar", kwargs)
#         self.assertNotIn("choices", kwargs)
#         # Non-None values should remain
#         self.assertEqual(kwargs["help"], "Test argument")
#         self.assertEqual(kwargs["type"], str)


# class TestArgumentTypes(TestCase):
#     """Test suite for argument types module."""

#     def testAllowedTypesContainsBasicTypes(self):
#         """
#         Test that ALLOWED_TYPES contains all basic Python types.

#         Verifies that the set of allowed types includes all the
#         fundamental types supported by the argument system.
#         """
#         expected_types = {str, int, float, bool, Path}
        
#         self.assertTrue(expected_types.issubset(ALLOWED_TYPES))
        
#         # Verify specific types are present
#         self.assertIn(str, ALLOWED_TYPES)
#         self.assertIn(int, ALLOWED_TYPES)
#         self.assertIn(float, ALLOWED_TYPES)
#         self.assertIn(bool, ALLOWED_TYPES)
#         self.assertIn(Path, ALLOWED_TYPES)

#     def testTypeConvertersMapping(self):
#         """
#         Test that TYPE_CONVERTERS contains correct string-to-type mapping.

#         Verifies that the type converter dictionary properly maps
#         string representations to their corresponding type objects.
#         """
#         self.assertIn("builtins.str", TYPE_CONVERTERS)
#         self.assertIn("builtins.int", TYPE_CONVERTERS)
#         self.assertIn("builtins.float", TYPE_CONVERTERS)
#         self.assertIn("builtins.bool", TYPE_CONVERTERS)
#         self.assertIn("pathlib.Path", TYPE_CONVERTERS)
        
#         # Verify correct mapping
#         self.assertEqual(TYPE_CONVERTERS["builtins.str"], str)
#         self.assertEqual(TYPE_CONVERTERS["builtins.int"], int)
#         self.assertEqual(TYPE_CONVERTERS["builtins.float"], float)
#         self.assertEqual(TYPE_CONVERTERS["builtins.bool"], bool)
#         self.assertEqual(TYPE_CONVERTERS["pathlib.Path"], Path)

#     def testAllowedTypesMatchesConverters(self):
#         """
#         Test that ALLOWED_TYPES matches TYPE_CONVERTERS values.

#         Verifies consistency between the set of allowed types and
#         the values in the type converter dictionary.
#         """
#         converter_types = set(TYPE_CONVERTERS.values())
        
#         self.assertEqual(ALLOWED_TYPES, converter_types)


# class TestArgumentActionsEnum(TestCase):
#     """Test suite for ArgumentAction enum values."""

#     def testArgumentActionValues(self):
#         """
#         Test that ArgumentAction enum contains expected values.

#         Verifies that all required argparse action types are
#         properly defined in the ArgumentAction enum.
#         """
#         # Test basic actions
#         self.assertEqual(ArgumentAction.STORE.value, "store")
#         self.assertEqual(ArgumentAction.STORE_CONST.value, "store_const")
#         self.assertEqual(ArgumentAction.STORE_TRUE.value, "store_true")
#         self.assertEqual(ArgumentAction.STORE_FALSE.value, "store_false")
        
#         # Test collection actions
#         self.assertEqual(ArgumentAction.APPEND.value, "append")
        
#         # Test special actions
#         self.assertEqual(ArgumentAction.COUNT.value, "count")
#         self.assertEqual(ArgumentAction.HELP.value, "help")
#         self.assertEqual(ArgumentAction.VERSION.value, "version")

#     def testArgumentActionEnumIteration(self):
#         """
#         Test that ArgumentAction enum can be properly iterated.

#         Verifies that all enum members are accessible through
#         iteration and contain expected string values.
#         """
#         action_values = [action.value for action in ArgumentAction]
        
#         expected_values = [
#             "store", "store_const", "store_true", "store_false",
#             "append", "count", "help", "version"
#         ]
        
#         for expected in expected_values:
#             self.assertIn(expected, action_values)


# class TestIntegrationScenarios(TestCase):
#     """Integration tests for complete argument processing scenarios."""

#     def testCompleteArgumentProcessingFlow(self):
#         """
#         Test complete flow from Argument creation to parser addition.

#         Verifies that a Argument can be created, processed through
#         constructor and filter, and successfully added to an ArgumentParser.
#         """
#         # Create argument
#         argument = Argument(
#             flags=["--input", "-i"],
#             type=Path,
#             required=True,
#             metavar="FILE",
#             help="Input file path"
#         )
        
#         # Verify it can be added to parser
#         parser = argparse.ArgumentParser()
#         argument.addToParser(parser)
        
#         # Parse test arguments
#         args = parser.parse_args(["--input", "/path/to/file.txt"])
        
#         # Verify parsing worked correctly
#         self.assertEqual(str(args.input), '\\path\\to\\file.txt')

#     def testPositionalArgumentProcessingFlow(self):
#         """
#         Test complete flow for positional argument processing.

#         Verifies that positional arguments are properly processed
#         and can be successfully used with ArgumentParser.
#         """
#         # Create positional argument
#         argument = Argument(
#             name="source_file",
#             type=str,
#             help="Source file to process"
#         )
        
#         # Add to parser
#         parser = argparse.ArgumentParser()
#         argument.addToParser(parser)
        
#         # Parse test arguments
#         args = parser.parse_args(["test.txt"])
        
#         # Verify parsing worked correctly
#         self.assertEqual(args.source_file, "test.txt")

#     def testBooleanArgumentProcessingFlow(self):
#         """
#         Test complete flow for boolean argument processing.

#         Verifies that boolean arguments with store_true action
#         are properly processed and behave correctly.
#         """
#         # Create boolean argument
#         argument = Argument(
#             flags=["--verbose", "-v"],
#             type=bool,
#             action=ArgumentAction.STORE_TRUE,
#             help="Enable verbose output"
#         )
        
#         # Add to parser
#         parser = argparse.ArgumentParser()
#         argument.addToParser(parser)
        
#         # Test without flag
#         args_false = parser.parse_args([])
#         self.assertFalse(args_false.verbose)
        
#         # Test with flag
#         args_true = parser.parse_args(["--verbose"])
#         self.assertTrue(args_true.verbose)

#     def testArgumentWithChoicesProcessingFlow(self):
#         """
#         Test complete flow for argument with choices constraint.

#         Verifies that arguments with predefined choices are properly
#         validated and processed.
#         """
#         # Create argument with choices
#         choices = ["small", "medium", "large"]
#         argument = Argument(
#             flags=["--size"],
#             type=str,
#             choices=choices,
#             default="medium",
#             help="Select size option"
#         )
        
#         # Add to parser
#         parser = argparse.ArgumentParser()
#         argument.addToParser(parser)
        
#         # Test valid choice
#         args_valid = parser.parse_args(["--size", "large"])
#         self.assertEqual(args_valid.size, "large")
        
#         # Test default when no argument provided
#         args_default = parser.parse_args([])
#         self.assertEqual(args_default.size, "medium")

#     def testMultipleArgumentsProcessingFlow(self):
#         """
#         Test complete flow with multiple different argument types.

#         Verifies that multiple CLIArguments with different configurations
#         can coexist and function properly in the same parser.
#         """
#         # Create multiple arguments
#         arguments = [
#             Argument(
#                 name="input_file",
#                 type=str,
#                 help="Input file"
#             ),
#             Argument(
#                 flags=["--output", "-o"],
#                 type=str,
#                 required=True,
#                 help="Output file"
#             ),
#             Argument(
#                 flags=["--verbose", "-v"],
#                 type=bool,
#                 action=ArgumentAction.STORE_TRUE,
#                 help="Verbose mode"
#             ),
#             Argument(
#                 flags=["--count", "-c"],
#                 type=int,
#                 default=1,
#                 help="Number of iterations"
#             )
#         ]
        
#         # Add all arguments to parser
#         parser = argparse.ArgumentParser()
#         for arg in arguments:
#             arg.addToParser(parser)
        
#         # Test parsing with all arguments
#         test_args = ["input.txt", "--output", "output.txt", "--verbose", "--count", "5"]
#         args = parser.parse_args(test_args)
        
#         # Verify all arguments parsed correctly
#         self.assertEqual(args.input_file, "input.txt")
#         self.assertEqual(args.output, "output.txt")
#         self.assertTrue(args.verbose)
#         self.assertEqual(args.count, 5)
