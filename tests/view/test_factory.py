from unittest.mock import AsyncMock, MagicMock
from orionis.http.response import HTMLResponse
from orionis.test import TestCase
from orionis.view.exceptions import ViewRenderException, ViewTemplateNotFoundException
from orionis.view.factory import ViewFactory

class TestViewFactory(TestCase):

    def _buildEngine(self, html: str = "<html></html>") -> MagicMock:
        """
        Build a mock IViewEngine whose render returns the given html.

        Parameters
        ----------
        html : str
            HTML string the mock engine's render method will return.

        Returns
        -------
        MagicMock
            A mock object with render set up as an AsyncMock.
        """
        engine = MagicMock()
        engine.render = AsyncMock(return_value=html)
        return engine

    async def testMakeReturnsHtmlResponse(self) -> None:
        """
        Verify make returns an HTMLResponse instance.

        Validates that the factory wraps the engine's output in an
        HTMLResponse rather than returning a plain string.
        """
        engine = self._buildEngine(html="<p>Hello</p>")
        factory = ViewFactory(engine)
        response = await factory.make("users.index")
        self.assertIsInstance(response, HTMLResponse)

    async def testMakeBodyContainsRenderedHtml(self) -> None:
        """
        Verify the response body contains the rendered HTML string.

        Validates that the engine's output is correctly stored in the
        response body and is accessible as bytes.
        """
        engine = self._buildEngine(html="<p>Rendered</p>")
        factory = ViewFactory(engine)
        response = await factory.make("users.index")
        self.assertIn(b"<p>Rendered</p>", response._body)

    async def testMakePassesTemplateNameToEngine(self) -> None:
        """
        Forward the template name to the underlying engine.

        Validates that the factory calls engine.render with the exact
        template string supplied by the caller.
        """
        engine = self._buildEngine()
        factory = ViewFactory(engine)
        await factory.make("users.index")
        engine.render.assert_called_once()
        call_args = engine.render.call_args
        self.assertEqual(call_args[0][0], "users.index")

    async def testMakePassesContextToEngine(self) -> None:
        """
        Forward keyword context arguments to the engine as a dict.

        Validates that **context kwargs are collected into a dict and
        forwarded as the second positional argument to engine.render.
        """
        engine = self._buildEngine()
        factory = ViewFactory(engine)
        await factory.make("users.index", name="World", count=5)
        call_args = engine.render.call_args
        self.assertEqual(call_args[0][1], {"name": "World", "count": 5})

    async def testMakeSetsOrionisRenderHeader(self) -> None:
        """
        Set the X-Orionis-Render header on the response.

        Validates that the factory marks SSR responses with the
        X-Orionis-Render header so clients can identify server rendering.
        """
        engine = self._buildEngine()
        factory = ViewFactory(engine)
        response = await factory.make("users.index")
        self.assertTrue(response.hasHeader("x-orionis-render"))

    async def testMakeOrionisRenderHeaderValueIsSsr(self) -> None:
        """
        Set the X-Orionis-Render header value to 'SSR'.

        Validates that the header carries the expected SSR marker value
        identifying server-side rendering.
        """
        engine = self._buildEngine()
        factory = ViewFactory(engine)
        response = await factory.make("users.index")
        header_values = response.getHeader("x-orionis-render")
        self.assertIsNotNone(header_values)
        self.assertIn("SSR", header_values)

    async def testMakePropagatesToViewTemplateNotFoundException(self) -> None:
        """
        Propagate ViewTemplateNotFoundException from the engine.

        Validates that the factory does not swallow template-not-found
        errors raised by the rendering engine.
        """
        err_msg = "template not found"
        engine = MagicMock()
        engine.render = AsyncMock(
            side_effect=ViewTemplateNotFoundException(err_msg),
        )
        factory = ViewFactory(engine)
        with self.assertRaises(ViewTemplateNotFoundException):
            await factory.make("missing.template")

    async def testMakePropagatesViewRenderException(self) -> None:
        """
        Propagate ViewRenderException from the engine.

        Validates that the factory does not swallow render errors raised
        by the underlying Jinja2 engine.
        """
        err_msg = "render failed"
        engine = MagicMock()
        engine.render = AsyncMock(side_effect=ViewRenderException(err_msg))
        factory = ViewFactory(engine)
        with self.assertRaises(ViewRenderException):
            await factory.make("broken.template")

    async def testMakeWithEmptyContextSucceeds(self) -> None:
        """
        Render a template successfully when no context kwargs are given.

        Validates that an empty context is forwarded correctly without
        causing errors in the engine call.
        """
        engine = self._buildEngine(html="<p>static</p>")
        factory = ViewFactory(engine)
        response = await factory.make("static.page")
        self.assertIsInstance(response, HTMLResponse)
        self.assertIn(b"<p>static</p>", response._body)
