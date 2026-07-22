from __future__ import annotations
from orionis.container.providers.service_provider import ServiceProvider
from orionis.view.contracts.engine import IViewEngine
from orionis.view.contracts.environment import IViewEnvironment
from orionis.view.contracts.factory import IViewFactory
from orionis.view.engine import Jinja2Engine
from orionis.view.environment import ViewEnvironment
from orionis.view.extensions import buildViewExtensions
from orionis.view.factory import ViewFactory
from orionis.view.filters import buildViewFilters
from orionis.view.globals import buildViewGlobals
from orionis.support.facades.view import View as ViewFacade

class ViewServiceProvider(ServiceProvider):
    """
    Register and boot the view system into the application container.

    Registration phase
    ------------------
    Binds :class:`IViewEnvironment` → :class:`ViewEnvironment`,
    :class:`IViewEngine` → :class:`Jinja2Engine`, and
    :class:`IViewFactory` → :class:`ViewFactory` as singletons.

    Boot phase
    ----------
    Registers template globals, filters, and extensions with the
    :class:`ViewEnvironment` singleton, then pins the :class:`View`
    facade for zero-resolution access on the hot path.
    """

    def register(self) -> None:
        """
        Bind view services as singletons in the application container.

        Returns
        -------
        None
        """
        # Environment wraps and owns the Jinja2 Environment instance
        self.app.singleton(IViewEnvironment, ViewEnvironment)

        # Engine uses the environment to perform async rendering
        self.app.singleton(IViewEngine, Jinja2Engine)

        # Factory is the public entry-point for controllers
        self.app.singleton(IViewFactory, ViewFactory)

    async def boot(self) -> None:
        """
        Register globals, filters, and extensions; then pin the facade.

        Returns
        -------
        None
        """
        # Resolve the shared environment singleton
        _env: IViewEnvironment = await self.app.make(IViewEnvironment)

        # Register all template globals bound to the application instance
        for _name, _value in buildViewGlobals(self.app).items():
            _env.addGlobal(_name, _value)

        # Register all template filters
        for _name, _callback in buildViewFilters().items():
            _env.addFilter(_name, _callback)

        # Register all Jinja2 extensions
        for _extension in buildViewExtensions():
            _env.addExtension(_extension)

        # Pin the facade for direct attribute access without DI overhead
        await ViewFacade.pin()
