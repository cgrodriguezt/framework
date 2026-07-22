from __future__ import annotations
from typing import Any

def buildViewExtensions() -> list[Any]:
    """
    Return the list of Jinja2 extension classes to register at boot time.

    Add extension classes to the returned list to make them available in
    every template rendered by the framework.  Extensions are registered
    via :meth:`ViewEnvironment.addExtension` during the boot phase of
    :class:`ViewServiceProvider`.

    Returns
    -------
    list[Any]
        Ordered list of Jinja2 :class:`Extension` subclasses (or their
        dotted import paths).  An empty list disables all custom extensions.
    """
    # Register extensions here as the view system grows.
    return []
