from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_debug import DummyDebug

class TestIDebug(AsyncTestCase):

    async def testDdTerminatesProgram(self):
        """
        Test that dd() terminates the program as expected.

        This test verifies that calling dd() raises SystemExit and sets the correct arguments.
        """
        debug = DummyDebug()
        try:
            debug.dd(1, 'a', None)
        except SystemExit as e:
            self.assertTrue(debug.dd_called)
            self.assertEqual(debug.dd_args, (1, 'a', None))
            self.assertEqual(e.code, 0)
        else:
            self.fail('SystemExit was not raised by dd()')

    async def testDumpStoresArguments(self):
        """
        Test that dump() stores the arguments correctly.

        This test checks that the dump() method is called and arguments are stored as expected.
        """
        debug = DummyDebug()
        debug.dump(42, {'key': 'value'})
        self.assertTrue(debug.dump_called)
        self.assertEqual(debug.dump_args, (42, {'key': 'value'}))

    async def testDdWithNoArguments(self):
        """
        Test dd() with no arguments.

        This test ensures that dd() can be called without arguments and still terminates the program.
        """
        debug = DummyDebug()
        try:
            debug.dd()
        except SystemExit as e:
            self.assertTrue(debug.dd_called)
            self.assertEqual(debug.dd_args, ())
            self.assertEqual(e.code, 0)
        else:
            self.fail('SystemExit was not raised by dd() with no arguments')

    async def testDumpWithMultipleArguments(self):
        """
        Test dump() with multiple arguments.

        This test verifies that dump() can handle multiple arguments of different types.
        """
        debug = DummyDebug()
        debug.dump(1, 2, 3, 'test', [1, 2, 3])
        self.assertTrue(debug.dump_called)
        self.assertEqual(debug.dump_args, (1, 2, 3, 'test', [1, 2, 3]))
