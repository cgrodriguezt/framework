import inspect
from pathlib import Path
from orionis.container.contracts.container import IContainer
from orionis.foundation.contracts.application import IApplication
from orionis.foundation.contracts.application import _SENTINEL
from orionis.foundation.enums.lifespan import Lifespan
from orionis.foundation.enums.runtimes import Runtime
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.test import TestCase

# ===========================================================================
# Minimal concrete stub that fully satisfies IApplication (properties + all
# abstract methods from IApplication and IContainer).  Used only in those
# tests that need an instantiable subclass.
# ===========================================================================

class _FullConcreteApp(IApplication):
    """Complete IApplication implementation used to test contract enforcement."""

    # ---- IContainer abstract methods ----

    def instance(self, abstract, instance, *, alias=None, override=False):  # NOSONAR
        return True

    def transient(self, abstract, concrete, *, alias=None, override=False):  # NOSONAR
        return True

    def singleton(self, abstract, concrete, *, alias=None, override=False):  # NOSONAR
        return True

    def scoped(self, abstract, concrete, *, alias=None, override=False):  # NOSONAR
        return True

    def bound(self, key):  # NOSONAR
        return False

    def beginScope(self):  # NOSONAR
        return None

    def getCurrentScope(self):  # NOSONAR
        return None

    async def make(self, key, *args, **kwargs):  # NOSONAR
        return None

    async def build(self, type_, *args, **kwargs):  # NOSONAR
        return None

    async def invoke(self, fn, *args, **kwargs):  # NOSONAR
        return None

    async def call(self, instance, method_name, *args, **kwargs):  # NOSONAR
        return None

    # ---- IApplication properties ----

    @property
    def isBooted(self):  # NOSONAR
        return False

    @property
    def startAt(self):  # NOSONAR
        return 0

    @property
    def routeHealthCheck(self):  # NOSONAR
        return "/up"

    @property
    def entryPoint(self):  # NOSONAR
        return None

    @property
    def basePath(self):  # NOSONAR
        return Path.cwd()

    @property
    def compiled(self):  # NOSONAR
        return False

    @property
    def compiledPath(self):  # NOSONAR
        return None

    @property
    def compiledInvalidationPathsDirs(self):  # NOSONAR
        return []

    @property
    def compiledInvalidationPathsFiles(self):  # NOSONAR
        return []

    # ---- IApplication abstract methods ----

    def on(self, lifespan, *callbacks, runtime=None):  # NOSONAR
        return self

    def withProviders(self, *providers):  # NOSONAR
        return self

    def withRouting(self, api=None, web=None, console=None, health=None):  # NOSONAR
        return self

    def withExceptionHandler(self, handler):  # NOSONAR
        return self

    async def getExceptionHandler(self):  # NOSONAR
        return None

    def withScheduler(self, scheduler):  # NOSONAR
        return self

    async def getScheduler(self):  # NOSONAR
        return None

    def withConfigApp(self, **app_config):  # NOSONAR
        return self

    def withConfigAuth(self, **auth_config):  # NOSONAR
        return self

    def withConfigCache(self, **cache_config):  # NOSONAR
        return self

    def withConfigCors(self, **cors_config):  # NOSONAR
        return self

    def withConfigDatabase(self, **database_config):  # NOSONAR
        return self

    def withConfigFilesystems(self, **filesystems_config):  # NOSONAR
        return self

    def withConfigLogging(self, **logging_config):  # NOSONAR
        return self

    def withConfigMail(self, **mail_config):  # NOSONAR
        return self

    def withConfigQueue(self, **queue_config):  # NOSONAR
        return self

    def withConfigSession(self, **session_config):  # NOSONAR
        return self

    def withConfigTesting(self, **testing_config):  # NOSONAR
        return self

    def withConfigPaths(self, **paths):  # NOSONAR
        return self

    def create(self):  # NOSONAR
        return self

    def config(self, key=None, value=_SENTINEL):  # NOSONAR
        return {}

    def resetRuntimeConfig(self):  # NOSONAR
        return True

    def path(self, key=None):  # NOSONAR
        return {}

    def routingPaths(self, key=None):  # NOSONAR
        return {}

    def isProduction(self):  # NOSONAR
        return False

    def isDebug(self):  # NOSONAR
        return False


# ===========================================================================
# Partial subclass — missing all IApplication-specific members.
# ===========================================================================

class _IncompleteApp(IApplication):
    """Intentionally incomplete — only satisfies IContainer, not IApplication."""

    def instance(self, abstract, instance, *, alias=None, override=False):  # NOSONAR
        return True

    def transient(self, abstract, concrete, *, alias=None, override=False):  # NOSONAR
        return True

    def singleton(self, abstract, concrete, *, alias=None, override=False):  # NOSONAR
        return True

    def scoped(self, abstract, concrete, *, alias=None, override=False):  # NOSONAR
        return True

    def bound(self, key):  # NOSONAR
        return False

    def beginScope(self):  # NOSONAR
        return None

    def getCurrentScope(self):  # NOSONAR
        return None

    async def make(self, key, *args, **kwargs):  # NOSONAR
        return None

    async def build(self, type_, *args, **kwargs):  # NOSONAR
        return None

    async def invoke(self, fn, *args, **kwargs):  # NOSONAR
        return None

    async def call(self, instance, method_name, *args, **kwargs):  # NOSONAR
        return None

# ===========================================================================
# TestIApplicationStructure
# ===========================================================================

class TestIApplicationStructure(TestCase):

    def testIsAbstractClass(self) -> None:
        """
        Test that IApplication is recognised as an abstract base class.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(inspect.isabstract(IApplication))

    def testCannotBeInstantiatedDirectly(self) -> None:
        """
        Test that instantiating IApplication directly raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            IApplication()  # type: ignore[abstract]

    def testInheritsFromIContainer(self) -> None:
        """
        Test that IApplication is a subclass of IContainer.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(IApplication, IContainer))

    def testSentinelObjectExists(self) -> None:
        """
        Test that the module-level _SENTINEL object is exported.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsNotNone(_SENTINEL)

    def testSentinelIsUniqueObject(self) -> None:
        """
        Test that _SENTINEL is not equal to common falsy or truthy values.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsNot(_SENTINEL, None)
        self.assertIsNot(_SENTINEL, False)
        self.assertIsNot(_SENTINEL, 0)

    def testAbstractMethodsCollectionIsNotEmpty(self) -> None:
        """
        Test that IApplication declares at least one abstract member.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(IApplication.__abstractmethods__), 0)

    def testIApplicationHasExpectedMemberCount(self) -> None:
        """
        Test that IApplication declares the expected number of abstract members.

        The interface defines 9 abstract properties and 26 abstract methods (35
        total), all of which must appear in ``__abstractmethods__``.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreaterEqual(len(IApplication.__abstractmethods__), 35)

    def testReflectionAbstractAcceptsIApplication(self) -> None:
        """
        Test that ReflectionAbstract can inspect IApplication without errors.

        Returns
        -------
        None
            This method does not return a value.
        """
        rf = ReflectionAbstract(IApplication)
        self.assertEqual(rf.getClassName(), "IApplication")

    def testGetModuleNameIsCorrect(self) -> None:
        """
        Test that the module name reported by reflection is correct.

        Returns
        -------
        None
            This method does not return a value.
        """
        rf = ReflectionAbstract(IApplication)
        self.assertIn("orionis", rf.getModuleName())

    def testGetBaseClassesContainsIContainer(self) -> None:
        """
        Test that ReflectionAbstract reports IContainer among the base classes.

        Returns
        -------
        None
            This method does not return a value.
        """
        rf = ReflectionAbstract(IApplication)
        base_names = [cls.__name__ for cls in rf.getBaseClasses()]
        self.assertIn("IContainer", base_names)

# ===========================================================================
# TestIApplicationAbstractProperties
# ===========================================================================

class TestIApplicationAbstractProperties(TestCase):

    def testIsBootedIsAbstract(self) -> None:
        """
        Test that the `isBooted` property is declared abstract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("isBooted", IApplication.__abstractmethods__)

    def testStartAtIsAbstract(self) -> None:
        """
        Test that the `startAt` property is declared abstract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("startAt", IApplication.__abstractmethods__)

    def testRouteHealthCheckIsAbstract(self) -> None:
        """
        Test that the `routeHealthCheck` property is declared abstract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("routeHealthCheck", IApplication.__abstractmethods__)

    def testEntryPointIsAbstract(self) -> None:
        """
        Test that the `entryPoint` property is declared abstract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("entryPoint", IApplication.__abstractmethods__)

    def testBasePathIsAbstract(self) -> None:
        """
        Test that the `basePath` property is declared abstract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("basePath", IApplication.__abstractmethods__)

    def testCompiledIsAbstract(self) -> None:
        """
        Test that the `compiled` property is declared abstract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("compiled", IApplication.__abstractmethods__)

    def testCompiledPathIsAbstract(self) -> None:
        """
        Test that the `compiledPath` property is declared abstract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("compiledPath", IApplication.__abstractmethods__)

    def testCompiledInvalidationPathsDirsIsAbstract(self) -> None:
        """
        Test that the `compiledInvalidationPathsDirs` property is declared abstract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("compiledInvalidationPathsDirs", IApplication.__abstractmethods__)

    def testCompiledInvalidationPathsFilesIsAbstract(self) -> None:
        """
        Test that the `compiledInvalidationPathsFiles` property is declared abstract.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("compiledInvalidationPathsFiles", IApplication.__abstractmethods__)

    def testPropertiesAreActualPropertyDescriptors(self) -> None:
        """
        Test that the abstract properties are implemented as property descriptors.

        Returns
        -------
        None
            This method does not return a value.
        """
        for prop_name in (
            "isBooted", "startAt", "routeHealthCheck", "entryPoint",
            "basePath", "compiled", "compiledPath",
            "compiledInvalidationPathsDirs", "compiledInvalidationPathsFiles",
        ):
            self.assertIsInstance(
                IApplication.__dict__[prop_name],
                property,
                msg=f"{prop_name} should be a property descriptor",
            )

# ===========================================================================
# TestIApplicationAbstractMethods
# ===========================================================================

class TestIApplicationAbstractMethods(TestCase):

    _EXPECTED_METHODS = (
        "on",
        "withProviders",
        "withRouting",
        "withExceptionHandler",
        "getExceptionHandler",
        "withScheduler",
        "getScheduler",
        "withConfigApp",
        "withConfigAuth",
        "withConfigCache",
        "withConfigCors",
        "withConfigDatabase",
        "withConfigFilesystems",
        "withConfigLogging",
        "withConfigMail",
        "withConfigQueue",
        "withConfigSession",
        "withConfigTesting",
        "withConfigPaths",
        "create",
        "config",
        "resetRuntimeConfig",
        "path",
        "routingPaths",
        "isProduction",
        "isDebug",
    )

    def testAllExpectedMethodsAreAbstract(self) -> None:
        """
        Test that every expected abstract method is registered in __abstractmethods__.

        Returns
        -------
        None
            This method does not return a value.
        """
        for method_name in self._EXPECTED_METHODS:
            self.assertIn(
                method_name,
                IApplication.__abstractmethods__,
                msg=f"Expected '{method_name}' to be abstract",
            )

    def testOnIsAbstract(self) -> None:
        """
        Test that `on` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("on", IApplication.__abstractmethods__)

    def testCreateIsAbstract(self) -> None:
        """
        Test that `create` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("create", IApplication.__abstractmethods__)

    def testConfigIsAbstract(self) -> None:
        """
        Test that `config` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("config", IApplication.__abstractmethods__)

    def testResetRuntimeConfigIsAbstract(self) -> None:
        """
        Test that `resetRuntimeConfig` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("resetRuntimeConfig", IApplication.__abstractmethods__)

    def testPathIsAbstract(self) -> None:
        """
        Test that `path` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("path", IApplication.__abstractmethods__)

    def testRoutingPathsIsAbstract(self) -> None:
        """
        Test that `routingPaths` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("routingPaths", IApplication.__abstractmethods__)

    def testIsProductionIsAbstract(self) -> None:
        """
        Test that `isProduction` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("isProduction", IApplication.__abstractmethods__)

    def testIsDebugIsAbstract(self) -> None:
        """
        Test that `isDebug` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("isDebug", IApplication.__abstractmethods__)

    def testGetExceptionHandlerIsAbstract(self) -> None:
        """
        Test that `getExceptionHandler` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("getExceptionHandler", IApplication.__abstractmethods__)

    def testGetSchedulerIsAbstract(self) -> None:
        """
        Test that `getScheduler` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("getScheduler", IApplication.__abstractmethods__)

    def testWithProvidersIsAbstract(self) -> None:
        """
        Test that `withProviders` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("withProviders", IApplication.__abstractmethods__)

    def testWithRoutingIsAbstract(self) -> None:
        """
        Test that `withRouting` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("withRouting", IApplication.__abstractmethods__)

    def testWithExceptionHandlerIsAbstract(self) -> None:
        """
        Test that `withExceptionHandler` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("withExceptionHandler", IApplication.__abstractmethods__)

    def testWithSchedulerIsAbstract(self) -> None:
        """
        Test that `withScheduler` is an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("withScheduler", IApplication.__abstractmethods__)

# ===========================================================================
# TestIApplicationMethodSignatures
# ===========================================================================

class TestIApplicationMethodSignatures(TestCase):

    def testOnSignatureAcceptsLifespanAndCallbacks(self) -> None:
        """
        Test that `on` declares `lifespan`, variadic `callbacks`, and `runtime`.

        Returns
        -------
        None
            This method does not return a value.
        """
        sig = inspect.signature(IApplication.on)
        params = list(sig.parameters)
        self.assertIn("lifespan", params)
        self.assertIn("runtime", params)

    def testConfigSignatureAcceptsKeyAndValue(self) -> None:
        """
        Test that `config` declares optional `key` and `value` parameters.

        Returns
        -------
        None
            This method does not return a value.
        """
        sig = inspect.signature(IApplication.config)
        params = sig.parameters
        self.assertIn("key", params)
        self.assertIn("value", params)

    def testConfigValueDefaultIsSentinel(self) -> None:
        """
        Test that the default value for `config`'s `value` parameter is _SENTINEL.

        Returns
        -------
        None
            This method does not return a value.
        """
        sig = inspect.signature(IApplication.config)
        default = sig.parameters["value"].default
        self.assertIs(default, _SENTINEL)

    def testPathSignatureAcceptsOptionalKey(self) -> None:
        """
        Test that `path` accepts an optional `key` parameter defaulting to None.

        Returns
        -------
        None
            This method does not return a value.
        """
        sig = inspect.signature(IApplication.path)
        params = sig.parameters
        self.assertIn("key", params)
        self.assertIsNone(params["key"].default)

    def testRoutingPathsSignatureAcceptsOptionalKey(self) -> None:
        """
        Test that `routingPaths` accepts an optional `key` parameter defaulting to None.

        Returns
        -------
        None
            This method does not return a value.
        """
        sig = inspect.signature(IApplication.routingPaths)
        params = sig.parameters
        self.assertIn("key", params)
        self.assertIsNone(params["key"].default)

    def testWithRoutingDefaultsAreNone(self) -> None:
        """
        Test that all `withRouting` parameters default to None.

        Returns
        -------
        None
            This method does not return a value.
        """
        sig = inspect.signature(IApplication.withRouting)
        for param_name in ("api", "web", "console", "health"):
            self.assertIn(param_name, sig.parameters)
            self.assertIsNone(
                sig.parameters[param_name].default,
                msg=f"'{param_name}' should default to None",
            )

    def testWithConfigMethodsAcceptKeywordArguments(self) -> None:
        """
        Test that each `withConfig*` method accepts variadic keyword arguments.

        Returns
        -------
        None
            This method does not return a value.
        """
        config_methods = (
            "withConfigApp", "withConfigAuth", "withConfigCache", "withConfigCors",
            "withConfigDatabase", "withConfigFilesystems", "withConfigLogging",
            "withConfigMail", "withConfigQueue", "withConfigSession",
            "withConfigTesting", "withConfigPaths",
        )
        for method_name in config_methods:
            method = getattr(IApplication, method_name)
            sig = inspect.signature(method)
            has_var_keyword = any(
                p.kind == inspect.Parameter.VAR_KEYWORD
                for p in sig.parameters.values()
            )
            self.assertTrue(
                has_var_keyword,
                msg=f"'{method_name}' should accept **kwargs",
            )

    def testGetExceptionHandlerIsCoroutineFunction(self) -> None:
        """
        Test that `getExceptionHandler` is declared as an async/coroutine function.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(
            inspect.iscoroutinefunction(IApplication.getExceptionHandler)
        )

    def testGetSchedulerIsCoroutineFunction(self) -> None:
        """
        Test that `getScheduler` is declared as an async/coroutine function.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(inspect.iscoroutinefunction(IApplication.getScheduler))

# ===========================================================================
# TestIApplicationContractEnforcement
# ===========================================================================

class TestIApplicationContractEnforcement(TestCase):

    def testIncompleteSubclassCannotBeInstantiated(self) -> None:
        """
        Test that a subclass missing IApplication-specific methods cannot be
        instantiated and raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            _IncompleteApp()  # type: ignore[abstract]

    def testFullConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Test that a complete IApplication implementation can be instantiated.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertIsInstance(app, IApplication)

    def testConcreteSubclassIsInstanceOfIContainer(self) -> None:
        """
        Test that a concrete IApplication subclass is also an IContainer instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertIsInstance(app, IContainer)

    def testConcreteSubclassIsBootedReturnsFalse(self) -> None:
        """
        Test that the concrete stub's `isBooted` property returns False.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertFalse(app.isBooted)

    def testConcreteSubclassStartAtReturnsInt(self) -> None:
        """
        Test that the concrete stub's `startAt` property returns an int.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertIsInstance(app.startAt, int)

    def testConcreteSubclassRouteHealthCheckReturnsStr(self) -> None:
        """
        Test that the concrete stub's `routeHealthCheck` property returns a str.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertIsInstance(app.routeHealthCheck, str)

    def testConcreteSubclassBasePathReturnsPath(self) -> None:
        """
        Test that the concrete stub's `basePath` property returns a Path instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertIsInstance(app.basePath, Path)

    def testConcreteSubclassCompiledReturnsBool(self) -> None:
        """
        Test that the concrete stub's `compiled` property returns a bool.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertIsInstance(app.compiled, bool)

    def testConcreteSubclassCompiledPathIsNone(self) -> None:
        """
        Test that the concrete stub's `compiledPath` property returns None.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertIsNone(app.compiledPath)

    def testConcreteSubclassCompiledDirsReturnsList(self) -> None:
        """
        Test that `compiledInvalidationPathsDirs` returns a list.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertIsInstance(app.compiledInvalidationPathsDirs, list)

    def testConcreteSubclassCompiledFilesReturnsList(self) -> None:
        """
        Test that `compiledInvalidationPathsFiles` returns a list.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        self.assertIsInstance(app.compiledInvalidationPathsFiles, list)

    def testConcreteSubclassOnReturnsSelf(self) -> None:
        """
        Test that `on()` on the concrete stub returns the app instance (Self).

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        result = app.on(Lifespan.STARTUP, lambda: None)
        self.assertIs(result, app)

    def testConcreteSubclassWithProvidersReturnsSelf(self) -> None:
        """
        Test that `withProviders()` on the concrete stub returns the app instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        result = app.withProviders()
        self.assertIs(result, app)

    def testConcreteSubclassCreateReturnsSelf(self) -> None:
        """
        Test that `create()` on the concrete stub returns the app instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        result = app.create()
        self.assertIs(result, app)

    def testConcreteSubclassConfigReturnsDict(self) -> None:
        """
        Test that `config()` on the concrete stub returns a dict.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        result = app.config()
        self.assertIsInstance(result, dict)

    def testConcreteSubclassResetRuntimeConfigReturnsTrue(self) -> None:
        """
        Test that `resetRuntimeConfig()` on the concrete stub returns True.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        result = app.resetRuntimeConfig()
        self.assertTrue(result)

    def testConcreteSubclassIsProductionReturnsBool(self) -> None:
        """
        Test that `isProduction()` on the concrete stub returns a bool.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        result = app.isProduction()
        self.assertIsInstance(result, bool)

    def testConcreteSubclassIsDebugReturnsBool(self) -> None:
        """
        Test that `isDebug()` on the concrete stub returns a bool.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FullConcreteApp()
        result = app.isDebug()
        self.assertIsInstance(result, bool)

# ===========================================================================
# TestIApplicationReflection
# ===========================================================================

class TestIApplicationReflection(TestCase):

    def _rf(self) -> ReflectionAbstract:
        """Return a fresh ReflectionAbstract instance for IApplication."""
        return ReflectionAbstract(IApplication)

    def testReflectionGetClassReturnsIApplication(self) -> None:
        """
        Test that `getClass()` returns the IApplication class object.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(self._rf().getClass(), IApplication)

    def testReflectionGetClassNameIsIApplication(self) -> None:
        """
        Test that `getClassName()` returns the string 'IApplication'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(self._rf().getClassName(), "IApplication")

    def testReflectionGetMethodsContainsOnMethod(self) -> None:
        """
        Test that `getMethods()` includes the 'on' method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("on", self._rf().getMethods())

    def testReflectionGetMethodsContainsCreate(self) -> None:
        """
        Test that `getMethods()` includes the 'create' method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("create", self._rf().getMethods())

    def testReflectionGetMethodsContainsConfig(self) -> None:
        """
        Test that `getMethods()` includes the 'config' method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("config", self._rf().getMethods())

    def testReflectionGetMethodsContainsIsProduction(self) -> None:
        """
        Test that `getMethods()` includes the 'isProduction' method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("isProduction", self._rf().getMethods())

    def testReflectionGetMethodsContainsIsDebug(self) -> None:
        """
        Test that `getMethods()` includes the 'isDebug' method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("isDebug", self._rf().getMethods())

    def testReflectionGetMethodsContainsAllExpectedMethods(self) -> None:
        """
        Test that `getMethods()` contains all 26 expected abstract method names.

        Returns
        -------
        None
            This method does not return a value.
        """
        methods = self._rf().getMethods()
        expected = (
            "on", "withProviders", "withRouting", "withExceptionHandler",
            "getExceptionHandler", "withScheduler", "getScheduler",
            "withConfigApp", "withConfigAuth", "withConfigCache",
            "withConfigCors", "withConfigDatabase", "withConfigFilesystems",
            "withConfigLogging", "withConfigMail", "withConfigQueue",
            "withConfigSession", "withConfigTesting", "withConfigPaths",
            "create", "config", "resetRuntimeConfig", "path",
            "routingPaths", "isProduction", "isDebug",
        )
        for name in expected:
            self.assertIn(name, methods, msg=f"Expected '{name}' in getMethods()")

    def testReflectionHasMethodReturnsTrueForCreate(self) -> None:
        """
        Test that `hasMethod('create')` returns True.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(self._rf().hasMethod("create"))

    def testReflectionHasMethodReturnsFalseForNonexistent(self) -> None:
        """
        Test that `hasMethod` returns False for a method not on the interface.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertFalse(self._rf().hasMethod("nonExistentMethod_xyz"))

    def testReflectionGetSourceCodeReturnsString(self) -> None:
        """
        Test that `getSourceCode()` returns a non-empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        source = self._rf().getSourceCode()
        self.assertIsInstance(source, str)
        self.assertGreater(len(source), 0)

    def testReflectionGetFileReturnsString(self) -> None:
        """
        Test that `getFile()` returns a string path to the source file.

        Returns
        -------
        None
            This method does not return a value.
        """
        file_path = self._rf().getFile()
        self.assertIsInstance(file_path, str)
        self.assertIn("application", file_path)
