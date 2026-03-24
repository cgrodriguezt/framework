from __future__ import annotations
from unittest.mock import AsyncMock, MagicMock
from orionis.console.kernel import KernelCLI
from orionis.console.contracts.kernel import IKernelCLI
from orionis.test import TestCase

class TestKernelCLI(TestCase):

    # ------------------------------------------------------------------ #
    #  Helpers                                                           #
    # ------------------------------------------------------------------ #

    def _make(self) -> KernelCLI:
        """
        Create a KernelCLI instance and inject a mock reactor.

        Returns
        -------
        KernelCLI
            A KernelCLI with a mocked IReactor so no real subprocess
            or I/O calls are made during tests.
        """
        kernel = KernelCLI()
        reactor = MagicMock()
        reactor.call = AsyncMock(return_value=0)
        kernel._KernelCLI__reactor = reactor
        return kernel

    # ------------------------------------------------------------------ #
    #  Instantiation / interface                                         #
    # ------------------------------------------------------------------ #

    def testInstantiation(self) -> None:
        """
        Test that KernelCLI can be instantiated without arguments.

        Ensures that the constructor completes successfully and returns
        a KernelCLI object.
        """
        kernel = KernelCLI()
        self.assertIsInstance(kernel, KernelCLI)

    def testInstanceIsIKernelCLI(self) -> None:
        """
        Test that KernelCLI is an instance of IKernelCLI.

        Ensures that KernelCLI satisfies the abstract interface contract.
        """
        kernel = KernelCLI()
        self.assertIsInstance(kernel, IKernelCLI)

    def testIsSubclassOfIKernelCLI(self) -> None:
        """
        Test that KernelCLI is a subclass of IKernelCLI.

        Ensures the class hierarchy is correct at the type level.
        """
        self.assertTrue(issubclass(KernelCLI, IKernelCLI))

    # ------------------------------------------------------------------ #
    #  IGNORE_FLAGS class variable                                       #
    # ------------------------------------------------------------------ #

    def testIgnoreFlagsIsClassVariable(self) -> None:
        """
        Test that IGNORE_FLAGS is defined as a class-level attribute.

        Ensures that the flags list is available without instantiation.
        """
        self.assertTrue(hasattr(KernelCLI, "IGNORE_FLAGS"))

    def testIgnoreFlagsIsList(self) -> None:
        """
        Test that IGNORE_FLAGS is a list.

        Ensures the type constraint required by processing logic is met.
        """
        self.assertIsInstance(KernelCLI.IGNORE_FLAGS, list)

    def testIgnoreFlagsContainsReactor(self) -> None:
        """
        Test that IGNORE_FLAGS contains the 'reactor' entry.

        Ensures the default script-name token is always filtered out.
        """
        self.assertIn("reactor", KernelCLI.IGNORE_FLAGS)

    def testIgnoreFlagsContainsCommonInterpreterFlags(self) -> None:
        """
        Test that IGNORE_FLAGS includes common Python interpreter flags.

        Ensures that flags like -B, -c, -m, and -v are filtered out when
        present at the beginning of the argument list.
        """
        for flag in ["-c", "-m", "-B", "-v", "-i"]:
            self.assertIn(flag, KernelCLI.IGNORE_FLAGS)

    # ------------------------------------------------------------------ #
    #  boot()                                                            #
    # ------------------------------------------------------------------ #

    async def testBootStoresReactor(self) -> None:
        """
        Test that boot() stores the reactor returned by the application.

        Ensures that after calling boot, the internal reactor attribute is
        the one produced by application.make().
        """
        kernel = KernelCLI()
        mock_reactor = MagicMock()
        mock_reactor.call = AsyncMock(return_value=0)
        app = MagicMock()
        app.make = AsyncMock(return_value=mock_reactor)

        await kernel.boot(app)

        self.assertIs(kernel._KernelCLI__reactor, mock_reactor)

    async def testBootCallsApplicationMake(self) -> None:
        """
        Test that boot() calls application.make() exactly once.

        Ensures the reactor is obtained via the application factory and
        not constructed directly inside the kernel.
        """
        kernel = KernelCLI()
        mock_reactor = MagicMock()
        app = MagicMock()
        app.make = AsyncMock(return_value=mock_reactor)

        await kernel.boot(app)

        app.make.assert_called_once()

    # ------------------------------------------------------------------ #
    #  handle() — TypeError guard                                        #
    # ------------------------------------------------------------------ #

    async def testHandleRaisesTypeErrorForNonListArgs(self) -> None:
        """
        Test that handle() raises TypeError when args is not a list.

        Ensures that passing a non-list type (e.g., a string) raises a
        descriptive TypeError instead of causing unexpected behaviour.
        """
        kernel = self._make()
        with self.assertRaises(TypeError):
            await kernel.handle("not-a-list")

    async def testHandleRaisesTypeErrorForDictArgs(self) -> None:
        """
        Test that handle() raises TypeError when args is a dict.

        Ensures non-list iterables are rejected with an appropriate error.
        """
        kernel = self._make()
        with self.assertRaises(TypeError):
            await kernel.handle({"cmd": "test"})

    async def testHandleRaisesTypeErrorForIntArgs(self) -> None:
        """
        Test that handle() raises TypeError when args is an integer.

        Verifies that scalar types are rejected as invalid argument inputs.
        """
        kernel = self._make()
        with self.assertRaises(TypeError):
            await kernel.handle(42)

    # ------------------------------------------------------------------ #
    #  handle() — fallback to list command                               #
    # ------------------------------------------------------------------ #

    async def testHandleWithNoneArgsCallsList(self) -> None:
        """
        Test that handle(None) delegates to the 'list' command.

        Ensures that when no arguments are provided the kernel shows the
        default help listing.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        result = await kernel.handle(None)
        kernel._KernelCLI__reactor.call.assert_called_once_with("list")
        self.assertEqual(result, 0)

    async def testHandleWithEmptyListCallsList(self) -> None:
        """
        Test that handle([]) delegates to the 'list' command.

        Ensures that an empty argument list triggers the default help.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        result = await kernel.handle([])
        kernel._KernelCLI__reactor.call.assert_called_once_with("list")
        self.assertEqual(result, 0)

    async def testHandleWithHelpFlagCallsList(self) -> None:
        """
        Test that handle(['--help']) delegates to the 'list' command.

        Ensures the --help flag is treated as a request for the listing.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        result = await kernel.handle(["--help"])
        kernel._KernelCLI__reactor.call.assert_called_once_with("list")
        self.assertEqual(result, 0)

    async def testHandleWithShortHelpFlagCallsList(self) -> None:
        """
        Test that handle(['-h']) delegates to the 'list' command.

        Ensures the short -h flag is treated the same as --help.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        result = await kernel.handle(["-h"])
        kernel._KernelCLI__reactor.call.assert_called_once_with("list")
        self.assertEqual(result, 0)

    async def testHandleWithHelpWordCallsList(self) -> None:
        """
        Test that handle(['help']) delegates to the 'list' command.

        Ensures the bare 'help' keyword triggers the listing as well.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        result = await kernel.handle(["help"])
        kernel._KernelCLI__reactor.call.assert_called_once_with("list")
        self.assertEqual(result, 0)

    # ------------------------------------------------------------------ #
    #  handle() — ignore flags stripping                                 #
    # ------------------------------------------------------------------ #

    async def testHandleStripsIgnoreFlagBeforeCommand(self) -> None:
        """
        Test that handle() removes IGNORE_FLAGS tokens before routing.

        Ensures that interpreter flags at the start of the list do not
        prevent the real command from being dispatched.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        # '-B' is an IGNORE_FLAG; 'serve' is the real command
        result = await kernel.handle(["-B", "serve"])
        kernel._KernelCLI__reactor.call.assert_called_once_with("serve", [])
        self.assertEqual(result, 0)

    async def testHandleStripsReactorTokenBeforeCommand(self) -> None:
        """
        Test that handle() removes the 'reactor' token at the start.

        Ensures the default script-name filter works as expected.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        result = await kernel.handle(["reactor", "migrate"])
        kernel._KernelCLI__reactor.call.assert_called_once_with("migrate", [])
        self.assertEqual(result, 0)

    async def testHandleOnlyIgnoreFlagsCallsList(self) -> None:
        """
        Test that handle() calls 'list' when only IGNORE_FLAGS remain.

        Ensures that after stripping all flags, an empty command falls
        back to the default help listing.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        result = await kernel.handle(["-B"])
        kernel._KernelCLI__reactor.call.assert_called_once_with("list")
        self.assertEqual(result, 0)

    # ------------------------------------------------------------------ #
    #  handle() — normal command dispatch                                #
    # ------------------------------------------------------------------ #

    async def testHandleDispatchesCommandWithNoExtraArgs(self) -> None:
        """
        Test that handle() routes a lone command with an empty args list.

        Ensures that when a command token has no trailing arguments the
        reactor receives an empty list.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        await kernel.handle(["migrate"])
        kernel._KernelCLI__reactor.call.assert_called_once_with("migrate", [])

    async def testHandleDispatchesCommandWithArgs(self) -> None:
        """
        Test that handle() routes a command together with its arguments.

        Ensures that remaining tokens after the command name are forwarded
        to the reactor as the args list.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        await kernel.handle(["make:model", "User", "--force"])
        kernel._KernelCLI__reactor.call.assert_called_once_with(
            "make:model", ["User", "--force"]
        )

    async def testHandleReturnsReactorExitCode(self) -> None:
        """
        Test that handle() propagates the exit code returned by the reactor.

        Ensures the integer result from reactor.call() is transparently
        returned to the caller.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=42)
        result = await kernel.handle(["some:command"])
        self.assertEqual(result, 42)

    async def testHandleReturnsNonZeroExitCode(self) -> None:
        """
        Test that handle() returns a non-zero exit code on failure.

        Ensures error codes from the reactor are propagated unchanged.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=1)
        result = await kernel.handle(["failing:command"])
        self.assertEqual(result, 1)

    # ------------------------------------------------------------------ #
    #  handle() — stop-stripping heuristic                               #
    # ------------------------------------------------------------------ #

    async def testHandleStopsStrippingAtFirstNonFlag(self) -> None:
        """
        Test that flag stripping stops at the first non-IGNORE_FLAGS token.

        Ensures that a non-flag token is treated as the command and is
        not removed, even when followed by more non-flag tokens.
        """
        kernel = self._make()
        kernel._KernelCLI__reactor.call = AsyncMock(return_value=0)
        # First token is the command; '-B' that follows is an argument, not stripped
        await kernel.handle(["db:seed", "-B"])
        kernel._KernelCLI__reactor.call.assert_called_once_with("db:seed", ["-B"])
