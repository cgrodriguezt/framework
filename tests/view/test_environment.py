import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import jinja2
from orionis.test import TestCase
from orionis.view.environment import ViewEnvironment
from orionis.view.exceptions import ViewException

class TestViewEnvironment(TestCase):

    def setUp(self) -> None:
        """
        Create an isolated temporary directory before each test.

        Provides a fresh, writable directory used as the template search
        path so every test operates on its own filesystem state.
        """
        self._tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        """
        Remove the temporary directory after each test.

        Ensures all files created during the test are cleaned up
        regardless of whether the test passed or failed.
        """
        self._tmpdir.cleanup()

    def _buildApp(
        self,
        *,
        paths: list | None = None,
        cache_path_str: str | None = None,
    ) -> MagicMock:
        """
        Build a mock IApplication configured for the view environment.

        Parameters
        ----------
        paths : list or None
            Template search paths. Defaults to the temporary directory.
        cache_path_str : str or None
            Optional bytecode cache path string.

        Returns
        -------
        MagicMock
            A mock application whose config and basePath are set up.
        """
        resolved_paths = paths if paths is not None else [self._tmpdir.name]
        app = MagicMock()
        app.config.return_value = {
            "paths": resolved_paths,
            "cache_size": 100,
            "cache_path": cache_path_str,
            "auto_reload": False,
            "autoescape": True,
            "enable_async": True,
        }
        app.basePath = Path(self._tmpdir.name)
        return app

    def _buildEnv(
        self,
        *,
        paths: list | None = None,
        cache_path_str: str | None = None,
    ) -> ViewEnvironment:
        """
        Build a ViewEnvironment backed by a mocked application.

        Parameters
        ----------
        paths : list or None
            Template search paths passed to _buildApp.
        cache_path_str : str or None
            Optional bytecode cache path string passed to _buildApp.

        Returns
        -------
        ViewEnvironment
            A freshly constructed environment instance.
        """
        return ViewEnvironment(
            self._buildApp(paths=paths, cache_path_str=cache_path_str),
        )

    def testConstructionSucceeds(self) -> None:
        """
        Construct ViewEnvironment without raising any exception.

        Validates that a correctly configured application mock produces
        a valid ViewEnvironment instance.
        """
        env = self._buildEnv()
        self.assertIsInstance(env, ViewEnvironment)

    def testGetJinjaEnvironmentReturnsJinjaEnvironment(self) -> None:
        """
        Return a jinja2.Environment from getJinjaEnvironment.

        Validates that the internal Jinja2 environment is correctly
        built and accessible through the public accessor.
        """
        env = self._buildEnv()
        jinja_env = env.getJinjaEnvironment()
        self.assertIsInstance(jinja_env, jinja2.Environment)

    def testSinglePathUsesFileSystemLoader(self) -> None:
        """
        Use a FileSystemLoader when a single template path is configured.

        Validates that the Jinja2 environment loader is a FileSystemLoader
        when only one search path is provided.
        """
        env = self._buildEnv(paths=[self._tmpdir.name])
        jinja_env = env.getJinjaEnvironment()
        self.assertIsInstance(jinja_env.loader, jinja2.FileSystemLoader)

    def testMultiplePathsUsesChoiceLoader(self) -> None:
        """
        Use a ChoiceLoader when multiple template paths are configured.

        Validates that the Jinja2 environment loader is a ChoiceLoader
        when two or more search paths are provided.
        """
        dir1 = Path(self._tmpdir.name) / "views1"
        dir2 = Path(self._tmpdir.name) / "views2"
        dir1.mkdir()
        dir2.mkdir()
        env = self._buildEnv(paths=[str(dir1), str(dir2)])
        jinja_env = env.getJinjaEnvironment()
        self.assertIsInstance(jinja_env.loader, jinja2.ChoiceLoader)

    def testAsyncIsEnabled(self) -> None:
        """
        Confirm the Jinja2 environment is built with async enabled.

        Validates that the enable_async flag is True on the environment
        so render_async can be called on every template.
        """
        env = self._buildEnv()
        jinja_env = env.getJinjaEnvironment()
        self.assertTrue(jinja_env.is_async)

    def testAddGlobalRegistersValueInJinjaGlobals(self) -> None:
        """
        Register a global value in the Jinja2 environment globals dict.

        Validates that addGlobal makes the value accessible by name
        in the underlying Jinja2 environment globals mapping.
        """
        env = self._buildEnv()
        jinja_env = env.getJinjaEnvironment()
        env.addGlobal("site_name", "Orionis")
        self.assertEqual(jinja_env.globals["site_name"], "Orionis")

    def testAddGlobalOverwritesPreviousValue(self) -> None:
        """
        Overwrite an existing global when the same name is re-registered.

        Validates that calling addGlobal twice with the same name updates
        the value rather than raising an error.
        """
        env = self._buildEnv()
        jinja_env = env.getJinjaEnvironment()
        env.addGlobal("counter", 1)
        env.addGlobal("counter", 99)
        self.assertEqual(jinja_env.globals["counter"], 99)

    def testAddFilterRegistersCallableInFilters(self) -> None:
        """
        Register a filter callable in the Jinja2 environment filters dict.

        Validates that addFilter makes the callable accessible by name
        in the underlying Jinja2 environment filters mapping.
        """
        env = self._buildEnv()
        jinja_env = env.getJinjaEnvironment()
        my_filter = str.upper
        env.addFilter("shout", my_filter)
        self.assertIs(jinja_env.filters["shout"], my_filter)

    def testAddTestRegistersCallableInTests(self) -> None:
        """
        Register a test callable in the Jinja2 environment tests dict.

        Validates that addTest makes the callable accessible by name
        in the underlying Jinja2 environment tests mapping.
        """
        env = self._buildEnv()
        jinja_env = env.getJinjaEnvironment()

        def is_positive(value: int) -> bool:
            return value > 0

        env.addTest("positive", is_positive)
        self.assertIs(jinja_env.tests["positive"], is_positive)

    def testAddExtensionRaisesViewExceptionForInvalidExtension(self) -> None:
        """
        Raise ViewException when an invalid extension is registered.

        Validates that addExtension wraps Jinja2 import or type errors
        as ViewException to maintain a consistent exception hierarchy.
        """
        env = self._buildEnv()
        invalid_ext = "invalid.module.that.does.not.exist.Extension"
        with self.assertRaises(ViewException):
            env.addExtension(invalid_ext)

    def testConstructionWithCachePathCreatesDirectory(self) -> None:
        """
        Create the bytecode cache directory when cache_path is configured.

        Validates that ViewEnvironment creates the cache directory during
        construction so OrionisBytecodeCache can write files immediately.
        """
        cache_path = Path(self._tmpdir.name) / "jinja_cache"
        env = self._buildEnv(cache_path_str=str(cache_path))
        jinja_env = env.getJinjaEnvironment()
        self.assertTrue(cache_path.exists())
        self.assertIsNotNone(jinja_env.bytecode_cache)

    def testConstructionWithoutCachePathHasNoBytecodeCache(self) -> None:
        """
        Leave the Jinja2 bytecode_cache as None when no cache path is set.

        Validates that the bytecode cache is only activated when a
        cache_path is explicitly provided in the view configuration.
        """
        env = self._buildEnv(cache_path_str=None)
        jinja_env = env.getJinjaEnvironment()
        self.assertIsNone(jinja_env.bytecode_cache)

    def testGetJinjaEnvironmentReturnsSameInstance(self) -> None:
        """
        Return the same Jinja2 environment instance on repeated calls.

        Validates that getJinjaEnvironment is idempotent and does not
        create a new environment object on each invocation.
        """
        env = self._buildEnv()
        self.assertIs(env.getJinjaEnvironment(), env.getJinjaEnvironment())
