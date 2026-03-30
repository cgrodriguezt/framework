from __future__ import annotations
from _collections_abc import dict_items
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING
from orionis.support.entities.base import BaseEntity

if TYPE_CHECKING:
    from orionis.services.introspection.dependencies.entities.argument import Argument

@dataclass(frozen=True, kw_only=True)
class Signature(BaseEntity):
    """
    Represent the categorized dependency signature of a callable.

    Groups parameter dependencies into resolved, unresolved, and ordered
    buckets that downstream IoC logic can consume directly.

    Parameters
    ----------
    resolved : dict[str, Argument]
        Parameters whose types or defaults are fully known.
    unresolved : dict[str, Argument]
        Parameters that lack sufficient type or default information.
    ordered : dict[str, Argument]
        All parameters in their original declaration order.
    """

    resolved: dict[str, Argument]
    unresolved: dict[str, Argument]
    ordered: dict[str, Argument]

    def noArgumentsRequired(self) -> bool:
        """
        Determine if there are no dependencies.

        Returns
        -------
        bool
            True if 'ordered' is empty, indicating no dependencies required.
        """
        return len(self.ordered) == 0

    def arguments(self) -> dict_items[str, "Argument"]:
        """
        Return an iterable view of ordered dependencies.

        Returns
        -------
        dict_items[str, Argument]
            Iterable of (name, Argument) pairs from 'ordered'.
        """
        return self.ordered.items()

    def hasUnresolvedArguments(self) -> bool:
        """
        Check if there are unresolved dependencies.

        Returns
        -------
        bool
            True if 'unresolved' is not empty, False otherwise.
        """
        return len(self.unresolved) > 0

    def toDict(self) -> dict[str, dict]:
        """
        Convert ordered dependencies to a dictionary.

        Returns
        -------
        dict[str, dict]
            Mapping of dependency names to their Argument as dict.
        """
        return {name: asdict(arg) for name, arg in self.ordered.items()}

    def getAllOrdered(self) -> dict[str, "Argument"]:
        """
        Retrieve all dependencies in definition order.

        Returns
        -------
        dict[str, Argument]
            Ordered mapping of dependency names to Argument instances.
        """
        return self.ordered

    def items(self) -> dict_items[str, "Argument"]:
        """
        Provide an iterable view of ordered dependencies.

        Returns
        -------
        dict_items[str, Argument]
            Iterable of (name, Argument) pairs from 'ordered'.
        """
        return self.ordered.items()

    def getPositionalOnly(self) -> dict[str, "Argument"]:
        """
        Retrieve positional-only dependencies.

        Returns
        -------
        dict[str, Argument]
            Mapping of positional-only dependency names to Argument instances.
        """
        return {
            name: arg
            for name, arg in self.ordered.items()
            if not arg.is_keyword_only
        }

    def positionalOnlyToDict(self) -> dict[str, dict]:
        """
        Convert positional-only dependencies to a dictionary.

        Returns
        -------
        dict[str, dict]
            Positional-only dependency names mapped to their Argument as dict.
        """
        positional_only_args = self.getPositionalOnly()
        return {name: asdict(arg) for name, arg in positional_only_args.items()}

    def getKeywordOnly(self) -> dict[str, "Argument"]:
        """
        Retrieve keyword-only dependencies.

        Returns
        -------
        dict[str, Argument]
            Mapping of keyword-only dependency names to Argument instances.
        """
        return {
            name: arg
            for name, arg in self.ordered.items()
            if arg.is_keyword_only
        }

    def keywordOnlyToDict(self) -> dict[str, dict]:
        """
        Convert keyword-only dependencies to a dictionary.

        Returns
        -------
        dict[str, dict]
            Keyword-only dependency names mapped to their Argument as dict.
        """
        keyword_only_args = self.getKeywordOnly()
        return {name: asdict(arg) for name, arg in keyword_only_args.items()}

    def getUnresolved(self) -> dict[str, "Argument"]:
        """
        Retrieve unresolved dependencies.

        Returns
        -------
        dict[str, Argument]
            Mapping of unresolved dependency names to Argument instances.
        """
        return self.unresolved

    def getResolved(self) -> dict[str, "Argument"]:
        """
        Retrieve resolved dependencies.

        Returns
        -------
        dict[str, Argument]
            Mapping of resolved dependency names to Argument instances.
        """
        return self.resolved

    def resolvedToDict(self) -> dict[str, dict]:
        """
        Convert resolved dependencies to a dictionary.

        Returns
        -------
        dict[str, dict]
            Resolved dependency names mapped to their Argument as dict.
        """
        return {name: asdict(arg) for name, arg in self.resolved.items()}

    def unresolvedToDict(self) -> dict[str, dict]:
        """
        Convert unresolved dependencies to a dictionary.

        Returns
        -------
        dict[str, dict]
            Unresolved dependency names mapped to their Argument as dict.
        """
        return {name: asdict(arg) for name, arg in self.unresolved.items()}

    def __post_init__(self) -> None:
        """
        Validate types of resolved, unresolved, and ordered attributes.

        Returns
        -------
        None
            Raises TypeError if any attribute is not a dict.
        """
        if not isinstance(self.resolved, dict):
            error_msg = (
                f"'resolved' must be a dict, "
                f"got {type(self.resolved).__name__}"
            )
            raise TypeError(error_msg)
        if not isinstance(self.unresolved, dict):
            error_msg = (
                f"'unresolved' must be a dict, "
                f"got {type(self.unresolved).__name__}"
            )
            raise TypeError(error_msg)
        if not isinstance(self.ordered, dict):
            error_msg = (
                f"'ordered' must be a dict, "
                f"got {type(self.ordered).__name__}"
            )
            raise TypeError(error_msg)
