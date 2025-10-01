from orionis.console.contracts.reactor import IReactor
from orionis.console.core.reactor import Reactor
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.test.cases.asynchronous import AsyncTestCase

class TestConsoleReactor(AsyncTestCase):

    async def onAsyncSetup(self, reactor: IReactor):
        """
        Asynchronously sets up the test environment with the provided reactor instance.

        This method initializes the test case by assigning the given `reactor` to the
        `self.reactor` attribute and creates a `ReflectionInstance` for introspection,
        which is assigned to `self.rf_reactor`. This setup is required for subsequent
        tests that rely on these attributes to interact with and inspect the reactor.

        Parameters
        ----------
        reactor : IReactor
            The reactor instance to be used for testing.

        Returns
        -------
        None
            This method performs setup actions and does not return a value.
        """

        # Store the provided reactor instance for use in tests
        self.reactor = reactor

        # Create a ReflectionInstance for introspection of the reactor
        self.rf_reactor = ReflectionInstance(reactor)

    def testEnsurePrivateMethods(self):
        """
        Verify that the rf_reactor object implements all required private methods.

        This test checks for the existence of several private methods within the
        `rf_reactor` instance by asserting that the `hasMethod` function returns
        True for each expected method name. The methods checked are responsible
        for loading commands, ensuring timestamps, signatures, descriptions,
        arguments, and parsing arguments.

        Returns
        -------
        None
            This method performs assertions and does not return a value.
        """

        # Assert that the private method for loading commands exists
        self.assertTrue(self.rf_reactor.hasMethod("__loadCommands"))

        # Assert that the private method for loading fluent commands exists
        self.assertTrue(self.rf_reactor.hasMethod("__loadFluentCommands"))

        # Assert that the private method for loading core commands exists
        self.assertTrue(self.rf_reactor.hasMethod("__loadCoreCommands"))

        # Assert that the private method for loading custom commands exists
        self.assertTrue(self.rf_reactor.hasMethod("__loadCustomCommands"))

        # Assert that the private method for ensuring timestamps exists
        self.assertTrue(self.rf_reactor.hasMethod("__ensureTimestamps"))

        # Assert that the private method for ensuring signatures exists
        self.assertTrue(self.rf_reactor.hasMethod("__ensureSignature"))

        # Assert that the private method for ensuring descriptions exists
        self.assertTrue(self.rf_reactor.hasMethod("__ensureDescription"))

        # Assert that the private method for ensuring arguments exists
        self.assertTrue(self.rf_reactor.hasMethod("__ensureArguments"))

        # Assert that the private method for parsing arguments exists
        self.assertTrue(self.rf_reactor.hasMethod("__parseArgs"))

    def testCoreCommands(self):
        """
        Checks that all expected core commands are registered in the reactor.

        This asynchronous test verifies that the set of native core commands is present
        in the list of commands returned by the reactor's `info()` method. It iterates
        through a predefined list of expected command names and asserts that each one
        exists in the signatures of the commands provided by the reactor.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs assertions to validate the presence of core commands
            and does not return any value.
        """

        # Define the list of expected native core command names
        native_commands = [
            "version",
            "help",
            "test",
            "cache:clear",
            "schedule:work",
            "schedule:list",
            "make:command",
            "log:clear"
        ]

        # Retrieve the list of available command signatures from the reactor
        signatures = [cmd.get('signature') for cmd in self.reactor.info()]

        # Assert that each expected native command is present in the reactor's command list
        for cmd in native_commands:
            self.assertIn(cmd, signatures)

    async def testCallCommand(self):
        """
        Tests the execution of a core command and verifies its output.

        This asynchronous test calls the 'version' command using the reactor's `call`
        method and captures the output. It then asserts that the output contains the
        expected version string, which is formatted as "Orionis Framework v{version}",
        where {version} is obtained from the reactor's `getVersion` method.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs assertions to validate the command execution and
            does not return any value.
        """

        # Call the 'version' command and capture the output
        output = await self.reactor.callAsync("version", ["--without-console"])

        # Ensure the output is a string in the format 'x.y.z' (e.g., '0.642.0')
        self.assertIsInstance(output, str)
        self.assertRegex(output, r'^\d+\.\d+\.\d+$')

        # Call the 'version' command synchronously and capture its output
        output = self.reactor.call("version", ["--without-console"])

        # Ensure the output is a string in the format 'x.y.z' (e.g., '0.642.0')
        self.assertIsInstance(output, str)
        self.assertRegex(output, r'^\d+\.\d+\.\d+$')

    def testImplementation(self):
        """
        Validates that all methods declared in the `IReactor` interface are implemented
        by the `Reactor` concrete class.

        This method uses reflection to retrieve the method names from both the interface
        (`IReactor`) and its concrete implementation (`Reactor`). It then checks that each
        method defined in the interface is also present in the implementation, ensuring
        interface compliance.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs assertions to verify method presence and does not return a value.
        """

        # Retrieve all method names from the interface using reflection
        rf_abstract = ReflectionAbstract(IReactor).getMethods()

        # Retrieve all method names from the concrete implementation using reflection
        rf_concrete = ReflectionConcrete(Reactor).getMethods()

        # Assert that every interface method is present in the concrete class
        for method in rf_abstract:
            self.assertIn(method, rf_concrete)  # Ensure method is implemented

    def testPropierties(self):
        """
        Validates that all properties declared in the `IReactor` interface are present
        in the `Reactor` concrete class.

        This method uses reflection to retrieve the property names from both the interface
        (`IReactor`) and its concrete implementation (`Reactor`). It then checks that each
        property defined in the interface is also present in the implementation, ensuring
        interface compliance.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The method performs assertions to verify property presence and does not return a value.
        """

        # Retrieve all property names from the interface using reflection
        rf_abstract = ReflectionAbstract(IReactor).getProperties()

        # Retrieve all property names from the concrete implementation using reflection
        rf_concrete = ReflectionConcrete(Reactor).getProperties()

        # Assert that every interface property is present in the concrete class
        for prop in rf_abstract:
            self.assertIn(prop, rf_concrete)  # Ensure property is implemented