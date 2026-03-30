from pathlib import Path
from orionis.console.base.contracts.scheduler import IBaseScheduler
from orionis.container.container import Container
from orionis.container.context.scope import ScopedContext
from orionis.container.providers.service_provider import ServiceProvider
from orionis.failure.contracts.handler import IBaseExceptionHandler
from orionis.foundation.application import Application
from orionis.foundation.enums.lifespan import Lifespan
from orionis.foundation.enums.runtimes import Runtime
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Framework root — used as base_path for every Application under test
# ---------------------------------------------------------------------------

BASE_PATH = Path(__file__).parents[2]

# ---------------------------------------------------------------------------
# Minimal concrete stubs required by some tests
# ---------------------------------------------------------------------------

class _ConcreteProvider(ServiceProvider):
    """Minimal ServiceProvider subclass for registration tests."""

    def register(self) -> None: # NOSONAR
        pass

class _ConcreteExceptionHandler(IBaseExceptionHandler):
    """Minimal IBaseExceptionHandler subclass for registration tests."""

    async def toThrowable(self, exception: Exception): # NOSONAR
        pass

    async def isExceptionIgnored(self, exception: Exception) -> bool: # NOSONAR
        return False

    async def report(self, exception: Exception, log): # NOSONAR
        pass

    async def handleCLI(self, exception: Exception, console) -> None: # NOSONAR
        pass

    async def render(self, exception: Exception, console) -> None: # NOSONAR
        pass

class _ConcreteScheduler(IBaseScheduler):
    """Minimal IBaseScheduler subclass for registration tests."""

    async def tasks(self, schedule) -> None: # NOSONAR
        pass

    async def onStarted(self, event) -> None: # NOSONAR
        pass

    async def onPaused(self, event) -> None: # NOSONAR
        pass

    async def onResumed(self, event) -> None: # NOSONAR
        pass

    async def onShutdown(self, event) -> None: # NOSONAR
        pass


# ---------------------------------------------------------------------------
# Base class that guarantees a fresh Application instance per test
# ---------------------------------------------------------------------------

class _AppTestBase(TestCase):
    """Reset the class-level Container singleton before every test method."""

    def setUp(self) -> None:
        Container._instances.pop(Application, None)

    def _createApp(self) -> Application:
        """
        Return a freshly created and booted Application.

        The reactor test runner wraps every test inside a scope context which
        prevents registering container aliases.  This helper temporarily clears
        the active scope, boots a new Application, then restores the previous
        scope so the rest of the framework continues working normally.

        Returns
        -------
        Application
            A new, booted Application instance.
        """
        token = ScopedContext.setCurrentScope(None)
        try:
            app = Application(base_path=BASE_PATH)
            app.create()
            return app
        finally:
            ScopedContext.reset(token)

    def _createAppWithRouting(self) -> Application:
        """
        Return a freshly created, booted Application with routing initialized.

        Calls `withRouting()` before `create()` so that routing keys ('api',
        'web', 'console') exist in the bootstrap config and return lists.

        Returns
        -------
        Application
            A new, booted Application instance with empty routing lists.
        """
        token = ScopedContext.setCurrentScope(None)
        try:
            app = Application(base_path=BASE_PATH)
            app.withRouting()
            app.create()
            return app
        finally:
            ScopedContext.reset(token)


# ===========================================================================
# Instantiation & default properties
# ===========================================================================

class TestApplicationInstantiation(_AppTestBase):

    def testIsBootedIsFalseAfterConstruction(self) -> None:
        """
        Test that `isBooted` is False immediately after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertFalse(app.isBooted)

    def testStartAtIsInteger(self) -> None:
        """
        Test that `startAt` returns an integer nanosecond timestamp.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertIsInstance(app.startAt, int)

    def testStartAtIsPositive(self) -> None:
        """
        Test that `startAt` is a positive nanosecond value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertGreater(app.startAt, 0)

    def testBasePathIsPathInstance(self) -> None:
        """
        Test that `basePath` returns a Path instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertIsInstance(app.basePath, Path)

    def testBasePathMatchesConstructorArgument(self) -> None:
        """
        Test that `basePath` matches the resolved constructor argument.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertEqual(app.basePath, BASE_PATH.resolve())

    def testCompiledIsFalseByDefault(self) -> None:
        """
        Test that `compiled` is False when compilation is not enabled.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertFalse(app.compiled)

    def testCompiledPathIsNoneByDefault(self) -> None:
        """
        Test that `compiledPath` is None when compilation is not enabled.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertIsNone(app.compiledPath)

    def testCompiledInvalidationPathsDirsIsEmptyByDefault(self) -> None:
        """
        Test that `compiledInvalidationPathsDirs` is an empty list by default.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertEqual(app.compiledInvalidationPathsDirs, [])

    def testCompiledInvalidationPathsFilesIsEmptyByDefault(self) -> None:
        """
        Test that `compiledInvalidationPathsFiles` is an empty list by default.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertEqual(app.compiledInvalidationPathsFiles, [])

    def testRouteHealthCheckDefaultsToSlashUp(self) -> None:
        """
        Test that `routeHealthCheck` defaults to '/up' before any routing config.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertEqual(app.routeHealthCheck, "/up")

    def testEntryPointIsNoneBeforeCreate(self) -> None:
        """
        Test that `entryPoint` is None before `create()` is invoked.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertIsNone(app.entryPoint)

    def testCompiledInvalidationPathsDirsIsListType(self) -> None:
        """
        Test that `compiledInvalidationPathsDirs` is a list.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertIsInstance(app.compiledInvalidationPathsDirs, list)

    def testCompiledInvalidationPathsFilesIsListType(self) -> None:
        """
        Test that `compiledInvalidationPathsFiles` is a list.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        self.assertIsInstance(app.compiledInvalidationPathsFiles, list)

# ===========================================================================
# on() — lifecycle callback registration
# ===========================================================================

class TestApplicationOnMethod(_AppTestBase):

    def testOnWithValidLifespanReturnsSelf(self) -> None:
        """
        Test that `on()` returns the Application instance for method chaining.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.on(Lifespan.STARTUP, lambda: None)
        self.assertIs(result, app)

    def testOnWithInvalidLifespanRaisesTypeError(self) -> None:
        """
        Test that `on()` raises TypeError when lifespan is not a Lifespan member.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(TypeError):
            app.on("startup", lambda: None)

    def testOnWithNoCallbacksRaisesValueError(self) -> None:
        """
        Test that `on()` raises ValueError when no callbacks are supplied.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(ValueError):
            app.on(Lifespan.STARTUP)

    def testOnWithNonCallableRaisesTypeError(self) -> None:
        """
        Test that `on()` raises TypeError when a callback is not callable.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(TypeError):
            app.on(Lifespan.STARTUP, "not_a_callable")

    def testOnWithShutdownLifespanReturnsSelf(self) -> None:
        """
        Test that `on()` works correctly with Lifespan.SHUTDOWN.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.on(Lifespan.SHUTDOWN, lambda: None)
        self.assertIs(result, app)

    def testOnWithRuntimeParameterReturnsSelf(self) -> None:
        """
        Test that `on()` accepts an optional runtime parameter.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.on(Lifespan.STARTUP, lambda: None, runtime=Runtime.HTTP)
        self.assertIs(result, app)

    def testOnWithCliRuntimeReturnsSelf(self) -> None:
        """
        Test that `on()` accepts Runtime.CLI as runtime parameter.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.on(Lifespan.STARTUP, lambda: None, runtime=Runtime.CLI)
        self.assertIs(result, app)

    def testOnChaining(self) -> None:
        """
        Test that multiple `on()` calls can be chained on the same instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = (
            app
            .on(Lifespan.STARTUP, lambda: None)
            .on(Lifespan.SHUTDOWN, lambda: None)
        )
        self.assertIs(result, app)

    def testOnWithMultipleCallbacksReturnsSelf(self) -> None:
        """
        Test that `on()` accepts multiple callbacks in a single call.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.on(Lifespan.STARTUP, lambda: None, lambda: None)
        self.assertIs(result, app)

    def testOnWithIntegerLifespanRaisesTypeError(self) -> None:
        """
        Test that `on()` raises TypeError when lifespan is an integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(TypeError):
            app.on(1, lambda: None)

# ===========================================================================
# withProviders()
# ===========================================================================

class TestApplicationWithProviders(_AppTestBase):

    def testWithProvidersWithNonClassRaisesTypeError(self) -> None:
        """
        Test that `withProviders()` raises TypeError for a non-class argument.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(TypeError):
            app.withProviders("not_a_class")

    def testWithProvidersWithNonProviderClassRaisesTypeError(self) -> None:
        """
        Test that `withProviders()` raises TypeError for a non-IServiceProvider subclass.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(TypeError):
            app.withProviders(int)

    def testWithProvidersWithValidProviderReturnsSelf(self) -> None:
        """
        Test that `withProviders()` returns the Application instance for chaining.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withProviders(_ConcreteProvider)
        self.assertIs(result, app)

    def testWithProvidersChaining(self) -> None:
        """
        Test that multiple `withProviders()` calls chain correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withProviders(_ConcreteProvider).withProviders(_ConcreteProvider)
        self.assertIs(result, app)

# ===========================================================================
# withExceptionHandler()
# ===========================================================================

class TestApplicationWithExceptionHandler(_AppTestBase):

    def testWithExceptionHandlerWithNonClassRaisesTypeError(self) -> None:
        """
        Test that `withExceptionHandler()` raises TypeError for a non-class argument.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(TypeError):
            app.withExceptionHandler("not_a_class")

    def testWithExceptionHandlerWithNonHandlerClassRaisesTypeError(self) -> None:
        """
        Test that `withExceptionHandler()` raises TypeError for a non-handler class.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(TypeError):
            app.withExceptionHandler(int)

    def testWithExceptionHandlerWithValidHandlerReturnsSelf(self) -> None:
        """
        Test that `withExceptionHandler()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withExceptionHandler(_ConcreteExceptionHandler)
        self.assertIs(result, app)

# ===========================================================================
# withScheduler()
# ===========================================================================

class TestApplicationWithScheduler(_AppTestBase):

    def testWithSchedulerWithNonSchedulerClassRaisesTypeError(self) -> None:
        """
        Test that `withScheduler()` raises TypeError for a non-IBaseScheduler subclass.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(TypeError):
            app.withScheduler(int)

    def testWithSchedulerWithValidSchedulerReturnsSelf(self) -> None:
        """
        Test that `withScheduler()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withScheduler(_ConcreteScheduler)
        self.assertIs(result, app)

# ===========================================================================
# withConfig*() — configuration setup methods
# ===========================================================================

class TestApplicationWithConfig(_AppTestBase):

    def testWithConfigAppReturnsSelf(self) -> None:
        """
        Test that `withConfigApp()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigApp(name="Test App")
        self.assertIs(result, app)

    def testWithConfigAuthReturnsSelf(self) -> None:
        """
        Test that `withConfigAuth()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigAuth(driver="session")
        self.assertIs(result, app)

    def testWithConfigCacheReturnsSelf(self) -> None:
        """
        Test that `withConfigCache()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigCache(default="file")
        self.assertIs(result, app)

    def testWithConfigCorsReturnsSelf(self) -> None:
        """
        Test that `withConfigCors()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigCors(allowed_origins=["*"])
        self.assertIs(result, app)

    def testWithConfigDatabaseReturnsSelf(self) -> None:
        """
        Test that `withConfigDatabase()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigDatabase(default="sqlite")
        self.assertIs(result, app)

    def testWithConfigFilesystemsReturnsSelf(self) -> None:
        """
        Test that `withConfigFilesystems()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigFilesystems(default="local")
        self.assertIs(result, app)

    def testWithConfigLoggingReturnsSelf(self) -> None:
        """
        Test that `withConfigLogging()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigLogging(channel="stack")
        self.assertIs(result, app)

    def testWithConfigMailReturnsSelf(self) -> None:
        """
        Test that `withConfigMail()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigMail(driver="smtp")
        self.assertIs(result, app)

    def testWithConfigQueueReturnsSelf(self) -> None:
        """
        Test that `withConfigQueue()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigQueue(default="sync")
        self.assertIs(result, app)

    def testWithConfigSessionReturnsSelf(self) -> None:
        """
        Test that `withConfigSession()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigSession(driver="file")
        self.assertIs(result, app)

    def testWithConfigTestingReturnsSelf(self) -> None:
        """
        Test that `withConfigTesting()` returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigTesting(enabled=True)
        self.assertIs(result, app)

    def testWithConfigPathsReturnsSelf(self) -> None:
        """
        Test that `withConfigPaths()` (no arguments) returns the Application instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = app.withConfigPaths()
        self.assertIs(result, app)

    def testMultipleConfigMethodsChain(self) -> None:
        """
        Test that multiple `withConfig*` calls can be chained on one instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        result = (
            app
            .withConfigApp(name="TestApp")
            .withConfigCache(default="file")
            .withConfigLogging(channel="stack")
        )
        self.assertIs(result, app)

# ===========================================================================
# create() — boostrap and boot behaviour
# ===========================================================================

class TestApplicationCreate(_AppTestBase):

    def testCreateSetsIsBootedTrue(self) -> None:
        """
        Test that `create()` sets `isBooted` to True.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        self.assertTrue(app.isBooted)

    def testCreateReturnsSelf(self) -> None:
        """
        Test that `create()` returns the Application instance for chaining.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        self.assertIs(app, app)

    def testCreateIsIdempotent(self) -> None:
        """
        Test that calling `create()` twice on the same instance is safe.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.create()
        self.assertIs(result, app)
        self.assertTrue(app.isBooted)

    def testWithProvidersAfterBootRaisesRuntimeError(self) -> None:
        """
        Test that `withProviders()` raises RuntimeError after `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        with self.assertRaises(RuntimeError):
            app.withProviders(_ConcreteProvider)

    def testWithExceptionHandlerAfterBootRaisesRuntimeError(self) -> None:
        """
        Test that `withExceptionHandler()` raises RuntimeError after `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        with self.assertRaises(RuntimeError):
            app.withExceptionHandler(_ConcreteExceptionHandler)

    def testWithSchedulerAfterBootRaisesRuntimeError(self) -> None:
        """
        Test that `withScheduler()` raises RuntimeError after `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        with self.assertRaises(RuntimeError):
            app.withScheduler(_ConcreteScheduler)

    def testWithConfigAppAfterBootRaisesRuntimeError(self) -> None:
        """
        Test that `withConfigApp()` raises RuntimeError after `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        with self.assertRaises(RuntimeError):
            app.withConfigApp(name="Too Late")

    def testWithConfigPathsAfterBootRaisesRuntimeError(self) -> None:
        """
        Test that `withConfigPaths()` raises RuntimeError after `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        with self.assertRaises(RuntimeError):
            app.withConfigPaths()

    def testEntryPointIsSetAfterCreate(self) -> None:
        """
        Test that `entryPoint` is set to a non-None string after `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        self.assertIsNotNone(app.entryPoint)

    def testEntryPointEndsWithApp(self) -> None:
        """
        Test that `entryPoint` ends with ':app' suffix.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        self.assertTrue(app.entryPoint.endswith(":app"))

# ===========================================================================
# config() — runtime configuration access
# ===========================================================================

class TestApplicationConfig(_AppTestBase):

    def testConfigRaisesRuntimeErrorBeforeCreate(self) -> None:
        """
        Test that `config()` raises RuntimeError when called before `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(RuntimeError):
            app.config()

    def testConfigReturnsDictForNoKey(self) -> None:
        """
        Test that `config()` returns the full config dict when no key is given.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.config()
        self.assertIsInstance(result, dict)

    def testConfigGetAppEnvReturnsString(self) -> None:
        """
        Test that `config('app.env')` returns a string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.config("app.env")
        self.assertIsInstance(result, str)

    def testConfigSetAndGet(self) -> None:
        """
        Test that `config(key, value)` stores and `config(key)` retrieves it.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        app.config("app.name", "UnitTestApp")
        self.assertEqual(app.config("app.name"), "UnitTestApp")

    def testConfigGetNonExistentKeyReturnsNone(self) -> None:
        """
        Test that `config()` returns None for an unknown dot-notation key.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.config("nonexistent.deep.key")
        self.assertIsNone(result)

    def testConfigSetNestedKey(self) -> None:
        """
        Test that `config()` can create nested keys on demand.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        app.config("custom.section.value", 42)
        self.assertEqual(app.config("custom.section.value"), 42)

    def testResetRuntimeConfigReturnsTrue(self) -> None:
        """
        Test that `resetRuntimeConfig()` returns True.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.resetRuntimeConfig()
        self.assertTrue(result)

    def testResetRuntimeConfigRestoresOriginalValues(self) -> None:
        """
        Test that `resetRuntimeConfig()` reverts any in-memory config changes.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        original = app.config("app.name")
        app.config("app.name", "TemporarlyChanged")
        app.resetRuntimeConfig()
        self.assertEqual(app.config("app.name"), original)

# ===========================================================================
# path() — application path resolution
# ===========================================================================

class TestApplicationPath(_AppTestBase):

    def testPathRaisesRuntimeErrorBeforeCreate(self) -> None:
        """
        Test that `path()` raises RuntimeError when called before `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(RuntimeError):
            app.path()

    def testPathReturnsDictForNoKey(self) -> None:
        """
        Test that `path()` returns all paths as a dict when no key is provided.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.path()
        self.assertIsInstance(result, dict)

    def testPathRootKeyReturnsPath(self) -> None:
        """
        Test that `path('root')` returns a Path object.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.path("root")
        self.assertIsInstance(result, Path)

    def testPathAppKeyReturnsPath(self) -> None:
        """
        Test that `path('app')` returns a Path object.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.path("app")
        self.assertIsInstance(result, Path)

    def testPathNonexistentKeyReturnsNone(self) -> None:
        """
        Test that `path('no_such_key')` returns None.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.path("no_such_key")
        self.assertIsNone(result)

    def testPathRaisesTypeErrorForNonStringKey(self) -> None:
        """
        Test that `path()` raises TypeError when argument is not a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        with self.assertRaises(TypeError):
            app.path(99)

# ===========================================================================
# routingPaths() — routing configuration access
# ===========================================================================

class TestApplicationRoutingPaths(_AppTestBase):

    def testRoutingPathsRaisesRuntimeErrorBeforeCreate(self) -> None:
        """
        Test that `routingPaths()` raises RuntimeError before `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(RuntimeError):
            app.routingPaths()

    def testRoutingPathsReturnsDictForNoKey(self) -> None:
        """
        Test that `routingPaths()` returns a dict when no key is provided.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.routingPaths()
        self.assertIsInstance(result, dict)

    def testRoutingPathsApiKeyReturnsList(self) -> None:
        """
        Test that `routingPaths('api')` returns a list.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createAppWithRouting()
        result = app.routingPaths("api")
        self.assertIsInstance(result, list)

    def testRoutingPathsWebKeyReturnsList(self) -> None:
        """
        Test that `routingPaths('web')` returns a list.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createAppWithRouting()
        result = app.routingPaths("web")
        self.assertIsInstance(result, list)

    def testRoutingPathsInvalidKeyReturnsNone(self) -> None:
        """
        Test that `routingPaths()` returns None for unknown routing keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.routingPaths("nonexistent_route_key")
        self.assertIsNone(result)

    def testRoutingPathsRaisesTypeErrorForNonStringKey(self) -> None:
        """
        Test that `routingPaths()` raises TypeError for a non-string key.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        with self.assertRaises(TypeError):
            app.routingPaths(42)

# ===========================================================================
# isProduction() / isDebug() — environment checks
# ===========================================================================

class TestApplicationEnvironmentChecks(_AppTestBase):

    def testIsProductionReturnsBool(self) -> None:
        """
        Test that `isProduction()` returns a boolean value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.isProduction()
        self.assertIsInstance(result, bool)

    def testIsDebugReturnsBool(self) -> None:
        """
        Test that `isDebug()` returns a boolean value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        result = app.isDebug()
        self.assertIsInstance(result, bool)

    def testIsProductionRaisesRuntimeErrorBeforeCreate(self) -> None:
        """
        Test that `isProduction()` raises RuntimeError before `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(RuntimeError):
            app.isProduction()

    def testIsDebugRaisesRuntimeErrorBeforeCreate(self) -> None:
        """
        Test that `isDebug()` raises RuntimeError before `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(RuntimeError):
            app.isDebug()

    def testIsProductionFalseWhenEnvIsLocal(self) -> None:
        """
        Test that `isProduction()` returns False when app.env does not contain 'prod'.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        app.config("app.env", "local")
        self.assertFalse(app.isProduction())

    def testIsProductionTrueWhenEnvIsProduction(self) -> None:
        """
        Test that `isProduction()` returns True when app.env contains 'prod'.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        app.config("app.env", "production")
        self.assertTrue(app.isProduction())

    def testIsDebugTrueWhenDebugEnabled(self) -> None:
        """
        Test that `isDebug()` returns True when app.debug is explicitly True.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        app.config("app.debug", True)
        self.assertTrue(app.isDebug())

    def testIsDebugFalseWhenDebugDisabled(self) -> None:
        """
        Test that `isDebug()` returns False when app.debug is False.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = self._createApp()
        app.config("app.debug", False)
        self.assertFalse(app.isDebug())

# ===========================================================================
# getExceptionHandler() / getScheduler() — async pre-boot guards
# ===========================================================================

class TestApplicationAsyncGetters(_AppTestBase):

    async def testGetExceptionHandlerRaisesRuntimeErrorBeforeBoot(self) -> None:
        """
        Test that `getExceptionHandler()` raises RuntimeError before `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(RuntimeError):
            await app.getExceptionHandler()

    async def testGetSchedulerRaisesRuntimeErrorBeforeBoot(self) -> None:
        """
        Test that `getScheduler()` raises RuntimeError before `create()`.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = Application(base_path=BASE_PATH)
        with self.assertRaises(RuntimeError):
            await app.getScheduler()
