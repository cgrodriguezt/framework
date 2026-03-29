from abc import ABC
from orionis.test import TestCase
from orionis.container.container import Container
from orionis.container.contracts.container import IContainer
from orionis.container.context.manager import ScopeManager
from orionis.container.exceptions.container import CircularDependencyException

# ---------------------------------------------------------------------------
# Module-level domain helpers
# (must live at module scope so qualified names are stable for DI resolution)
# ---------------------------------------------------------------------------

class _Plain:
    """No-dependency service."""


class _IAbstract(ABC):
    """Minimal abstract contract."""


class _ConcreteA(_Plain, _IAbstract):
    """Satisfies both _Plain and _IAbstract."""


class _NeedsPlain:
    """Service with a single _Plain dependency."""

    def __init__(self, dep: _Plain) -> None:
        self.dep = dep

# Circular dependency pair — patched after both classes are defined so that
# annotations are real class references (not strings), which the reflection
# engine can resolve correctly.
class _CircA:
    """Circular dep node A — constructor patched below."""

class _CircB:
    """Circular dep node B — depends on _CircA."""

    def __init__(self, a: _CircA) -> None:
        self.a = a

def _circa_init(self, b: _CircB) -> None:
    """Patched constructor that closes the A→B→A cycle."""
    self.b = b

_CircA.__init__ = _circa_init  # type: ignore[method-assign]

class _Host:
    """Object used to test call() DI dispatch."""

    non_callable: str = "string_value"

    def greet(self) -> str:
        return "hello"

    def echo(self, dep: _Plain) -> _Plain:
        return dep

def _fn_no_dep() -> str:
    """Plain synchronous function with no dependencies."""
    return "ok"


def _fn_with_dep(dep: _Plain) -> _Plain:
    """Synchronous function declaring a _Plain dependency."""
    return dep

async def _afn_no_dep() -> str: # NOSONAR
    """Async function with no dependencies."""
    return "async_ok"


# ---------------------------------------------------------------------------
# Container isolation factory
# ---------------------------------------------------------------------------

def _fresh() -> Container:
    """
    Return an isolated Container instance.

    Every call executes a ``class`` statement, producing a *new* class object.
    Container stores singletons keyed by class, so each returned container has
    its own, completely private state.

    Returns
    -------
    Container
        A brand-new container instance with no registrations.
    """
    class _Isolated(Container):
        pass

    return _Isolated()

# ===========================================================================
# IContainer contract
# ===========================================================================

class TestIContainerContract(TestCase):

    def testCannotInstantiateDirectly(self) -> None:
        """
        Test that IContainer cannot be directly instantiated.

        IContainer is abstract; instantiating it must raise TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            IContainer()  # type: ignore[abstract]

    def testIsAbstractBaseClass(self) -> None:
        """
        Test that IContainer is registered as a subclass of ABC.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(IContainer, ABC))

    def testAllRequiredAbstractMethodsAreDeclared(self) -> None:
        """
        Test that IContainer declares all expected abstract method names.

        Ensures that refactoring never silently removes a critical contract
        method.

        Returns
        -------
        None
            This method does not return a value.
        """
        expected = {
            "instance", "transient", "singleton", "scoped",
            "bound", "beginScope", "getCurrentScope",
            "make", "build", "invoke", "call",
        }
        for name in expected:
            self.assertTrue(
                hasattr(IContainer, name),
                f"IContainer is missing declared method: {name!r}",
            )

# ===========================================================================
# Container — singleton pattern & contract
# ===========================================================================

class TestContainerSingleton(TestCase):

    def testSameClassReturnsSameInstance(self) -> None:
        """
        Test that constructing the same Container subclass twice yields the same object.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _S(Container):
            pass

        self.assertIs(_S(), _S())

    def testDifferentSubclassesYieldDifferentInstances(self) -> None:
        """
        Test that two distinct Container subclasses produce independent singletons.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _X(Container):
            pass

        class _Y(Container):
            pass

        self.assertIsNot(_X(), _Y())

    def testContainerImplementsIContainer(self) -> None:
        """
        Test that a Container instance satisfies the IContainer contract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(_fresh(), IContainer)

# ===========================================================================
# instance()
# ===========================================================================

class TestContainerInstance(TestCase):

    def testRegisterInstanceReturnsTrue(self) -> None:
        """
        Test that instance() returns True on a successful registration.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Svc:
            pass
        c = _fresh()
        self.assertTrue(c.instance(None, _Svc()))

    def testRegisterInstanceWithExplicitAbstract(self) -> None:
        """
        Test that instance() accepts an explicit abstract contract and returns True.

        Returns
        -------
        None
            This method does not return a value.
        """
        from abc import ABC
        class _ISvc(ABC):
            pass
        class _SvcImpl(_ISvc):
            pass
        c = _fresh()
        self.assertTrue(c.instance(_ISvc, _SvcImpl()))

    def testRegisterClassTypeRaisesTypeError(self) -> None:
        """
        Test that passing a class (not an instance) to instance() raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(TypeError):
            c.instance(None, _Plain)  # type: ignore[arg-type]

    def testRegisterInstanceMismatchRaisesTypeError(self) -> None:
        """
        Test that registering an instance that does not implement the abstract raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(TypeError):
            c.instance(_IAbstract, _Plain())  # _Plain does not extend _IAbstract

    def testRegisterDuplicateWithoutOverrideRaisesValueError(self) -> None:
        """
        Test that registering the same abstract twice without override raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Svc:
            pass
        c = _fresh()
        c.instance(None, _Svc())
        with self.assertRaises(ValueError):
            c.instance(None, _Svc())

    def testRegisterDuplicateWithOverrideSucceeds(self) -> None:
        """
        Test that re-registering with override=True does not raise and returns True.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Svc:
            pass
        c = _fresh()
        c.instance(None, _Svc())
        self.assertTrue(c.instance(None, _Svc(), override=True))

    async def testRegisterInstanceWithAliasInsideScopeRaisesValueError(self) -> None:
        """
        Test that registering an instance with an alias while a scope is active raises ValueError.

        Alias registration is only allowed globally, not inside a scope.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        async with c.beginScope():
            with self.assertRaises(ValueError):
                c.instance(None, _Plain(), alias="scoped_alias")

# ===========================================================================
# transient()
# ===========================================================================

class TestContainerTransient(TestCase):

    def testTransientReturnsTrue(self) -> None:
        """
        Test that transient() returns True on a valid registration.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(_fresh().transient(None, _Plain))

    def testTransientWithoutAbstractSelfBinds(self) -> None:
        """
        Test that transient(None, Concrete) binds the concrete to itself.

        After registration, bound(Concrete) must return True.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.transient(None, _Plain)
        self.assertTrue(c.bound(_Plain))

    def testTransientWithAbstractBindsContract(self) -> None:
        """
        Test that transient with an explicit abstract registers the abstract correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.transient(_IAbstract, _ConcreteA)
        self.assertTrue(c.bound(_IAbstract))

    def testTransientConcreteNotClassRaisesTypeError(self) -> None:
        """
        Test that providing a non-class as the concrete argument raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(TypeError):
            c.transient(None, "not_a_class")  # type: ignore[arg-type]

    def testTransientDuplicateRaisesValueError(self) -> None:
        """
        Test that registering the same abstract twice without override raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.transient(None, _Plain)
        with self.assertRaises(ValueError):
            c.transient(None, _Plain)

    async def testTransientMakeReturnsNewInstanceEachTime(self) -> None:
        """
        Test that every make() call on a transient binding returns a distinct object.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Svc:
            pass
        c = _fresh()
        c.transient(None, _Svc)
        i1 = await c.make(_Svc)
        i2 = await c.make(_Svc)
        self.assertIsNot(i1, i2)

# ===========================================================================
# singleton()
# ===========================================================================

class TestContainerSingletonBinding(TestCase):

    def testSingletonReturnsTrue(self) -> None:
        """
        Test that singleton() returns True on a valid registration.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(_fresh().singleton(None, _Plain))

    async def testSingletonMakeReturnsSameInstanceEveryTime(self) -> None:
        """
        Test that make() on a singleton binding always returns the same cached object.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Svc:
            pass
        c = _fresh()
        c.singleton(None, _Svc)
        i1 = await c.make(_Svc)
        i2 = await c.make(_Svc)
        self.assertIs(i1, i2)

    def testSingletonDuplicateRaisesValueError(self) -> None:
        """
        Test that registering the same singleton abstract twice without override raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.singleton(None, _Plain)
        with self.assertRaises(ValueError):
            c.singleton(None, _Plain)

# ===========================================================================
# scoped()
# ===========================================================================

class TestContainerScopedBinding(TestCase):

    def testScopedReturnsTrue(self) -> None:
        """
        Test that scoped() returns True on a valid registration.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(_fresh().scoped(None, _Plain))

    async def testScopedServiceResolvesInsideScope(self) -> None:
        """
        Test that a scoped service is resolved successfully within an active scope.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.scoped(None, _Plain)
        async with c.beginScope():
            self.assertIsInstance(await c.make(_Plain), _Plain)

    async def testScopedServiceReturnsSameInstanceWithinScope(self) -> None:
        """
        Test that multiple make() calls within the same scope return identical instances.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.scoped(None, _Plain)
        async with c.beginScope():
            i1 = await c.make(_Plain)
            i2 = await c.make(_Plain)
            self.assertIs(i1, i2)

    async def testScopedServiceRaisesRuntimeErrorOutsideScope(self) -> None:
        """
        Test that resolving a scoped service without an active scope raises RuntimeError.

        The test runner keeps a scope active at all times, so the reactor scope is
        temporarily cleared with a ContextVar token to simulate a truly scope-free
        context, then restored in the finally block.

        Returns
        -------
        None
            This method does not return a value.
        """
        from orionis.container.context.scope import ScopedContext
        c = _fresh()
        c.scoped(None, _Plain)
        # Temporarily clear the reactor scope to test the no-scope error path.
        token = ScopedContext.setCurrentScope(None)
        try:
            with self.assertRaises(RuntimeError):
                await c.make(_Plain)
        finally:
            ScopedContext.reset(token)

# ===========================================================================
# bound()
# ===========================================================================

class TestContainerBound(TestCase):

    def testBoundReturnsTrueAfterTransientRegistration(self) -> None:
        """
        Test that bound() returns True immediately after a transient registration.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.transient(None, _Plain)
        self.assertTrue(c.bound(_Plain))

    def testBoundReturnsFalseForUnregisteredType(self) -> None:
        """
        Test that bound() returns False for a type that has never been registered.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertFalse(_fresh().bound(_Plain))

    def testBoundReturnsTrueForRegisteredAlias(self) -> None:
        """
        Test that bound() returns True when queried with a valid alias string.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.transient(None, _Plain, alias="plain_svc")
        self.assertTrue(c.bound("plain_svc"))

    def testBoundReturnsFalseForUnknownAlias(self) -> None:
        """
        Test that bound() returns False for a string alias that was never registered.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertFalse(_fresh().bound("nonexistent_alias"))

    def testBoundReturnsTrueAfterInstanceRegistration(self) -> None:
        """
        Test that bound() returns True after registering an object instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Svc:
            pass
        c = _fresh()
        c.instance(None, _Svc())
        self.assertTrue(c.bound(_Svc))

# ===========================================================================
# Alias validation
# ===========================================================================

class TestContainerAlias(TestCase):

    def testEmptyAliasRaisesValueError(self) -> None:
        """
        Test that a blank-only alias string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(ValueError):
            c.transient(None, _Plain, alias="   ")

    def testNonStringAliasRaisesTypeError(self) -> None:
        """
        Test that a non-string alias raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(TypeError):
            c.transient(None, _Plain, alias=123)  # type: ignore[arg-type]

    def testDuplicateAliasRaisesValueError(self) -> None:
        """
        Test that two registrations using the same alias raise ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.transient(None, _Plain, alias="svc")
        with self.assertRaises(ValueError):
            c.transient(_IAbstract, _ConcreteA, alias="svc")

    async def testMakeByAliasReturnsCorrectType(self) -> None:
        """
        Test that make() with an alias string returns an instance of the registered type.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.transient(None, _Plain, alias="my_plain")
        self.assertIsInstance(await c.make("my_plain"), _Plain)

# ===========================================================================
# override parameter
# ===========================================================================

class TestContainerOverride(TestCase):

    def testOverrideFalseRaisesValueError(self) -> None:
        """
        Test that registering the same abstract twice with override=False raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.singleton(None, _Plain)
        with self.assertRaises(ValueError):
            c.singleton(None, _Plain, override=False)

    def testOverrideTrueReplacesExistingBinding(self) -> None:
        """
        Test that re-registering with override=True succeeds and returns True.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.singleton(_IAbstract, _ConcreteA)
        self.assertTrue(c.singleton(_IAbstract, _ConcreteA, override=True))

# ===========================================================================
# make()
# ===========================================================================

class TestContainerMake(TestCase):

    async def testMakeTransientReturnsNewInstanceEachCall(self) -> None:
        """
        Test that make() on a transient binding returns a different object every time.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Svc:
            pass
        c = _fresh()
        c.transient(None, _Svc)
        i1 = await c.make(_Svc)
        i2 = await c.make(_Svc)
        self.assertIsNot(i1, i2)

    async def testMakeSingletonReturnsSameObjectEachCall(self) -> None:
        """
        Test that make() on a singleton binding always returns the same cached instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Svc:
            pass
        c = _fresh()
        c.singleton(None, _Svc)
        self.assertIs(await c.make(_Svc), await c.make(_Svc))

    async def testMakeUnregisteredClassAutoResolves(self) -> None:
        """
        Test that make() auto-resolves an unregistered class with no constructor args.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        self.assertIsInstance(await c.make(_Plain), _Plain)

    async def testMakeUnregisteredStringRaisesValueError(self) -> None:
        """
        Test that make() raises ValueError when given an unknown string key.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(ValueError):
            await c.make("ghost_service")

    async def testMakeAbstractContractReturnsConcreteInstance(self) -> None:
        """
        Test that make() on an abstract key returns an instance of the concrete class.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.transient(_IAbstract, _ConcreteA)
        self.assertIsInstance(await c.make(_IAbstract), _ConcreteA)

# ===========================================================================
# build()
# ===========================================================================

class TestContainerBuild(TestCase):

    async def testBuildPlainClassReturnsInstance(self) -> None:
        """
        Test that build() creates and returns an instance of a plain no-arg class.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        self.assertIsInstance(await c.build(_Plain), _Plain)

    async def testBuildClassWithDepAutoResolvesConstructorArg(self) -> None:
        """
        Test that build() injects a _Plain dependency into _NeedsPlain automatically.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        instance = await c.build(_NeedsPlain)
        self.assertIsInstance(instance, _NeedsPlain)
        self.assertIsInstance(instance.dep, _Plain)

    async def testBuildNonClassRaisesTypeError(self) -> None:
        """
        Test that passing a non-class argument to build() raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(TypeError):
            await c.build("not_a_class")  # type: ignore[arg-type]

    async def testBuildAlwaysCreatesNewInstanceEvenForRegisteredSingleton(self) -> None:
        """
        Test that build() bypasses the singleton cache and always creates a fresh instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.singleton(None, _Plain)
        singleton = await c.make(_Plain)   # cached
        built = await c.build(_Plain)       # bypasses cache
        self.assertIsNot(singleton, built)

# ===========================================================================
# invoke()
# ===========================================================================

class TestContainerInvoke(TestCase):

    async def testInvokeSyncFunctionReturnsResult(self) -> None:
        """
        Test that invoke() executes a plain synchronous function and returns its result.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        self.assertEqual(await c.invoke(_fn_no_dep), "ok")

    async def testInvokeAsyncFunctionReturnsResult(self) -> None:
        """
        Test that invoke() awaits an async function and returns the correct result.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        self.assertEqual(await c.invoke(_afn_no_dep), "async_ok")

    async def testInvokeFunctionInjectedDependency(self) -> None:
        """
        Test that invoke() resolves and injects a _Plain dependency into _fn_with_dep.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        result = await c.invoke(_fn_with_dep)
        self.assertIsInstance(result, _Plain)

    async def testInvokeClassRaisesTypeError(self) -> None:
        """
        Test that passing a class type to invoke() raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(TypeError):
            await c.invoke(_Plain)  # type: ignore[arg-type]

# ===========================================================================
# call()
# ===========================================================================

class TestContainerCall(TestCase):

    async def testCallMethodReturnsCorrectResult(self) -> None:
        """
        Test that call() dispatches to the named method and returns its value.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        self.assertEqual(await c.call(_Host(), "greet"), "hello")

    async def testCallMissingMethodRaisesAttributeError(self) -> None:
        """
        Test that call() raises AttributeError when the method does not exist on the instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(AttributeError):
            await c.call(_Host(), "nonexistent_method")

    async def testCallNonCallableAttributeRaisesTypeError(self) -> None:
        """
        Test that call() raises TypeError when the named attribute is not callable.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        with self.assertRaises(TypeError):
            await c.call(_Host(), "non_callable")

    async def testCallMethodWithInjectedDependency(self) -> None:
        """
        Test that call() injects _Plain into _Host.echo() which declares it as a parameter.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        result = await c.call(_Host(), "echo")
        self.assertIsInstance(result, _Plain)

# ===========================================================================
# Circular dependency detection
# ===========================================================================

class TestContainerCircularDependency(TestCase):

    async def testCircularDependencyRaisesException(self) -> None:
        """
        Test that resolving mutually dependent classes raises CircularDependencyException.

        _CircA → _CircB → _CircA forms a cycle that the container must detect.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        c.transient(None, _CircA)
        c.transient(None, _CircB)
        with self.assertRaises(CircularDependencyException):
            await c.make(_CircB)

    async def testCircularDependencyExceptionIsSubclassOfException(self) -> None:
        """
        Test that CircularDependencyException is a subclass of the built-in Exception.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(CircularDependencyException, Exception))

# ===========================================================================
# Scope management: beginScope() / getCurrentScope()
# ===========================================================================

class TestContainerScopeManagement(TestCase):

    def testBeginScopeReturnsScopeManager(self) -> None:
        """
        Test that beginScope() returns a ScopeManager instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(_fresh().beginScope(), ScopeManager)

    def testGetCurrentScopeReturnsNoneOutsideScope(self) -> None:
        """
        Test that getCurrentScope() returns None when no scope is active.

        The test runner keeps a reactor scope active during execution, so this
        test temporarily clears the ContextVar to isolate the assertion.

        Returns
        -------
        None
            This method does not return a value.
        """
        from orionis.container.context.scope import ScopedContext
        token = ScopedContext.setCurrentScope(None)
        try:
            self.assertIsNone(_fresh().getCurrentScope())
        finally:
            ScopedContext.reset(token)

    async def testGetCurrentScopeReturnsActiveObjectInsideScope(self) -> None:
        """
        Test that getCurrentScope() returns a non-None object while inside an active scope.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        async with c.beginScope():
            self.assertIsNotNone(c.getCurrentScope())

    async def testGetCurrentScopeReturnsNoneAfterScopeExits(self) -> None:
        """
        Test that getCurrentScope() no longer returns the nested scope after its block exits.

        The reactor scope is always active, so this test verifies that after the
        nested scope terminates, the active scope is no longer that nested scope
        manager (it reverts to the outer reactor scope).

        Returns
        -------
        None
            This method does not return a value.
        """
        c = _fresh()
        async with c.beginScope() as nested:
            self.assertIs(c.getCurrentScope(), nested)
        # After exit the nested scope is no longer the active context.
        self.assertIsNot(c.getCurrentScope(), nested)

    async def testScopedInstanceIsNotVisibleOutsideScope(self) -> None:
        """
        Test that an instance registered inside a scope is cleared after the scope exits.

        After the nested scope exits the reactor scope is restored.  The scoped binding
        still exists globally, but without any scope that owns the cached instance the
        container must raise RuntimeError.  The reactor scope is temporarily cleared
        via a ContextVar token to simulate the no-scope condition.

        Returns
        -------
        None
            This method does not return a value.
        """
        from orionis.container.context.scope import ScopedContext
        c = _fresh()
        c.scoped(None, _Plain)
        async with c.beginScope():
            instance_inside = await c.make(_Plain)
            self.assertIsInstance(instance_inside, _Plain)
        # After the nested scope exits, temporarily clear the reactor scope so that
        # the scoped resolution fails as expected.
        token = ScopedContext.setCurrentScope(None)
        try:
            with self.assertRaises(RuntimeError):
                await c.make(_Plain)
        finally:
            ScopedContext.reset(token)
