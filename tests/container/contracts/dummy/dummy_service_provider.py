from orionis.container.contracts.service_provider import IServiceProvider

class DummyServiceProvider(IServiceProvider):
    """
    Dummy implementation of IServiceProvider for testing purposes.

    This class provides a mock implementation of the IServiceProvider interface,
    allowing tests to verify the behavior of service registration and bootstrapping
    without relying on actual service logic. It tracks whether the `register` and
    `boot` methods have been called by setting corresponding flags.

    Attributes
    ----------
    register_called : bool
        Indicates whether the `register` method has been called.
    boot_called : bool
        Indicates whether the `boot` method has been called.
    """

    def __init__(self):
        """
        Initializes the DummyServiceProvider instance.

        Sets the `register_called` and `boot_called` flags to False, which are used
        to track whether the `register` and `boot` methods have been invoked.

        Returns
        -------
        None
        """
        # Track if register() has been called
        self.register_called = False
        # Track if boot() has been called
        self.boot_called = False

    async def register(self) -> None:
        """
        Asynchronously registers the service provider.

        This method sets the `register_called` attribute to True to indicate that
        the registration process has been invoked. Intended for use in test scenarios
        to verify that the registration logic is executed.

        Returns
        -------
        None
        """
        # Mark that register() was called
        self.register_called = True

    async def boot(self) -> None:
        """
        Asynchronously performs bootstrapping actions for the service provider.

        This method sets the `boot_called` attribute to True to indicate that the
        boot process has been executed. Used in tests to confirm that bootstrapping
        logic is triggered as expected.

        Returns
        -------
        None
        """
        # Mark that boot() was called
        self.boot_called = True