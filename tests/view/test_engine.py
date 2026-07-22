from unittest.mock import AsyncMock, MagicMock
import jinja2
from orionis.test import TestCase
from orionis.view.engine import Jinja2Engine
from orionis.view.exceptions import ViewRenderException, ViewTemplateNotFoundException

class TestJinja2EngineNormalisePath(TestCase):

    def testDotNotationConvertsToSlashPath(self) -> None:
        """
        Convert dot-notation template names to slash-delimited paths.

        Validates that dots are replaced with forward slashes and the
        .html extension is appended when absent.
        """
        result = Jinja2Engine._normalisePath("users.index")
        self.assertEqual(result, "users/index.html")

    def testDirectPathWithExtensionIsUnchanged(self) -> None:
        """
        Return a direct path with extension unchanged.

        Validates that a path containing a forward slash and an existing
        extension is not modified by the normalisation step.
        """
        result = Jinja2Engine._normalisePath("users/index.html")
        self.assertEqual(result, "users/index.html")

    def testDirectPathWithoutExtensionGetsHtmlSuffix(self) -> None:
        """
        Append .html to a direct path that has no extension.

        Validates that when a slash is present but no extension exists
        in the last segment, the default .html suffix is added.
        """
        result = Jinja2Engine._normalisePath("users/index")
        self.assertEqual(result, "users/index.html")

    def testSingleWordGetsHtmlSuffix(self) -> None:
        """
        Append .html to a single-word template identifier.

        Validates that a bare word without slash or dot produces a
        .html filename in the normalised output.
        """
        result = Jinja2Engine._normalisePath("nav")
        self.assertEqual(result, "nav.html")

    def testDeepDotNotationConvertsToNestedPath(self) -> None:
        """
        Convert multi-level dot notation to a nested slash path.

        Validates that three or more dot-separated segments are all
        converted to slash separators with .html appended.
        """
        result = Jinja2Engine._normalisePath("admin.users.index")
        self.assertEqual(result, "admin/users/index.html")

    def testNestedDirectPathWithExtensionIsUnchanged(self) -> None:
        """
        Return a deeply nested direct path with extension unchanged.

        Validates that the presence of a slash signals direct-path mode
        for arbitrarily deep template paths.
        """
        result = Jinja2Engine._normalisePath("partials/nav.html")
        self.assertEqual(result, "partials/nav.html")

    def testTwoDotSegmentsConvertsCorrectly(self) -> None:
        """
        Convert a two-segment dot-notation name to a slash path.

        Validates the basic two-segment case: module.template becomes
        module/template.html.
        """
        result = Jinja2Engine._normalisePath("layout.base")
        self.assertEqual(result, "layout/base.html")

    def testDirectPathWithNonHtmlExtensionIsUnchanged(self) -> None:
        """
        Return a direct path with a non-HTML extension unchanged.

        Validates that any existing dot in the last path segment prevents
        a double extension from being appended.
        """
        result = Jinja2Engine._normalisePath("emails/welcome.txt")
        self.assertEqual(result, "emails/welcome.txt")

class TestJinja2EngineRender(TestCase):

    def _buildEnv(
        self,
        html: str = "",
    ) -> tuple[MagicMock, MagicMock, MagicMock]:
        """
        Build a triple of (env_mock, jinja_env_mock, template_mock).

        Returns mocks wired so env_mock.getJinjaEnvironment() returns
        jinja_env_mock and jinja_env_mock.get_template() returns
        template_mock whose render_async yields the given html string.

        Parameters
        ----------
        html : str
            HTML string the template mock's render_async will return.

        Returns
        -------
        tuple[MagicMock, MagicMock, MagicMock]
            (env_mock, jinja_env_mock, template_mock)
        """
        env_mock = MagicMock()
        jinja_env = MagicMock()
        env_mock.getJinjaEnvironment.return_value = jinja_env
        template_mock = MagicMock()
        template_mock.render_async = AsyncMock(return_value=html)
        jinja_env.get_template.return_value = template_mock
        return env_mock, jinja_env, template_mock

    async def testRenderReturnsRenderedHtml(self) -> None:
        """
        Return the rendered HTML string from a successful render call.

        Validates that the engine delegates to the Jinja2 template's
        render_async and returns the resulting HTML unchanged.
        """
        env_mock, _, _ = self._buildEnv(html="<h1>Hello</h1>")
        engine = Jinja2Engine(env_mock)
        result = await engine.render("users.index", {"name": "World"})
        self.assertEqual(result, "<h1>Hello</h1>")

    async def testRenderNormalisesTemplateNameToPath(self) -> None:
        """
        Normalise the template name before requesting it from the loader.

        Validates that the engine translates dot notation to a file path
        before calling get_template on the Jinja2 environment.
        """
        env_mock, jinja_env, _ = self._buildEnv()
        engine = Jinja2Engine(env_mock)
        await engine.render("users.index", {})
        jinja_env.get_template.assert_called_once_with("users/index.html")

    async def testRenderForwardsContextAsKeywordArgs(self) -> None:
        """
        Forward the context dict as keyword arguments to render_async.

        Validates that all variables in the context mapping are passed
        through to the Jinja2 template during rendering.
        """
        env_mock, _, template_mock = self._buildEnv(html="<p>ok</p>")
        engine = Jinja2Engine(env_mock)
        await engine.render("page.index", {"title": "Home", "count": 3})
        template_mock.render_async.assert_called_once_with(
            title="Home", count=3,
        )

    async def testRenderRaisesViewTemplateNotFoundOnMissingTemplate(self) -> None:
        """
        Raise ViewTemplateNotFoundException when the template is missing.

        Validates that a Jinja2 TemplateNotFound error is wrapped and
        re-raised as the framework's ViewTemplateNotFoundException.
        """
        env_mock = MagicMock()
        jinja_env = MagicMock()
        env_mock.getJinjaEnvironment.return_value = jinja_env
        jinja_env.get_template.side_effect = jinja2.TemplateNotFound(
            "users/index.html",
        )
        engine = Jinja2Engine(env_mock)
        with self.assertRaises(ViewTemplateNotFoundException):
            await engine.render("users.index", {})

    async def testRenderRaisesViewRenderExceptionOnTemplateError(self) -> None:
        """
        Raise ViewRenderException when Jinja2 fails during rendering.

        Validates that a Jinja2 TemplateError raised by render_async is
        wrapped and re-raised as the framework's ViewRenderException.
        """
        env_mock, _, template_mock = self._buildEnv()
        jinja_err = jinja2.TemplateError("syntax error")
        template_mock.render_async = AsyncMock(side_effect=jinja_err)
        engine = Jinja2Engine(env_mock)
        with self.assertRaises(ViewRenderException):
            await engine.render("users.index", {})

    async def testViewTemplateNotFoundPreservesChainedCause(self) -> None:
        """
        Preserve the original Jinja2 exception as __cause__.

        Validates that the ViewTemplateNotFoundException chains the
        original TemplateNotFound exception via the from clause.
        """
        env_mock = MagicMock()
        jinja_env = MagicMock()
        env_mock.getJinjaEnvironment.return_value = jinja_env
        original = jinja2.TemplateNotFound("missing.html")
        jinja_env.get_template.side_effect = original
        engine = Jinja2Engine(env_mock)
        with self.assertRaises(ViewTemplateNotFoundException) as ctx:
            await engine.render("missing", {})
        self.assertIs(ctx.exception.__cause__, original)

    async def testViewRenderExceptionPreservesChainedCause(self) -> None:
        """
        Preserve the original Jinja2 TemplateError as __cause__.

        Validates that the ViewRenderException chains the original
        TemplateError exception via the from clause.
        """
        env_mock, _, template_mock = self._buildEnv()
        original = jinja2.TemplateError("bad syntax")
        template_mock.render_async = AsyncMock(side_effect=original)
        engine = Jinja2Engine(env_mock)
        with self.assertRaises(ViewRenderException) as ctx:
            await engine.render("broken.template", {})
        self.assertIs(ctx.exception.__cause__, original)

    async def testRenderWithEmptyContextSucceeds(self) -> None:
        """
        Render a template successfully when an empty context is supplied.

        Validates that passing an empty dict does not cause errors and
        the engine returns the expected HTML string.
        """
        env_mock, _, _ = self._buildEnv(html="<p>static</p>")
        engine = Jinja2Engine(env_mock)
        result = await engine.render("static.page", {})
        self.assertEqual(result, "<p>static</p>")
