from unittest.mock import AsyncMock, MagicMock, patch
from orionis.test import TestCase
from orionis.view.globals import (
    _makeApp,
    _makeConfig,
    _makeEnv,
    _makeRequest,
    _makeSession,
    buildViewGlobals,
)

class TestMakeConfig(TestCase):

    def testConfigCallableIsCallable(self) -> None:
        """
        Confirm the closure returned by _makeConfig is callable.

        Validates that the returned object can be invoked as a function
        inside a Jinja2 template context.
        """
        app = MagicMock()
        config = _makeConfig(app)
        self.assertTrue(callable(config))

    def testConfigReturnsAppConfigValue(self) -> None:
        """
        Retrieve a configuration value via the config callable.

        Validates that calling the returned closure delegates to
        app.config(key) and returns the resolved result.
        """
        app = MagicMock()
        app.config.return_value = "test-app"
        config = _makeConfig(app)
        result = config("app.name")
        self.assertEqual(result, "test-app")

    def testConfigReturnsDefaultOnException(self) -> None:
        """
        Return the default value when app.config raises an exception.

        Validates that any exception raised by the configuration lookup
        is swallowed and the caller-supplied default is returned.
        """
        app = MagicMock()
        app.config.side_effect = KeyError("missing")
        config = _makeConfig(app)
        result = config("missing.key", default="fallback")
        self.assertEqual(result, "fallback")

    def testConfigDefaultIsNoneWhenOmitted(self) -> None:
        """
        Return None when no default is specified and config lookup fails.

        Validates that the default argument is None when omitted and
        the config lookup raises an exception.
        """
        app = MagicMock()
        app.config.side_effect = RuntimeError("unavailable")
        config = _makeConfig(app)
        result = config("key.not.found")
        self.assertIsNone(result)

    def testConfigCallsAppConfigWithKey(self) -> None:
        """
        Forward the key argument to app.config unchanged.

        Validates that the closure calls app.config with exactly the key
        provided by the template, with no transformation.
        """
        app = MagicMock()
        app.config.return_value = "value"
        config = _makeConfig(app)
        config("database.host")
        app.config.assert_called_once_with("database.host")

class TestMakeEnv(TestCase):

    def testEnvCallableIsCallable(self) -> None:
        """
        Confirm the closure returned by _makeEnv is callable.

        Validates that the returned object can be invoked as a function
        inside a Jinja2 template context.
        """
        env_fn = _makeEnv()
        self.assertTrue(callable(env_fn))

    def testEnvForwardsKeyToEnvGet(self) -> None:
        """
        Forward the key argument to Env.get via the env callable.

        Validates that the env closure delegates to Env.get with the
        correct key so the right environment variable is retrieved.
        """
        with patch(
            "orionis.environment.env.Env.get", return_value="production",
        ) as mock_get:
            env_fn = _makeEnv()
            result = env_fn("APP_ENV")
            mock_get.assert_called_once_with("APP_ENV", None)
            self.assertEqual(result, "production")

    def testEnvForwardsDefaultArgument(self) -> None:
        """
        Forward both key and default arguments to Env.get.

        Validates that the closure passes the caller-supplied default
        through to Env.get without modification.
        """
        with patch(
            "orionis.environment.env.Env.get", return_value="development",
        ) as mock_get:
            env_fn = _makeEnv()
            result = env_fn("APP_ENV", "development")
            mock_get.assert_called_once_with("APP_ENV", "development")
            self.assertEqual(result, "development")

class TestMakeApp(TestCase):

    def testAppCallableIsCallable(self) -> None:
        """
        Confirm the closure returned by _makeApp is callable.

        Validates that the returned object can be invoked as a function
        inside a Jinja2 template context.
        """
        app = MagicMock()
        app_fn = _makeApp(app)
        self.assertTrue(callable(app_fn))

    def testAppCallableReturnsApplicationInstance(self) -> None:
        """
        Return the application instance from the app closure.

        Validates that invoking the closure always returns the same
        application reference that was passed to _makeApp.
        """
        app = MagicMock()
        app_fn = _makeApp(app)
        result = app_fn()
        self.assertIs(result, app)

    def testAppCallableReturnsSameInstanceOnMultipleCalls(self) -> None:
        """
        Return the same application instance on repeated invocations.

        Validates that the closure is a stable reference and does not
        create or return a different object on each call.
        """
        app = MagicMock()
        app_fn = _makeApp(app)
        self.assertIs(app_fn(), app_fn())

class TestMakeRequest(TestCase):

    async def testRequestCallableIsCallable(self) -> None:
        """
        Confirm the closure returned by _makeRequest is callable.

        Validates that the returned async callable can be awaited in a
        Jinja2 async template environment.
        """
        app = MagicMock()
        request_fn = _makeRequest(app)
        self.assertTrue(callable(request_fn))

    async def testRequestReturnsNoneWhenMakeRaises(self) -> None:
        """
        Return None when app.make raises an exception.

        Validates that the request closure swallows all exceptions and
        returns None when the request service cannot be resolved.
        """
        app = MagicMock()
        app.make = AsyncMock(side_effect=RuntimeError("no request scope"))
        request_fn = _makeRequest(app)
        result = await request_fn()
        self.assertIsNone(result)

    async def testRequestReturnsResolvedRequest(self) -> None:
        """
        Return the resolved request object from the app container.

        Validates that the closure returns whatever app.make produces
        when a request is in scope and resolution succeeds.
        """
        fake_request = MagicMock()
        app = MagicMock()
        app.make = AsyncMock(return_value=fake_request)
        request_fn = _makeRequest(app)
        result = await request_fn()
        self.assertIs(result, fake_request)

class TestMakeSession(TestCase):

    async def testSessionCallableIsCallable(self) -> None:
        """
        Confirm the closure returned by _makeSession is callable.

        Validates that the returned async callable can be awaited in a
        Jinja2 async template environment.
        """
        app = MagicMock()
        session_fn = _makeSession(app)
        self.assertTrue(callable(session_fn))

    async def testSessionReturnsNoneWhenMakeRaises(self) -> None:
        """
        Return None when app.make raises an exception.

        Validates that the session closure swallows all exceptions and
        returns None when the session service cannot be resolved.
        """
        app = MagicMock()
        app.make = AsyncMock(side_effect=RuntimeError("no session scope"))
        session_fn = _makeSession(app)
        result = await session_fn()
        self.assertIsNone(result)

    async def testSessionReturnsResolvedSession(self) -> None:
        """
        Return the resolved session object from the app container.

        Validates that the closure returns whatever app.make produces
        when a session is in scope and resolution succeeds.
        """
        fake_session = MagicMock()
        app = MagicMock()
        app.make = AsyncMock(return_value=fake_session)
        session_fn = _makeSession(app)
        result = await session_fn()
        self.assertIs(result, fake_session)

class TestBuildViewGlobals(TestCase):

    def testReturnsDict(self) -> None:
        """
        Verify buildViewGlobals returns a dictionary.

        Validates that the return type is a plain dict mapping global
        names to their callable implementations.
        """
        app = MagicMock()
        result = buildViewGlobals(app)
        self.assertIsInstance(result, dict)

    def testContainsAllExpectedKeys(self) -> None:
        """
        Verify buildViewGlobals contains all expected template global keys.

        Validates that every documented global name is present in the
        returned mapping so templates can access them.
        """
        app = MagicMock()
        result = buildViewGlobals(app)
        expected = {"config", "env", "app", "request", "session"}
        self.assertEqual(set(result.keys()), expected)

    def testAllValuesAreCallable(self) -> None:
        """
        Verify every value in the globals dict is callable.

        Validates that Jinja2 can invoke each global as a function
        during template rendering without a TypeError.
        """
        app = MagicMock()
        result = buildViewGlobals(app)
        for name, value in result.items():
            self.assertTrue(callable(value), msg=f"'{name}' is not callable")

    def testExactlyFiveGlobalsRegistered(self) -> None:
        """
        Verify exactly five globals are registered by default.

        Validates the expected global count so new globals are noticed
        when added without updating the test suite.
        """
        app = MagicMock()
        result = buildViewGlobals(app)
        self.assertEqual(len(result), 5)
