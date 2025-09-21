from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_console import DummyConsole

class TestIConsole(AsyncTestCase):

    async def testSuccess(self):
        """
        Test the success method records the correct call.

        Notes
        -----
        Ensures that calling success() appends the correct tuple to the calls list.
        """
        console = DummyConsole()
        console.success('Operation completed', timestamp=True)
        self.assertIn(('success', 'Operation completed', True), console.calls)

    async def testTextSuccessBold(self):
        """
        Test the textSuccessBold method records the correct call.

        Notes
        -----
        Ensures that calling textSuccessBold() appends the correct tuple to the calls list.
        """
        console = DummyConsole()
        console.textSuccessBold('Bold success')
        self.assertIn(('textSuccessBold', 'Bold success'), console.calls)

    async def testInfoWithTimestamp(self):
        """
        Test the info method with timestamp argument.

        Notes
        -----
        Checks that info() records the message and timestamp flag.
        """
        console = DummyConsole()
        console.info('Information', timestamp=False)
        self.assertIn(('info', 'Information', False), console.calls)

    async def testWarning(self):
        """
        Test the warning method records the correct call.

        Notes
        -----
        Ensures that calling warning() appends the correct tuple to the calls list.
        """
        console = DummyConsole()
        console.warning('Warning message')
        self.assertEqual(console.calls[0][0], 'warning')

    async def testFail(self):
        """
        Test the fail method records the correct call.

        Notes
        -----
        Ensures that calling fail() appends the correct tuple to the calls list.
        """
        console = DummyConsole()
        console.fail('Failure occurred')
        self.assertEqual(console.calls[0][0], 'fail')

    async def testAskReturnsDummy(self):
        """
        Test the ask method returns a dummy string.

        Notes
        -----
        Ensures that ask() returns 'dummy' and records the call.
        """
        console = DummyConsole()
        result = console.ask('What is your name?')
        self.assertEqual(result, 'dummy')
        self.assertIn(('ask', 'What is your name?'), console.calls)

    async def testConfirmDefault(self):
        """
        Test the confirm method returns the default value.

        Notes
        -----
        Ensures that confirm() returns the default argument and records the call.
        """
        console = DummyConsole()
        result = console.confirm('Are you sure?', default=True)
        self.assertTrue(result)
        self.assertIn(('confirm', 'Are you sure?', True), console.calls)

    async def testTable(self):
        """
        Test the table method records headers and rows.

        Notes
        -----
        Ensures that table() appends the correct tuple to the calls list.
        """
        console = DummyConsole()
        headers = ['Name', 'Age']
        rows = [['Alice', '30'], ['Bob', '25']]
        console.table(headers, rows)
        self.assertIn(('table', headers, rows), console.calls)

    async def testChoiceReturnsDefault(self):
        """
        Test the choice method returns the default choice.

        Notes
        -----
        Ensures that choice() returns the default choice and records the call.
        """
        console = DummyConsole()
        choices = ['A', 'B', 'C']
        result = console.choice('Pick one:', choices, default_index=1)
        self.assertEqual(result, 'B')
        self.assertIn(('choice', 'Pick one:', choices, 1), console.calls)

    async def testException(self):
        """
        Test the exception method records the exception message.

        Notes
        -----
        Ensures that exception() appends the exception message to the calls list.
        """
        console = DummyConsole()
        try:
            raise ValueError('Test error')
        except Exception as e:
            console.exception(e)
        self.assertEqual(console.calls[0][0], 'exception')
        self.assertIn('Test error', console.calls[0][1])
