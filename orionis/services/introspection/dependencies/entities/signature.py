from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from orionis.support.entities.base import BaseEntity

if TYPE_CHECKING:
    from _collections_abc import dict_items
    from orionis.services.introspection.dependencies.entities.argument import Argument

@dataclass(frozen=True, kw_only=True)
class Signature(BaseEntity):
    """
    Represent the categorized dependency signature of a callable.

    Groups parameter dependencies into resolved, unresolved, and ordered
    buckets that downstream IoC logic can consume directly.

    Parameters
    ----------
    resolved_args : dict[str, Argument]
        Parameters whose types or defaults are fully known.
    unresolved_args : dict[str, Argument]
        Parameters that lack sufficient type or default information.
    args : dict[str, Argument]
        All parameters in their original declaration order.
    """

    resolved_args: dict[str, Argument]
    unresolved_args: dict[str, Argument]
    args: dict[str, Argument]

    def hasParameters(self) -> bool:
        """
        Determine whether the callable defines any parameters.

        Returns
        -------
        bool
            True if at least one parameter is defined; otherwise False.
        """
        return bool(self.args)

    def arguments(self) -> dict_items[str, Argument]:
        """
        Return an iterable view of all parameters.

        Returns
        -------
        dict_items[str, Argument]
            Iterable of (name, Argument) pairs from 'args'.
        """
        return self.args.items()
