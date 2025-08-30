from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.core.reactor import Reactor
from unittest.mock import MagicMock, patch
import asyncio

class TestReactor(AsyncTestCase):
    """
    Unit tests for the Reactor class.
    """

    async def testLoadCommandsLoadsOnce(self):
        """
        Tests that __loadCommands loads commands only once per instance.

        Notes
        -----
        Ensures that repeated calls to __loadCommands do not reload commands.
        """
        app = MagicMock()
        reactor = Reactor(app)
        # Patch internal methods to track calls
        with patch.object(reactor, '_Reactor__loadCustomCommands') as custom, \
             patch.object(reactor, '_Reactor__loadCoreCommands') as core, \
             patch.object(reactor, '_Reactor__loadFluentCommands') as fluent:
            reactor._Reactor__loadCommands()
            reactor._Reactor__loadCommands()
            self.assertEqual(custom.call_count, 1)
            self.assertEqual(core.call_count, 1)
            self.assertEqual(fluent.call_count, 1)

    async def testCommandFluentRegistration(self):
        """
        Tests that the command() method registers a fluent command correctly.

        Notes
        -----
        Ensures that a command defined via the fluent interface is added to the internal list.
        """
        app = MagicMock()
        reactor = Reactor(app)
        class DummyHandler:
            def handle(self):
                pass
        handler = [DummyHandler, 'handle']
        result = reactor.command('demo:fluent', handler)
        # Robust check: attribute or get() method
        if hasattr(result, 'signature'):
            self.assertEqual(result.signature, 'demo:fluent')
        elif hasattr(result, 'get'):
            sig, _ = result.get()
            self.assertEqual(sig, 'demo:fluent')
        else:
            self.fail('Fluent command does not expose signature as attribute or get()')
        self.assertEqual(len(reactor._Reactor__fluent_commands), 1)

    async def testInfoReturnsSortedCommands(self):
        """
        Tests that info() returns a sorted list of command metadata.

        Notes
        -----
        Ensures that the info method returns a list sorted by signature.
        """
        app = MagicMock()
        reactor = Reactor(app)
        # Patch __loadCommands to inject fake commands
        with patch.object(reactor, '_Reactor__loadCommands'):
            reactor._Reactor__commands = {
                'b:cmd': MagicMock(signature='b:cmd', description='desc', timestamps=True),
                'a:cmd': MagicMock(signature='a:cmd', description='desc', timestamps=False)
            }
            info = reactor.info()
            self.assertEqual(info[0]['signature'], 'a:cmd')
            self.assertEqual(info[1]['signature'], 'b:cmd')

    async def testCallRaisesOnMissingCommand(self):
        """
        Tests that call() raises CLIOrionisValueError if the command is not found.

        Notes
        -----
        Ensures that an exception is raised when calling a non-existent command.
        """
        from orionis.console.exceptions import CLIOrionisValueError
        app = MagicMock()
        reactor = Reactor(app)
        with self.assertRaises(CLIOrionisValueError):
            await asyncio.to_thread(reactor.call, 'not:found')

    async def testEnsureSignatureValidatesCorrectly(self):
        """
        Tests that __ensureSignature accepts valid signatures and rejects invalid ones.

        Notes
        -----
        Ensures that only valid signature formats are accepted.
        """
        app = MagicMock()
        reactor = Reactor(app)
        class Dummy:
            signature = 'valid:signature'
        # Should not raise
        self.assertEqual(reactor._Reactor__ensureSignature(Dummy), 'valid:signature')
        class BadDummy:
            signature = '1bad:signature'
        with self.assertRaises(Exception):
            reactor._Reactor__ensureSignature(BadDummy)
