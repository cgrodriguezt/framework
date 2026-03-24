from __future__ import annotations
import inspect
from orionis.console.request.contracts.cli_request import ICLIRequest
from orionis.console.request.cli_request import CLIRequest
from orionis.test import TestCase

class TestICLIRequestContract(TestCase):

    # ------------------------------------------------------------------ #
    #  Abstract class characteristics                                    #
    # ------------------------------------------------------------------ #

    def testIsAbstractClass(self) -> None:
        """
        Verify that ICLIRequest is recognised as an abstract class.

        Ensures the interface declares at least one abstract method so
        Python prevents direct instantiation.
        """
        self.assertTrue(inspect.isabstract(ICLIRequest))

    def testCannotBeInstantiatedDirectly(self) -> None:
        """
        Verify that ICLIRequest cannot be instantiated directly.

        Ensures attempting to create an instance raises TypeError due to
        unimplemented abstract methods.
        """
        with self.assertRaises(TypeError):
            ICLIRequest()  # type: ignore[abstract]

    def testHasExactlyFiveAbstractMembers(self) -> None:
        """
        Verify that ICLIRequest declares exactly five abstract members.

        Ensures the interface surface area is stable and that no methods or
        properties have been silently added or removed.
        """
        self.assertEqual(len(ICLIRequest.__abstractmethods__), 5)

    # ------------------------------------------------------------------ #
    #  Abstract property presence                                        #
    # ------------------------------------------------------------------ #

    def testSignaturePropertyIsAbstract(self) -> None:
        """
        Verify that 'signature' is listed in ICLIRequest.__abstractmethods__.

        Ensures every concrete subclass is forced to provide a concrete
        implementation of the signature read-only property.
        """
        self.assertIn("signature", ICLIRequest.__abstractmethods__)

    def testCommandPropertyIsAbstract(self) -> None:
        """
        Verify that 'command' is listed in ICLIRequest.__abstractmethods__.

        Ensures every concrete subclass is forced to provide a concrete
        implementation of the command read-only property.
        """
        self.assertIn("command", ICLIRequest.__abstractmethods__)

    # ------------------------------------------------------------------ #
    #  Abstract method presence                                         #
    # ------------------------------------------------------------------ #

    def testGetArgumentsIsAbstract(self) -> None:
        """
        Verify that 'getArguments' is listed in ICLIRequest.__abstractmethods__.

        Ensures every concrete subclass must implement the bulk-arguments
        accessor to satisfy the interface contract.
        """
        self.assertIn("getArguments", ICLIRequest.__abstractmethods__)

    def testGetArgumentIsAbstract(self) -> None:
        """
        Verify that 'getArgument' is listed in ICLIRequest.__abstractmethods__.

        Ensures every concrete subclass must implement the single-argument
        accessor to satisfy the interface contract.
        """
        self.assertIn("getArgument", ICLIRequest.__abstractmethods__)

    def testInjectArgumentsIsAbstract(self) -> None:
        """
        Verify that '_injectArguments' is listed in ICLIRequest.__abstractmethods__.

        Ensures every concrete subclass must implement the injection method
        to satisfy the internal contract used by the framework.
        """
        self.assertIn("_injectArguments", ICLIRequest.__abstractmethods__)

    # ------------------------------------------------------------------ #
    #  Abstract property types                                          #
    # ------------------------------------------------------------------ #

    def testSignatureIsProperty(self) -> None:
        """
        Verify that 'signature' is defined as a property on ICLIRequest.

        Ensures the abstract declaration uses the @property decorator so
        concrete classes must implement it as a property rather than a method.
        """
        self.assertIsInstance(inspect.getattr_static(ICLIRequest, "signature"), property)

    def testCommandIsProperty(self) -> None:
        """
        Verify that 'command' is defined as a property on ICLIRequest.

        Ensures the abstract declaration uses the @property decorator so
        concrete classes must implement it as a property rather than a method.
        """
        self.assertIsInstance(inspect.getattr_static(ICLIRequest, "command"), property)

    # ------------------------------------------------------------------ #
    #  Signature verification                                            #
    # ------------------------------------------------------------------ #

    def testGetArgumentSignatureHasKeyParam(self) -> None:
        """
        Verify that getArgument declares a positional 'key' parameter.

        Ensures the interface method signature aligns with the documented
        contract so callers know exactly what argument name to use.
        """
        sig = inspect.signature(ICLIRequest.getArgument)
        self.assertIn("key", sig.parameters)

    def testGetArgumentSignatureHasDefaultParam(self) -> None:
        """
        Verify that getArgument declares a 'default' parameter with a default of None.

        Ensures callers can omit the default argument and receive None when
        the requested key is absent, as documented.
        """
        sig = inspect.signature(ICLIRequest.getArgument)
        params = sig.parameters
        self.assertIn("default", params)
        self.assertIsNone(params["default"].default)

    def testInjectArgumentsSignatureHasArgsParam(self) -> None:
        """
        Verify that _injectArguments declares an 'args' parameter.

        Ensures the parameter name matches the documented interface so
        callers are not surprised by unexpected keyword names.
        """
        sig = inspect.signature(ICLIRequest._injectArguments)
        self.assertIn("args", sig.parameters)

    # ------------------------------------------------------------------ #
    #  CLIRequest conformance                                            #
    # ------------------------------------------------------------------ #

    def testCLIRequestIsSubclassOfICLIRequest(self) -> None:
        """
        Verify that CLIRequest is a subclass of ICLIRequest.

        Ensures the concrete class satisfies the abstract interface so it
        can be used anywhere ICLIRequest is expected.
        """
        self.assertTrue(issubclass(CLIRequest, ICLIRequest))

    def testCLIRequestCanBeInstantiated(self) -> None:
        """
        Verify that CLIRequest can be instantiated without raising errors.

        Ensures the concrete class provides implementations for all abstract
        members declared by ICLIRequest.
        """
        req = CLIRequest()
        self.assertIsInstance(req, CLIRequest)

    def testCLIRequestIsInstanceOfICLIRequest(self) -> None:
        """
        Verify that a CLIRequest instance passes isinstance(obj, ICLIRequest).

        Ensures polymorphic usage is valid so any code accepting an
        ICLIRequest can transparently receive a CLIRequest.
        """
        req = CLIRequest()
        self.assertIsInstance(req, ICLIRequest)

    def testCLIRequestImplementsAllAbstractMethods(self) -> None:
        """
        Verify that CLIRequest provides a concrete implementation for every
        abstract member declared in ICLIRequest.

        Ensures no abstract method or property was accidentally left
        unimplemented in the concrete class.
        """
        for name in ICLIRequest.__abstractmethods__:
            member = inspect.getattr_static(CLIRequest, name, None)
            self.assertIsNotNone(
                member,
                msg=f"CLIRequest is missing implementation for '{name}'",
            )
            is_concrete = (
                inspect.isfunction(member)
                or isinstance(member, property)
            )
            self.assertTrue(
                is_concrete,
                msg=f"CLIRequest.{name} is not a concrete implementation",
            )
