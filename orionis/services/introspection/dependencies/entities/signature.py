from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING
from orionis.services.introspection.exceptions import ReflectionTypeError
from orionis.support.entities.base import BaseEntity

if TYPE_CHECKING:
    from orionis.services.introspection.dependencies.entities.argument import Argument

@dataclass(frozen=True, kw_only=True)
class SignatureArguments(BaseEntity):
    """
    Represent dependencies of a class, distinguishing resolved and unresolved.

    Parameters
    ----------
    resolved : dict[str, Argument]
        Mapping of dependency names to resolved Argument instances.
    unresolved : dict[str, Argument]
        Mapping of dependency names to unresolved Argument instances.
    ordered : dict[str, Argument]
        All dependencies in definition order.

    Raises
    ------
    ReflectionTypeError
        If any attribute is not a dictionary.
    """

    resolved: dict[str, Argument]
    unresolved: dict[str, Argument]
    ordered: dict[str, Argument]

    def hasNoDependencies(self) -> bool:
        """
        Check if there are no dependencies.

        Returns
        -------
        bool
            True if 'ordered' is empty, False otherwise.
        """
        # Return True if there are no dependencies in 'ordered'
        return len(self.ordered) == 0

    def hasUnresolvedDependencies(self) -> bool:
        """
        Check if there are unresolved dependencies.

        Returns
        -------
        bool
            True if 'unresolved' is not empty, False otherwise.
        """
        # Return True if there is at least one unresolved dependency
        return len(self.unresolved) > 0

    def toDict(self) -> dict[str, dict]:
        """
        Convert ordered dependencies to a dictionary.

        Returns
        -------
        Dict[str, Dict]
            Mapping of dependency names to their Argument as dict.
        """
        return {name: asdict(arg) for name, arg in self.ordered.items()}

    def getAllOrdered(self) -> dict[str, Argument]:
        """
        Retrieve all dependencies in definition order.

        Returns
        -------
        dict[str, Argument]
            Ordered mapping of dependency names to Argument instances.
        """
        return self.ordered

    def items(self) -> dict[str, Argument].items:
        """
        Provide an iterable view of ordered dependencies.

        Returns
        -------
        ItemsView[str, Argument]
            Iterable of (name, Argument) pairs from 'ordered'.
        """
        return self.ordered.items()

    def getPositionalOnly(self) -> dict[str, Argument]:
        """
        Retrieve positional-only dependencies.

        Returns
        -------
        Dict[str, Argument]
            Mapping of positional-only dependency names to Argument instances.
        """
        # Select arguments that are not keyword-only using a dictionary comprehension
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
            Mapping of positional-only dependency names to their Argument as dict.
        """
        positional_only_args = self.getPositionalOnly()
        return {name: asdict(arg) for name, arg in positional_only_args.items()}

    def getKeywordOnly(self) -> dict[str, Argument]:
        """
        Retrieve keyword-only dependencies.

        Returns
        -------
        dict[str, Argument]
            Mapping of keyword-only dependency names to Argument instances.
        """
        # Select arguments that are keyword-only using a dictionary comprehension
        return {name: arg for name, arg in self.ordered.items() if arg.is_keyword_only}

    def keywordOnlyToDict(self) -> dict[str, dict]:
        """
        Convert keyword-only dependencies to a dictionary.

        Returns
        -------
        dict[str, dict]
            Mapping of keyword-only dependency names to their Argument as dict.
        """
        keyword_only_args = self.getKeywordOnly()
        return {name: asdict(arg) for name, arg in keyword_only_args.items()}

    def getUnresolved(self) -> dict[str, Argument]:
        """
        Retrieve unresolved dependencies.

        Returns
        -------
        dict[str, Argument]
            Mapping of unresolved dependency names to Argument instances.
        """
        return self.unresolved

    def getResolved(self) -> dict[str, Argument]:
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
            Mapping of resolved dependency names to their Argument as dict.
        """
        return {name: asdict(arg) for name, arg in self.resolved.items()}

    def unresolvedToDict(self) -> dict[str, dict]:
        """
        Convert unresolved dependencies to a dictionary.

        Returns
        -------
        dict[str, dict]
            Mapping of unresolved dependency names to their Argument as dict.
        """
        return {name: asdict(arg) for name, arg in self.unresolved.items()}

    def __post_init__(self) -> None:
        """
        Validate types of resolved, unresolved, and ordered attributes.

        Returns
        -------
        None
            This method performs validation only.
        """
        # Validate that 'resolved' is a dictionary
        if not isinstance(self.resolved, dict):
            error_msg = f"'resolved' must be a dict, got {type(self.resolved).__name__}"
            raise ReflectionTypeError(error_msg)
        # Validate that 'unresolved' is a dictionary
        if not isinstance(self.unresolved, dict):
            error_msg = (
                f"'unresolved' must be a dict, got "
                f"{type(self.unresolved).__name__}"
            )
            raise ReflectionTypeError(error_msg)
        # Validate that 'ordered' is a dictionary
        if not isinstance(self.ordered, dict):
            error_msg = f"'ordered' must be a dict, got {type(self.ordered).__name__}"
            raise ReflectionTypeError(error_msg)
