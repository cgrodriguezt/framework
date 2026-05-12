from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from orionis.http.routes.compiled_route import CompiledRoute

@dataclass(slots=True, frozen=True)
class ResolvedRoute:
    """
    Represent the immutable result of a successful route resolution.

    Attributes
    ----------
    route : CompiledRoute
        The matched compiled route descriptor.
    params : dict[str, Any]
        Path parameters extracted and type-converted from the URL.
        Empty for static routes.
    """

    route: CompiledRoute
    params: dict[str, Any]
