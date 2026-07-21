from orionis.http.middleware import BaseMiddleware
from orionis.test import TestCase

class TestBaseMiddleware(TestCase):
    """Unit tests for the BaseMiddleware abstract class."""

    async def testHandleRaisesNotImplementedError(self) -> None:
        """
        Verify that the base handle() method raises NotImplementedError.

        Confirms that callers attempting to use an un-subclassed
        BaseMiddleware receive a NotImplementedError.
        """

        class _Bare(BaseMiddleware):
            pass

        async def _next():
            pass

        instance = _Bare()
        with self.assertRaises(NotImplementedError):
            await instance.handle(None, _next)  # type: ignore[arg-type]

    async def testSubclassCanImplementHandle(self) -> None:
        """
        Verify that a concrete subclass can override handle() successfully.

        Confirms that defining handle() in a subclass does not raise and
        is invoked correctly.
        """

        class _Concrete(BaseMiddleware):
            async def handle(self, _request, _call_next):  # type: ignore[override]
                return "response"

        instance = _Concrete()
        result = await instance.handle(None, None)  # type: ignore[arg-type]
        self.assertEqual(result, "response")

    def testBaseMiddlewareIsSubclassable(self) -> None:
        """
        Verify that BaseMiddleware can be subclassed without errors.

        Confirms that the class hierarchy allows clean inheritance.
        """

        class _MW(BaseMiddleware):
            async def handle(self, _request, call_next):  # type: ignore[override]
                return await call_next()

        self.assertTrue(issubclass(_MW, BaseMiddleware))

    async def testErrorMessageContainsClassName(self) -> None:
        """
        Verify that the NotImplementedError message includes the subclass name.

        Confirms that the class name is interpolated into the error string
        to aid debugging.
        """

        class _CustomMiddleware(BaseMiddleware):
            pass

        async def _next():
            pass

        instance = _CustomMiddleware()
        message: str | None = None
        try:
            await instance.handle(None, _next)  # type: ignore[arg-type]
        except NotImplementedError as exc:
            message = str(exc)

        self.assertIsNotNone(message)
        self.assertIn("_CustomMiddleware", message)
