import threading
from orionis.test import TestCase
from orionis.support.patterns.singleton.meta import Singleton


class TestSingletonMetaclass(TestCase):
    """Unit tests for the Singleton metaclass."""

    # ------------------------------------------------ basic usage

    def testSingletonReturnsInstance(self):
        """
        Return an instance when calling a singleton class.

        Validates that calling a class using the Singleton metaclass
        produces a valid object instance.
        """
        class MySingleton(metaclass=Singleton):
            pass

        obj = MySingleton()
        self.assertIsNotNone(obj)

    def testSingletonReturnsSameInstance(self):
        """
        Return the same instance on repeated calls.

        Validates that multiple calls to a singleton class always
        return the identical object.
        """
        class MySingleton(metaclass=Singleton):
            pass

        a = MySingleton()
        b = MySingleton()
        self.assertIs(a, b)

    def testSingletonInstanceIsStoredInInstances(self):
        """
        Store the singleton instance in the class-level dict.

        Validates that after creation, the instance is found in
        the Singleton._instances registry.
        """
        class MySingleton(metaclass=Singleton):
            pass

        obj = MySingleton()
        self.assertIn(MySingleton, Singleton._instances)
        self.assertIs(Singleton._instances[MySingleton], obj)

    def testSingletonPreservesInitArguments(self):
        """
        Preserve constructor arguments in the singleton instance.

        Validates that keyword arguments passed during the first
        instantiation are correctly stored on the instance.
        """
        class MySingleton(metaclass=Singleton):
            def __init__(self, value: int = 0) -> None:
                self.value = value

        obj = MySingleton(value=42)
        self.assertEqual(obj.value, 42)

    def testSingletonIgnoresSubsequentArgs(self):
        """
        Ignore constructor arguments on subsequent calls.

        Validates that after the first instantiation, subsequent
        calls with different arguments return the original instance.
        """
        class MySingleton(metaclass=Singleton):
            def __init__(self, value: int = 0) -> None:
                self.value = value

        first = MySingleton(value=1)
        second = MySingleton(value=99)
        self.assertIs(first, second)
        self.assertEqual(second.value, 1)

    # ------------------------------------------------ isolation

    def testTwoDistinctSingletonClassesAreIndependent(self):
        """
        Maintain separate instances for different singleton classes.

        Validates that two different classes using the Singleton
        metaclass each have their own independent instance.
        """
        class AlphaSingleton(metaclass=Singleton):
            pass

        class BetaSingleton(metaclass=Singleton):
            pass

        a = AlphaSingleton()
        b = BetaSingleton()
        self.assertIsNot(a, b)

    def testSingletonDoesNotShareInstanceAcrossClasses(self):
        """
        Prevent instance sharing across distinct singleton classes.

        Validates that the instance stored for one singleton class
        is not accessible under a different singleton class key.
        """
        class Foo(metaclass=Singleton):
            pass

        class Bar(metaclass=Singleton):
            pass

        _ = Foo()
        _ = Bar()
        self.assertIsNot(
            Singleton._instances[Foo],
            Singleton._instances[Bar],
        )

    # ------------------------------------------------ thread safety

    def testSingletonIsThreadSafe(self):
        """
        Create only one instance under concurrent thread access.

        Validates that creating a singleton from multiple threads
        simultaneously results in exactly one shared instance.
        """
        class ThreadSingleton(metaclass=Singleton):
            pass

        results: list = []

        def create() -> None:
            results.append(ThreadSingleton())

        threads = [threading.Thread(target=create) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        first = results[0]
        self.assertTrue(all(obj is first for obj in results))

    def testSingletonInstanceCountIsOne(self):
        """
        Produce exactly one instance despite concurrent calls.

        Validates that the set of unique instances created by
        concurrent threads contains only one object.
        """
        class ConcurrentSingleton(metaclass=Singleton):
            pass

        results: list = []

        def create() -> None:
            results.append(ConcurrentSingleton())

        threads = [threading.Thread(target=create) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        unique_ids = {id(obj) for obj in results}
        self.assertEqual(len(unique_ids), 1)

    # ------------------------------------------------ async usage

    async def testSingletonAcallReturnsInstance(self):
        """
        Return an instance from the async singleton accessor.

        Validates that __acall__ on a singleton class produces
        a valid object instance.
        """
        class AsyncSingleton(metaclass=Singleton):
            pass

        obj = await AsyncSingleton.__acall__()
        self.assertIsNotNone(obj)

    async def testSingletonAcallReturnsSameInstance(self):
        """
        Return the same instance from repeated async calls.

        Validates that multiple awaited calls to __acall__ return
        the identical singleton instance.
        """
        class AsyncSingleton2(metaclass=Singleton):
            pass

        a = await AsyncSingleton2.__acall__()
        b = await AsyncSingleton2.__acall__()
        self.assertIs(a, b)

    async def testSingletonAcallStoresInInstances(self):
        """
        Store the async-created singleton in the class-level dict.

        Validates that after __acall__, the instance is registered
        in the Singleton._instances registry.
        """
        class AsyncSingleton3(metaclass=Singleton):
            pass

        obj = await AsyncSingleton3.__acall__()
        self.assertIn(AsyncSingleton3, Singleton._instances)
        self.assertIs(Singleton._instances[AsyncSingleton3], obj)

    async def testSingletonSyncAndAsyncReturnSameInstance(self):
        """
        Unify sync and async singleton instances.

        Validates that calling a singleton class synchronously and
        then via __acall__ returns the same underlying instance.
        """
        class MixedSingleton(metaclass=Singleton):
            pass

        sync_obj = MixedSingleton()
        async_obj = await MixedSingleton.__acall__()
        self.assertIs(sync_obj, async_obj)

    # ------------------------------------------------ metaclass type

    def testSingletonMetaclassIsSubclassOfType(self):
        """
        Confirm Singleton is a subclass of type.

        Validates that the Singleton metaclass inherits from the
        built-in type, qualifying it as a valid metaclass.
        """
        self.assertTrue(issubclass(Singleton, type))

    def testClassCreatedWithSingletonHasSingletonAsMetaclass(self):
        """
        Use Singleton as the metaclass of the created class.

        Validates that the type of a class created with Singleton
        is the Singleton metaclass itself.
        """
        class MySingleton(metaclass=Singleton):
            pass

        self.assertIsInstance(MySingleton, Singleton)

    # ------------------------------------------------ edge cases

    def testSingletonClassWithNoInitArgs(self):
        """
        Create singleton from a class with no __init__ parameters.

        Validates that a singleton class requiring no arguments is
        instantiated and cached correctly.
        """
        class NoArgSingleton(metaclass=Singleton):
            label = "no-arg"

        obj = NoArgSingleton()
        self.assertEqual(obj.label, "no-arg")
        self.assertIs(obj, NoArgSingleton())

    def testSingletonWithAttributeMutation(self):
        """
        Persist attribute mutations on the singleton instance.

        Validates that changes to the singleton instance's attributes
        are reflected in any subsequent reference to the instance.
        """
        class MutableSingleton(metaclass=Singleton):
            def __init__(self) -> None:
                self.counter = 0

        obj1 = MutableSingleton()
        obj1.counter += 1
        obj2 = MutableSingleton()
        self.assertEqual(obj2.counter, 1)

    def testSingletonHasLockAttribute(self):
        """
        Expose a threading lock on the Singleton metaclass.

        Validates that the Singleton metaclass defines the _lock
        attribute used for thread-safe instantiation.
        """
        self.assertTrue(hasattr(Singleton, "_lock"))
        self.assertIsInstance(Singleton._lock, type(threading.Lock()))

    def testSingletonHasInstancesDict(self):
        """
        Expose the _instances registry on the Singleton metaclass.

        Validates that the Singleton metaclass maintains the
        _instances dict for storing created instances.
        """
        self.assertTrue(hasattr(Singleton, "_instances"))
        self.assertIsInstance(Singleton._instances, dict)
