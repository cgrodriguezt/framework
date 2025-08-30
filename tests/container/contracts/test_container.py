from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.container.contracts.container import IContainer

class TestIContainer(AsyncTestCase):

    async def testSingletonRegistration(self):
        """
        Test that a service can be registered as a singleton in the container.

        This test verifies that the `singleton` method of the container implementation
        correctly registers a service as a singleton, ensuring that the registration
        process returns a truthy value.

        Returns
        -------
        None
            This method does not return a value. The test will pass if the singleton
            registration returns True, otherwise it will fail.
        """

        # Define a dummy service interface
        class DummyService:
            pass

        # Define a dummy implementation of the service
        class DummyImplementation(DummyService):
            pass

        # Create a mock container implementation with stubbed methods
        class ContainerImpl(IContainer):
            # Always return True for singleton registration
            def singleton(self, *a, **k): return True
            def transient(self, *a, **k): return True
            def scoped(self, *a, **k): return True
            def scopedInstance(self, *a, **k): return True
            def instance(self, *a, **k): return True
            def callable(self, *a, **k): return True
            def bound(self, *a, **k): return True
            def getBinding(self, *a, **k): return None
            def drop(self, *a, **k): return None
            def createContext(self): return self
            def resolveDependencyArguments(self, *a, **k): return {}
            def make(self, *a, **k): return DummyImplementation()
            def resolve(self, *a, **k): return DummyImplementation()
            def resolveWithoutContainer(self, *a, **k): return DummyImplementation()
            def call(self, *a, **k): return None
            async def callAsync(self, *a, **k): return None
            def invoke(self, *a, **k): return None
            async def invokeAsync(self, *a, **k): return None

        # Instantiate the container
        container = ContainerImpl()

        # Attempt to register the DummyService as a singleton
        result = container.singleton(DummyService, DummyImplementation)

        # Assert that the registration was successful
        self.assertTrue(result)

    async def testTransientRegistration(self):
        """
        Test that a service can be registered as transient in the container.

        This test ensures that the `transient` method of the container implementation
        correctly registers a service as transient. It verifies that the registration
        process returns a truthy value, indicating successful registration.

        Returns
        -------
        None
            This method does not return a value. The test passes if the transient
            registration returns True, otherwise it fails.
        """
        # Define a dummy service interface
        class DummyService:
            pass

        # Define a dummy implementation of the service interface
        class DummyImplementation(DummyService):
            pass

        # Create a mock container implementation with stubbed methods
        class ContainerImpl(IContainer):
            # Always return True for singleton registration
            def singleton(self, *a, **k): return True
            # Always return True for transient registration
            def transient(self, *a, **k): return True
            # Always return True for scoped registration
            def scoped(self, *a, **k): return True
            # Always return True for scopedInstance registration
            def scopedInstance(self, *a, **k): return True
            # Always return True for instance registration
            def instance(self, *a, **k): return True
            # Always return True for callable registration
            def callable(self, *a, **k): return True
            # Always return True for bound registration
            def bound(self, *a, **k): return True
            # Always return None for getBinding
            def getBinding(self, *a, **k): return None
            # Always return None for drop
            def drop(self, *a, **k): return None
            # Return self for createContext
            def createContext(self): return self
            # Return empty dict for resolveDependencyArguments
            def resolveDependencyArguments(self, *a, **k): return {}
            # Always return a new DummyImplementation for make
            def make(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolve
            def resolve(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolveWithoutContainer
            def resolveWithoutContainer(self, *a, **k): return DummyImplementation()
            # Always return None for call
            def call(self, *a, **k): return None
            # Always return None for callAsync
            async def callAsync(self, *a, **k): return None
            # Always return None for invoke
            def invoke(self, *a, **k): return None
            # Always return None for invokeAsync
            async def invokeAsync(self, *a, **k): return None

        # Instantiate the container
        container = ContainerImpl()
        # Attempt to register the DummyService as a transient
        result = container.transient(DummyService, DummyImplementation)
        # Assert that the registration was successful
        self.assertTrue(result)

    async def testScopedRegistration(self):
        """
        Test that a service can be registered as scoped in the container.

        This test verifies that the `scoped` method of the container implementation
        correctly registers a service with a scoped lifetime. It ensures that the
        registration process returns a truthy value, indicating successful registration.

        Returns
        -------
        None
            This method does not return a value. The test passes if the scoped
            registration returns True, otherwise it fails.
        """
        # Define a dummy service interface to be registered
        class DummyService:
            pass

        # Define a dummy implementation of the service interface
        class DummyImplementation(DummyService):
            pass

        # Create a mock container implementation with stubbed methods
        class ContainerImpl(IContainer):
            # Always return True for singleton registration
            def singleton(self, *a, **k): return True
            # Always return True for transient registration
            def transient(self, *a, **k): return True
            # Always return True for scoped registration
            def scoped(self, *a, **k): return True
            # Always return True for scopedInstance registration
            def scopedInstance(self, *a, **k): return True
            # Always return True for instance registration
            def instance(self, *a, **k): return True
            # Always return True for callable registration
            def callable(self, *a, **k): return True
            # Always return True for bound registration
            def bound(self, *a, **k): return True
            # Always return None for getBinding
            def getBinding(self, *a, **k): return None
            # Always return None for drop
            def drop(self, *a, **k): return None
            # Return self for createContext
            def createContext(self): return self
            # Return empty dict for resolveDependencyArguments
            def resolveDependencyArguments(self, *a, **k): return {}
            # Always return a new DummyImplementation for make
            def make(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolve
            def resolve(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolveWithoutContainer
            def resolveWithoutContainer(self, *a, **k): return DummyImplementation()
            # Always return None for call
            def call(self, *a, **k): return None
            # Always return None for callAsync
            async def callAsync(self, *a, **k): return None
            # Always return None for invoke
            def invoke(self, *a, **k): return None
            # Always return None for invokeAsync
            async def invokeAsync(self, *a, **k): return None

        # Instantiate the mock container
        container = ContainerImpl()
        # Attempt to register the DummyService as scoped
        result = container.scoped(DummyService, DummyImplementation)
        # Assert that the registration was successful
        self.assertTrue(result)

    async def testInstanceRegistration(self):
        """
        Test that an instance can be registered in the container using the `instance` method.

        This test verifies that the container's `instance` method correctly registers a specific
        instance for a given service interface. It ensures that the registration process returns
        a truthy value, indicating that the instance was successfully registered.

        Returns
        -------
        None
            This method does not return a value. The test passes if the instance registration
            returns True, otherwise it fails.
        """
        # Define a dummy service interface
        class DummyService:
            pass

        # Define a dummy implementation of the service interface
        class DummyImplementation(DummyService):
            pass

        # Create a mock container implementation with stubbed methods
        class ContainerImpl(IContainer):
            # Always return True for singleton registration
            def singleton(self, *a, **k): return True
            # Always return True for transient registration
            def transient(self, *a, **k): return True
            # Always return True for scoped registration
            def scoped(self, *a, **k): return True
            # Always return True for scopedInstance registration
            def scopedInstance(self, *a, **k): return True
            # Always return True for instance registration
            def instance(self, *a, **k): return True
            # Always return True for callable registration
            def callable(self, *a, **k): return True
            # Always return True for bound registration
            def bound(self, *a, **k): return True
            # Always return None for getBinding
            def getBinding(self, *a, **k): return None
            # Always return None for drop
            def drop(self, *a, **k): return None
            # Return self for createContext
            def createContext(self): return self
            # Return empty dict for resolveDependencyArguments
            def resolveDependencyArguments(self, *a, **k): return {}
            # Always return a new DummyImplementation for make
            def make(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolve
            def resolve(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolveWithoutContainer
            def resolveWithoutContainer(self, *a, **k): return DummyImplementation()
            # Always return None for call
            def call(self, *a, **k): return None
            # Always return None for callAsync
            async def callAsync(self, *a, **k): return None
            # Always return None for invoke
            def invoke(self, *a, **k): return None
            # Always return None for invokeAsync
            async def invokeAsync(self, *a, **k): return None

        # Instantiate the mock container
        container = ContainerImpl()
        # Create an instance of the dummy implementation
        instance = DummyImplementation()
        # Attempt to register the instance for the DummyService interface
        result = container.instance(DummyService, instance)
        # Assert that the registration was successful
        self.assertTrue(result)

    async def testMakeResolvesInstance(self):
        """
        Test that the `make` method resolves and returns an instance of the expected implementation.

        This test ensures that the container's `make` method correctly resolves a service interface
        and returns an instance of the registered implementation. It verifies that the returned object
        is an instance of `DummyImplementation`, confirming that the resolution process works as intended.

        Parameters
        ----------
        self : TestIContainer
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. The test passes if the resolved instance is of type
            `DummyImplementation`, otherwise it fails.
        """
        # Define a dummy service interface
        class DummyService:
            pass

        # Define a dummy implementation of the service interface
        class DummyImplementation(DummyService):
            pass

        # Create a mock container implementation with stubbed methods
        class ContainerImpl(IContainer):
            # Always return True for singleton registration
            def singleton(self, *a, **k): return True
            # Always return True for transient registration
            def transient(self, *a, **k): return True
            # Always return True for scoped registration
            def scoped(self, *a, **k): return True
            # Always return True for scopedInstance registration
            def scopedInstance(self, *a, **k): return True
            # Always return True for instance registration
            def instance(self, *a, **k): return True
            # Always return True for callable registration
            def callable(self, *a, **k): return True
            # Always return True for bound registration
            def bound(self, *a, **k): return True
            # Always return None for getBinding
            def getBinding(self, *a, **k): return None
            # Always return None for drop
            def drop(self, *a, **k): return None
            # Return self for createContext
            def createContext(self): return self
            # Return empty dict for resolveDependencyArguments
            def resolveDependencyArguments(self, *a, **k): return {}
            # Always return a new DummyImplementation for make
            def make(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolve
            def resolve(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolveWithoutContainer
            def resolveWithoutContainer(self, *a, **k): return DummyImplementation()
            # Always return None for call
            def call(self, *a, **k): return None
            # Always return None for callAsync
            async def callAsync(self, *a, **k): return None
            # Always return None for invoke
            def invoke(self, *a, **k): return None
            # Always return None for invokeAsync
            async def invokeAsync(self, *a, **k): return None

        # Instantiate the mock container
        container = ContainerImpl()
        # Use the make method to resolve an instance of DummyService
        instance = container.make(DummyService)
        # Assert that the returned instance is of type DummyImplementation
        self.assertIsInstance(instance, DummyImplementation)

    async def testCallAsyncMethod(self):
        """
        Test that the container's `callAsync` method can be awaited and returns the expected result.

        This test verifies that the `callAsync` method of the container implementation is awaitable
        and returns the correct value when invoked. It ensures that asynchronous service method calls
        are handled properly by the container.

        Returns
        -------
        None
            This method does not return a value. The test passes if the awaited result from
            `callAsync` matches the expected value, otherwise it fails.
        """
        # Define a dummy service interface
        class DummyService:
            pass

        # Define a dummy implementation of the service interface
        class DummyImplementation(DummyService):
            pass

        # Create a mock container implementation with stubbed methods
        class ContainerImpl(IContainer):
            # Always return True for singleton registration
            def singleton(self, *a, **k): return True
            # Always return True for transient registration
            def transient(self, *a, **k): return True
            # Always return True for scoped registration
            def scoped(self, *a, **k): return True
            # Always return True for scopedInstance registration
            def scopedInstance(self, *a, **k): return True
            # Always return True for instance registration
            def instance(self, *a, **k): return True
            # Always return True for callable registration
            def callable(self, *a, **k): return True
            # Always return True for bound registration
            def bound(self, *a, **k): return True
            # Always return None for getBinding
            def getBinding(self, *a, **k): return None
            # Always return None for drop
            def drop(self, *a, **k): return None
            # Return self for createContext
            def createContext(self): return self
            # Return empty dict for resolveDependencyArguments
            def resolveDependencyArguments(self, *a, **k): return {}
            # Always return a new DummyImplementation for make
            def make(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolve
            def resolve(self, *a, **k): return DummyImplementation()
            # Always return a new DummyImplementation for resolveWithoutContainer
            def resolveWithoutContainer(self, *a, **k): return DummyImplementation()
            # Always return None for call
            def call(self, *a, **k): return None
            # Always return the string "async_result" for callAsync
            async def callAsync(self, *a, **k): return "async_result"
            # Always return None for invoke
            def invoke(self, *a, **k): return None
            # Always return None for invokeAsync
            async def invokeAsync(self, *a, **k): return None

        # Instantiate the mock container
        container = ContainerImpl()
        # Await the callAsync method and capture the result
        result = await container.callAsync(DummyImplementation(), "__str__")
        # Assert that the result matches the expected value
        self.assertEqual(result, "async_result")
