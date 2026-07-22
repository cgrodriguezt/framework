from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.http.response import HTMLResponse

class IViewFactory(ABC):
    """
    Contract for the view factory.

    Callers use this interface to render named templates and receive
    fully formed :class:`HTMLResponse` objects ready to return from
    HTTP controllers.
    """

    # ruff: noqa: ANN401

    __slots__ = ()

    @abstractmethod
    async def make(self, template: str, **context: Any) -> HTMLResponse:
        """
        Render a template and return an :class:`HTMLResponse`.

        Parameters
        ----------
        template : str
            Template name using dot notation (e.g. ``'users.index'``) or a
            direct path relative to a configured template directory.
        **context : Any
            Keyword arguments are forwarded as template variables.

        Returns
        -------
        HTMLResponse
            An HTTP response whose body is the rendered HTML string.

        Raises
        ------
        ViewTemplateNotFoundException
            When the requested template file cannot be located.
        ViewRenderException
            When the template engine fails during rendering.
        """
