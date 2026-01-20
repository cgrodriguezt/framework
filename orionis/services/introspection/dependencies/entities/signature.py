from dataclasses import dataclass, asdict
from typing import Dict
from orionis.services.introspection.dependencies.entities.argument import Argument
from orionis.services.introspection.exceptions import ReflectionTypeError
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class SignatureArguments(BaseEntity):
    """
    Represents the dependencies of a class, distinguishing between resolved and unresolved dependencies.

    This class encapsulates both successfully resolved dependencies (with their corresponding
    Argument instances) and unresolved dependencies that could not be satisfied during
    dependency injection or reflection analysis.

    Parameters
    ----------
    resolved : Dict[str, Argument]
        Dictionary mapping dependency names to their corresponding Argument instances
        that have been successfully resolved.
    unresolved : Dict[str, Argument]
        Dictionary mapping dependency names to their corresponding Argument instances
        that could not be resolved during dependency analysis.

    Attributes
    ----------
    resolved : Dict[str, Argument]
        The resolved dependencies for the class, where each key is a dependency name
        and each value is an Argument instance containing the resolved information.
    unresolved : Dict[str, Argument]
        The unresolved dependency names mapped to their Argument instances, representing
        dependencies that could not be satisfied.
    ordered : Dict[str, Argument]
        All dependencies (both resolved and unresolved) in the order they were defined.

    Raises
    ------
    ReflectionTypeError
        If 'resolved' is not a dictionary or 'unresolved' is not a dictionary.
    """

    # Resolved dependencies as a dictionary of names to Argument instances
    resolved: Dict[str, Argument]

    # Unresolved dependencies as a dictionary of names to Argument instances
    unresolved: Dict[str, Argument]

    # All dependencies in the order they were defined
    ordered: Dict[str, Argument]

    def hasNoDependencies(self) -> bool:
        """
        Checks whether the class has any dependencies, either resolved or unresolved.

        This method evaluates if the 'ordered' dictionary, which contains all dependencies
        in their defined order, is empty. If there are no dependencies present, it returns True;
        otherwise, it returns False.

        Returns
        -------
        bool
            True if there are no dependencies (the 'ordered' dictionary is empty),
            False if there is at least one dependency.
        """
        # Return True if there are no dependencies in 'ordered', otherwise False
        return len(self.ordered) == 0

    def hasUnresolvedDependencies(self) -> bool:
        """
        Checks if there are any unresolved dependencies.

        This method evaluates whether the 'unresolved' dictionary, which contains dependencies
        that could not be resolved, is empty. If there is at least one unresolved dependency,
        it returns True; otherwise, it returns False.

        Returns
        -------
        bool
            True if there are unresolved dependencies (the 'unresolved' dictionary is not empty),
            False if all dependencies have been resolved.
        """
        # Return True if there is at least one unresolved dependency, otherwise False
        return len(self.unresolved) > 0

    def toDict(self) -> Dict[str, Dict]:
        """
        Converts the ordered dependencies into a dictionary representation.

        Returns
        -------
        Dict[str, Dict]
            A dictionary where each dependency name is associated with its
            corresponding Argument instance represented as a dictionary.
        """
        return {name: asdict(arg) for name, arg in self.ordered.items()}

    def getAllOrdered(self) -> Dict[str, Argument]:
        """
        Retrieves the dictionary of all dependencies in the order they were defined.

        Returns
        -------
        Dict[str, Argument]
            A dictionary where each key is the name of a dependency and
            each value is the corresponding Argument instance, maintaining
            the original order of definition.
        """
        return self.ordered

    def items(self):
        """
        Provides an iterable view of the ordered dependencies.

        This method returns an iterable view of the items in the 'ordered' dictionary,
        allowing iteration over the dependency names and their corresponding Argument instances.

        Returns
        -------
        ItemsView[str, Argument]
            An iterable view of the (name, Argument) pairs in the 'ordered' dictionary.
        """
        return self.ordered.items()

    def getPositionalOnly(self) -> Dict[str, Argument]:
        """
        Retrieves all positional-only dependencies from the ordered arguments.

        This method iterates through the ordered dependencies and selects those
        that are marked as positional-only, based on the 'is_keyword_only' attribute
        of each Argument instance.

        Returns
        -------
        Dict[str, Argument]
            A dictionary containing only the positional-only dependencies, where
            each key is the dependency name and each value is the corresponding
            Argument instance.
        """
        # Initialize an empty dictionary to store positional-only arguments
        arguments = {}

        # Iterate through all ordered arguments
        for name, arg in self.ordered.items():

            # Check if the argument is positional-only (not keyword-only)
            if not arg.is_keyword_only:
                arguments[name] = arg

        # Return the dictionary of positional-only arguments
        return arguments

    def positionalOnlyToDict(self) -> Dict[str, Dict]:
        """
        Converts the positional-only dependencies into a dictionary representation.

        Returns
        -------
        Dict[str, Dict]
            A dictionary where each positional-only dependency name is associated
            with its corresponding Argument instance represented as a dictionary.
        """
        # Retrieve positional-only arguments
        positional_only_args = self.getPositionalOnly()

        # Convert each Argument instance to a dictionary
        return {name: asdict(arg) for name, arg in positional_only_args.items()}

    def getKeywordOnly(self) -> Dict[str, Argument]:
        """
        Retrieves all keyword-only dependencies from the ordered arguments.

        This method iterates through the ordered dependencies and selects those
        that are marked as keyword-only, based on the 'is_keyword_only' attribute
        of each Argument instance.

        Returns
        -------
        Dict[str, Argument]
            A dictionary containing only the keyword-only dependencies, where
            each key is the dependency name and each value is the corresponding
            Argument instance.
        """
        # Initialize an empty dictionary to store keyword-only arguments
        arguments = {}

        # Iterate through all ordered arguments
        for name, arg in self.ordered.items():

            # Check if the argument is keyword-only
            if arg.is_keyword_only:
                arguments[name] = arg

        # Return the dictionary of keyword-only arguments
        return arguments

    def keywordOnlyToDict(self) -> Dict[str, Dict]:
        """
        Converts the keyword-only dependencies into a dictionary representation.

        Returns
        -------
        Dict[str, Dict]
            A dictionary where each keyword-only dependency name is associated
            with its corresponding Argument instance represented as a dictionary.
        """
        # Retrieve keyword-only arguments
        keyword_only_args = self.getKeywordOnly()

        # Convert each Argument instance to a dictionary
        return {name: asdict(arg) for name, arg in keyword_only_args.items()}

    def getUnresolved(self) -> Dict[str, Argument]:
        """
        Retrieves the dictionary of unresolved dependencies.

        Returns
        -------
        Dict[str, Argument]
            A dictionary where each key is the name of an unresolved dependency
            and each value is the corresponding Argument instance.
        """
        return self.unresolved

    def getResolved(self) -> Dict[str, Argument]:
        """
        Retrieves the dictionary of resolved dependencies.

        Returns
        -------
        Dict[str, Argument]
            A dictionary where each key is the name of a resolved dependency
            and each value is the corresponding Argument instance.
        """
        return self.resolved

    def resolvedToDict(self) -> Dict[str, Dict]:
        """
        Converts the resolved dependencies into a dictionary representation.

        Returns
        -------
        Dict[str, Dict]
            A dictionary where each resolved dependency name is associated
            with its corresponding Argument instance represented as a dictionary.
        """
        return {name: asdict(arg) for name, arg in self.resolved.items()}

    def unresolvedToDict(self) -> Dict[str, Dict]:
        """
        Converts the unresolved dependencies into a dictionary representation.

        Returns
        -------
        Dict[str, Dict]
            A dictionary where each unresolved dependency name is associated
            with its corresponding Argument instance represented as a dictionary.
        """
        return {name: asdict(arg) for name, arg in self.unresolved.items()}

    def __post_init__(self):
        """
        Validates the types and contents of the resolved and unresolved attributes.

        This method is automatically called by the dataclass after object initialization
        to ensure that both attributes are dictionaries with the correct types. It performs
        runtime type checking to maintain data integrity and provide clear error messages
        when invalid types are provided.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs validation only and does not return any value.

        Raises
        ------
        ReflectionTypeError
            If 'resolved' is not a dict or 'unresolved' is not a dict.
        """
        # Validate that the 'resolved' attribute is a dictionary type
        # This ensures that resolved dependencies can be properly accessed by name
        if not isinstance(self.resolved, dict):
            raise ReflectionTypeError(
                f"'resolved' must be a dict, got {type(self.resolved).__name__}",
            )

        # Validate that the 'unresolved' attribute is a dictionary type
        # This ensures that unresolved dependencies maintain the same structure as resolved ones
        if not isinstance(self.unresolved, dict):
            raise ReflectionTypeError(
                f"'unresolved' must be a dict, got {type(self.unresolved).__name__}",
            )

        # Validate that the 'ordered' attribute is a dictionary type
        # This ensures that all dependencies maintain the same structure as resolved ones
        if not isinstance(self.ordered, dict):
            raise ReflectionTypeError(
                f"'ordered' must be a dict, got {type(self.ordered).__name__}",
            )
