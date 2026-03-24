from __future__ import annotations
from orionis.console.request.contracts.cli_request import ICLIRequest
from orionis.console.request.cli_request import CLIRequest
from orionis.test import TestCase

class TestCLIRequest(TestCase):

    # ------------------------------------------------------------------ #
    #  Instantiation & interface                                         #
    # ------------------------------------------------------------------ #

    def testInstantiationWithNoArguments(self) -> None:
        """
        Verify that CLIRequest can be instantiated without any arguments.

        Ensures the default constructor creates a valid instance without
        raising any exception when neither command nor args are provided.
        """
        req = CLIRequest()
        self.assertIsInstance(req, CLIRequest)

    def testInstantiationWithCommand(self) -> None:
        """
        Verify that CLIRequest can be instantiated with a command string.

        Ensures the constructor stores the provided command name without
        raising any exception.
        """
        req = CLIRequest(command="make:model")
        self.assertIsInstance(req, CLIRequest)

    def testInstantiationWithArgs(self) -> None:
        """
        Verify that CLIRequest can be instantiated with an args dictionary.

        Ensures the constructor accepts a dictionary of arguments and stores
        it internally without raising any exception.
        """
        req = CLIRequest(args={"name": "User"})
        self.assertIsInstance(req, CLIRequest)

    def testInstantiationWithBothCommandAndArgs(self) -> None:
        """
        Verify that CLIRequest can be instantiated with command and args together.

        Ensures both parameters are accepted simultaneously and the instance
        is valid for subsequent operations.
        """
        req = CLIRequest(command="make:model", args={"name": "User", "force": True})
        self.assertIsInstance(req, CLIRequest)

    def testIsSubclassOfICLIRequest(self) -> None:
        """
        Verify that CLIRequest is a subclass of ICLIRequest.

        Ensures the concrete implementation satisfies the abstract interface
        so it can be used polymorphically wherever ICLIRequest is expected.
        """
        self.assertTrue(issubclass(CLIRequest, ICLIRequest))

    def testInstanceIsICLIRequest(self) -> None:
        """
        Verify that a CLIRequest instance satisfies isinstance(obj, ICLIRequest).

        Ensures polymorphic usage is valid and the object passes type checks
        against the abstract interface.
        """
        req = CLIRequest()
        self.assertIsInstance(req, ICLIRequest)

    # ------------------------------------------------------------------ #
    #  Constructor — error cases                                         #
    # ------------------------------------------------------------------ #

    def testConstructorRaisesTypeErrorForNonDictArgs(self) -> None:
        """
        Verify that the constructor raises TypeError when args is not a dict.

        Ensures invalid argument types are rejected at construction time
        rather than silently producing unexpected behaviour later.
        """
        with self.assertRaises(TypeError):
            CLIRequest(args=["--force"])  # type: ignore[arg-type]

    def testConstructorRaisesTypeErrorForNonStringCommand(self) -> None:
        """
        Verify that the constructor raises TypeError when command is not a string.

        Ensures only string values are accepted as command names so the
        property always returns a homogeneous type.
        """
        with self.assertRaises(TypeError):
            CLIRequest(command=123)  # type: ignore[arg-type]

    def testConstructorAcceptsNoneCommand(self) -> None:
        """
        Verify that the constructor accepts None as the command argument.

        Ensures None is treated as an absent command without raising any
        exception, leaving the command property returning None.
        """
        req = CLIRequest(command=None)
        self.assertIsNone(req.command)

    def testConstructorAcceptsNoneArgs(self) -> None:
        """
        Verify that the constructor treats None args as an empty dictionary.

        Ensures callers can omit args and still receive an empty dict from
        getArguments rather than a None reference.
        """
        req = CLIRequest(args=None)
        self.assertEqual(req.getArguments(), {})

    def testConstructorAcceptsEmptyDict(self) -> None:
        """
        Verify that the constructor accepts an empty dictionary for args.

        Ensures the edge case of an explicitly empty argument map is handled
        without raising any exception.
        """
        req = CLIRequest(args={})
        self.assertEqual(req.getArguments(), {})

    def testConstructorAcceptsEmptyStringCommand(self) -> None:
        """
        Verify that an empty string command is stored without raising TypeError.

        Ensures empty string is treated as a falsy but valid value since the
        guard condition only validates truthy command values.
        """
        req = CLIRequest(command="")
        self.assertEqual(req.command, "")

    # ------------------------------------------------------------------ #
    #  signature property                                                #
    # ------------------------------------------------------------------ #

    def testSignatureReturnsCommandValue(self) -> None:
        """
        Verify that the signature property returns the command string.

        Ensures the signature attribute exposes the same value that was
        passed as the command argument to the constructor.
        """
        req = CLIRequest(command="migrate:fresh")
        self.assertEqual(req.signature, "migrate:fresh")

    def testSignatureReturnsNoneWhenNoCommand(self) -> None:
        """
        Verify that the signature property returns None when no command was set.

        Ensures the property is consistent with the command property when the
        instance was created without a command argument.
        """
        req = CLIRequest()
        self.assertIsNone(req.signature)

    # ------------------------------------------------------------------ #
    #  command property                                                  #
    # ------------------------------------------------------------------ #

    def testCommandReturnsStoredCommand(self) -> None:
        """
        Verify that the command property returns the command name verbatim.

        Ensures the value passed to the constructor is retrievable exactly
        without modification or truncation.
        """
        req = CLIRequest(command="db:seed")
        self.assertEqual(req.command, "db:seed")

    def testCommandReturnsNoneWhenNoCommand(self) -> None:
        """
        Verify that the command property returns None when no command was given.

        Ensures the default state of the command property is None when the
        constructor is invoked without the command parameter.
        """
        req = CLIRequest()
        self.assertIsNone(req.command)

    def testCommandAndSignatureMatchAlways(self) -> None:
        """
        Verify that command and signature always return the same value.

        Ensures both properties are backed by the same internal storage so
        callers can rely on their equivalence at any point in time.
        """
        req = CLIRequest(command="route:list")
        self.assertEqual(req.command, req.signature)

    # ------------------------------------------------------------------ #
    #  getArguments                                                      #
    # ------------------------------------------------------------------ #

    def testGetArgumentsReturnsEmptyDictByDefault(self) -> None:
        """
        Verify that getArguments returns an empty dict when no args were provided.

        Ensures the absent-args default does not expose None or raise any
        exception but yields an empty dictionary instead.
        """
        req = CLIRequest()
        self.assertEqual(req.getArguments(), {})

    def testGetArgumentsReturnsAllStoredArgs(self) -> None:
        """
        Verify that getArguments returns every key-value pair provided at construction.

        Ensures all arguments passed to the constructor are retrievable through
        the public getArguments interface.
        """
        data = {"name": "Post", "force": True, "count": 5}
        req = CLIRequest(args=data)
        self.assertEqual(req.getArguments(), data)

    def testGetArgumentsReturnsCopy(self) -> None:
        """
        Verify that getArguments returns a copy of the internal dictionary.

        Ensures mutating the returned dict does not alter the internal state
        so subsequent calls always reflect the true stored arguments.
        """
        req = CLIRequest(args={"key": "value"})
        result = req.getArguments()
        result["extra"] = "injected"
        self.assertNotIn("extra", req.getArguments())

    def testGetArgumentsAfterInjectReturnsNewArgs(self) -> None:
        """
        Verify that getArguments reflects arguments injected via _injectArguments.

        Ensures the method returns the most recently injected argument set
        rather than the original constructor arguments.
        """
        req = CLIRequest(args={"old": 1})
        req._injectArguments({"new": 2})
        self.assertEqual(req.getArguments(), {"new": 2})

    # ------------------------------------------------------------------ #
    #  getArgument                                                       #
    # ------------------------------------------------------------------ #

    def testGetArgumentReturnsExistingValue(self) -> None:
        """
        Verify that getArgument returns the correct value for an existing key.

        Ensures the method looks up keys correctly against the stored
        argument dictionary without any transformation.
        """
        req = CLIRequest(args={"model": "Article"})
        self.assertEqual(req.getArgument("model"), "Article")

    def testGetArgumentReturnNoneForMissingKeyByDefault(self) -> None:
        """
        Verify that getArgument returns None when the key is absent and no default given.

        Ensures the method does not raise an exception for missing keys
        but quietly returns the documented default of None.
        """
        req = CLIRequest()
        self.assertIsNone(req.getArgument("missing"))

    def testGetArgumentReturnsProvidedDefault(self) -> None:
        """
        Verify that getArgument returns the caller's default for a missing key.

        Ensures the default parameter is honoured and its value is returned
        unchanged when the requested key does not exist.
        """
        req = CLIRequest()
        self.assertEqual(req.getArgument("missing", "fallback"), "fallback")

    def testGetArgumentRaisesTypeErrorForNonStringKey(self) -> None:
        """
        Verify that getArgument raises TypeError when key is not a string.

        Ensures only string keys are accepted so accidental integer or None
        lookups fail fast with a descriptive error.
        """
        req = CLIRequest(args={"key": "value"})
        with self.assertRaises(TypeError):
            req.getArgument(123)  # type: ignore[arg-type]

    def testGetArgumentRaisesTypeErrorForNoneKey(self) -> None:
        """
        Verify that getArgument raises TypeError when key is None.

        Ensures None is treated as an invalid key type rather than silently
        performing a dictionary lookup with None.
        """
        req = CLIRequest()
        with self.assertRaises(TypeError):
            req.getArgument(None)  # type: ignore[arg-type]

    def testGetArgumentWithBooleanValue(self) -> None:
        """
        Verify that getArgument correctly returns a boolean argument value.

        Ensures that boolean values stored in the argument map are returned
        without type coercion or conversion.
        """
        req = CLIRequest(args={"verbose": False})
        self.assertFalse(req.getArgument("verbose"))

    def testGetArgumentWithZeroValue(self) -> None:
        """
        Verify that getArgument returns 0 rather than the default for a zero-value key.

        Ensures falsy stored values are distinguished from a missing key so
        the correct value is returned even when it evaluates to False.
        """
        req = CLIRequest(args={"count": 0})
        self.assertEqual(req.getArgument("count", 99), 0)

    def testGetArgumentWithNoneStoredValue(self) -> None:
        """
        Verify that getArgument returns None when None is explicitly stored.

        Ensures that an explicitly stored None value is distinguishable in
        principle — both the stored value and the default are None, but the
        key is present and the method returns without error.
        """
        req = CLIRequest(args={"opt": None})
        self.assertIsNone(req.getArgument("opt", "default"))

    # ------------------------------------------------------------------ #
    #  _injectArguments                                                  #
    # ------------------------------------------------------------------ #

    def testInjectArgumentsReplacesInternalArgs(self) -> None:
        """
        Verify that _injectArguments replaces the existing arguments dictionary.

        Ensures the injection mechanism fully replaces prior arguments so the
        new dictionary is the sole source of truth for subsequent lookups.
        """
        req = CLIRequest(args={"old": "data"})
        req._injectArguments({"new": "data"})
        self.assertNotIn("old", req.getArguments())
        self.assertIn("new", req.getArguments())

    def testInjectArgumentsWithEmptyDict(self) -> None:
        """
        Verify that _injectArguments accepts an empty dictionary.

        Ensures that clearing all arguments via injection is supported and
        results in getArguments returning an empty dict.
        """
        req = CLIRequest(args={"key": "value"})
        req._injectArguments({})
        self.assertEqual(req.getArguments(), {})

    def testInjectArgumentsWithMultipleTypes(self) -> None:
        """
        Verify that _injectArguments accepts values of different Python types.

        Ensures the method stores heterogeneous argument maps without any
        type coercion or validation on the values.
        """
        payload = {"str_arg": "hello", "int_arg": 42, "bool_arg": True, "none_arg": None}
        req = CLIRequest()
        req._injectArguments(payload)
        self.assertEqual(req.getArguments(), payload)

    def testInjectArgumentsCanBeCalledMultipleTimes(self) -> None:
        """
        Verify that _injectArguments can be invoked more than once sequentially.

        Ensures each injection fully replaces the previous state so the final
        call determines what getArguments returns.
        """
        req = CLIRequest()
        req._injectArguments({"first": 1})
        req._injectArguments({"second": 2})
        self.assertEqual(req.getArguments(), {"second": 2})

    # ------------------------------------------------------------------ #
    #  Edge cases                                                        #
    # ------------------------------------------------------------------ #

    def testGetArgumentsWithNestedStructures(self) -> None:
        """
        Verify that getArguments handles nested lists and dicts as values.

        Ensures complex argument structures are stored and returned intact
        without flattening or serialisation.
        """
        data = {"items": [1, 2, 3], "meta": {"page": 1}}
        req = CLIRequest(args=data)
        self.assertEqual(req.getArguments(), data)

    def testCommandWithSpecialCharacters(self) -> None:
        """
        Verify that command strings containing colons and hyphens are stored correctly.

        Ensures common CLI command naming conventions such as 'make:model'
        or 'db-seed' are accepted and returned verbatim.
        """
        req = CLIRequest(command="make:controller --resource")
        self.assertEqual(req.command, "make:controller --resource")

    def testGetArgumentKeyWithSpaces(self) -> None:
        """
        Verify that getArgument works with keys that contain spaces.

        Ensures the method performs a plain dictionary lookup regardless of
        the key's content, returning the stored value without modification.
        """
        req = CLIRequest(args={"key with spaces": "value"})
        self.assertEqual(req.getArgument("key with spaces"), "value")
