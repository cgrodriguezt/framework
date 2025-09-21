from unittest.mock import Mock, patch
from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.tasks.schedule import Schedule
from orionis.console.exceptions import CLIOrionisValueError
from rich.console import Console

class TestSchedule(AsyncTestCase):

    async def asyncSetUp(self):
        """
        Set up mock dependencies required for testing the Schedule class.

        This method initializes mock objects that simulate the real dependencies
        expected by the Schedule class, including a mock reactor that provides
        command information, a mock application with configuration and service
        resolution, and a mock logger. It also creates a Console instance for
        output and instantiates the Schedule object to be tested.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Create mock reactor that returns commands in the expected dict format
        self.mock_reactor = Mock()
        self.mock_reactor.info.return_value = [
            {'signature': 'test:command', 'description': 'Test Command Description'},
            {'signature': 'another:cmd', 'description': 'Another Command Description'},
            {'signature': 'no:desc'}  # Command without description
        ]

        # Create mock application with proper config and service resolution
        self.mock_app = Mock()
        self.mock_app.config.side_effect = self._mockAppConfig

        # Mock logger and failure catch services
        self.mock_logger = Mock()
        self.mock_catch = Mock()

        # Configure app.make to return appropriate mocks based on service name
        def mock_make(service_name):
            if service_name == 'x-orionis.services.log.log_service':
                return self.mock_logger
            elif service_name == 'x-orionis.failure.catch':
                return self.mock_catch
            return Mock()

        self.mock_app.make.side_effect = mock_make

        # Create console for output (no file, no color)
        self.console = Console(file=None, force_terminal=False, color_system=None)

        # Instantiate the Schedule class with mocks
        self.schedule = Schedule(self.mock_reactor, self.mock_app, self.console)

    def _mockAppConfig(self, key, default=None):
        """
        Helper method to simulate application configuration retrieval.

        Parameters
        ----------
        key : str
            The configuration key to retrieve.
        default : Any, optional
            The default value to return if the key is not found.

        Returns
        -------
        Any
            The configuration value for the given key, or the default if not found.
        """
        config_map = {
            'app.timezone': 'UTC'
        }
        return config_map.get(key, default)

    async def testInitializationSuccess(self):
        """
        Test successful initialization of the Schedule class with valid dependencies.

        This test verifies that the Schedule instance is created, the reactor's
        info method is called, the logger service is requested, and the scheduler
        is not running initially.

        Returns
        -------
        None
        """
        # Verify that the schedule was created
        self.assertIsNotNone(self.schedule)

        # Verify that the reactor's info method was called during initialization
        self.mock_reactor.info.assert_called_once()

        # Verify that the logger service was requested
        self.mock_app.make.assert_any_call('x-orionis.services.log.log_service')

        # Verify that scheduler is not running initially
        self.assertFalse(self.schedule.isRunning())

    async def testCommandWithValidSignature(self):
        """
        Test scheduling a command with a valid signature.

        Ensures that valid commands are accepted and return proper Event instances.
        Also checks that commands with and without arguments are handled correctly.

        Returns
        -------
        None
        """
        # Schedule a valid command with arguments
        event = self.schedule.command('test:command', ['--arg1', 'value1'])

        # Verify event creation and convert to entity to access attributes
        self.assertIsNotNone(event)
        entity = event.toEntity()
        self.assertEqual(entity.signature, 'test:command')
        self.assertEqual(entity.args, ['--arg1', 'value1'])

        # Test command without arguments
        event_no_args = self.schedule.command('another:cmd')
        self.assertIsNotNone(event_no_args)
        entity_no_args = event_no_args.toEntity()
        self.assertEqual(entity_no_args.signature, 'another:cmd')
        self.assertEqual(entity_no_args.args, [])

    async def testCommandWithInvalidSignature(self):
        """
        Test that invalid command signatures raise appropriate exceptions.

        This test verifies that the validation logic properly rejects commands
        with non-existent, empty, or None signatures by raising CLIOrionisValueError.

        Returns
        -------
        None
        """
        # Test with non-existent command
        with self.assertRaises(CLIOrionisValueError) as context:
            self.schedule.command('invalid:command')
        self.assertIn("is not available or does not exist", str(context.exception))

        # Test with empty signature
        with self.assertRaises(CLIOrionisValueError) as context:
            self.schedule.command('')
        self.assertIn("must be a non-empty string", str(context.exception))

        # Test with None signature
        with self.assertRaises(CLIOrionisValueError):
            self.schedule.command(None)

    async def testCommandWithInvalidArguments(self):
        """
        Test that invalid argument types raise appropriate exceptions.

        This test verifies that passing arguments of incorrect types (e.g., not a list)
        to the command method raises CLIOrionisValueError.

        Returns
        -------
        None
        """
        # Test with non-list arguments
        with self.assertRaises(CLIOrionisValueError) as context:
            self.schedule.command('test:command', 'invalid_args')
        self.assertIn("must be a list of strings or None", str(context.exception))

    async def testGetDescriptionMethod(self):
        """
        Test the private __getDescription method for retrieving command descriptions.

        This test checks that command descriptions are properly retrieved for commands
        with and without descriptions, and returns None for non-existent commands.

        Returns
        -------
        None
        """
        # Test valid command with description
        desc = self.schedule._Schedule__getDescription('test:command')
        self.assertEqual(desc, 'Test Command Description')

        # Test command without description (should return default)
        desc_no_desc = self.schedule._Schedule__getDescription('no:desc')
        self.assertEqual(desc_no_desc, 'No description available.')

        # Test non-existent command
        desc_none = self.schedule._Schedule__getDescription('nonexistent:cmd')
        self.assertIsNone(desc_none)

    async def testIsAvailableMethod(self):
        """
        Test the private __isAvailable method for checking command availability.

        This test verifies that available commands return True and unavailable
        commands return False.

        Returns
        -------
        None
        """
        # Test available commands
        self.assertTrue(self.schedule._Schedule__isAvailable('test:command'))
        self.assertTrue(self.schedule._Schedule__isAvailable('another:cmd'))
        self.assertTrue(self.schedule._Schedule__isAvailable('no:desc'))

        # Test unavailable command
        self.assertFalse(self.schedule._Schedule__isAvailable('nonexistent:cmd'))

    async def testEventsInitialState(self):
        """
        Test that the events list is properly initialized and empty.

        This test verifies the initial state of the events tracking in the Schedule
        instance.

        Returns
        -------
        None
        """
        events = self.schedule.events()
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 0)

    async def testSchedulerNotRunningInitially(self):
        """
        Test that the scheduler is not running when first created.

        This test verifies the initial running state of the scheduler.

        Returns
        -------
        None
        """
        self.assertFalse(self.schedule.isRunning())

    async def testTimezoneConfiguration(self):
        """
        Test that timezone configuration is properly applied to the scheduler.

        This test verifies that the scheduler uses the configured timezone and that
        the logger is called to indicate the timezone assignment. It also checks the
        format of the current time string.

        Returns
        -------
        None
        """
        # Get current time to verify timezone handling
        current_time = self.schedule._Schedule__getCurrentTime()

        # Verify time format (YYYY-MM-DD HH:MM:SS)
        self.assertRegex(current_time, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

        # Verify logger was called for timezone assignment
        self.mock_logger.info.assert_called_with("Timezone assigned to the scheduler: UTC")

    async def testCommandPreventionWhenRunning(self):
        """
        Test that commands cannot be added while the scheduler is running.

        This test verifies that the scheduler properly prevents command addition
        during execution by raising a CLIOrionisValueError.

        Returns
        -------
        None
        """
        # Mock the scheduler as running
        with patch.object(self.schedule, 'isRunning', return_value=True):
            with patch.object(self.schedule, '_Schedule__raiseException') as mock_raise:
                self.schedule.command('test:command')
                mock_raise.assert_called_once()
                # Verify the exception type
                call_args = mock_raise.call_args[0][0]
                self.assertIsInstance(call_args, CLIOrionisValueError)
                self.assertIn("Cannot add new commands while the scheduler is running", str(call_args))
