from dataclasses import dataclass
from typing import Any, Dict, List
from orionis.luminate.support.introspection.dependencies.entities.resolved_dependencies import ResolvedDependency

@dataclass(frozen=True, kw_only=True)
class MethodDependency:
    """
    Represents the dependencies of a method, separating resolved and unresolved dependencies.

    Attributes:
        resolved (Dict[ResolvedDependency, Any]):
            A dictionary mapping resolved dependency descriptors to their corresponding
            resolved instances or values for the method.
            All keys must be ResolvedDependency instances.
        unresolved (List[str]):
            A list of method parameter names or dependency identifiers that could not be resolved.
            Must contain only non-empty strings.
    """
    resolved: Dict[ResolvedDependency, Any]
    unresolved: List[str]

    def __post_init__(self):
        """
        Validates types and values of attributes during initialization.

        Raises:
            TypeError: If types don't match the expected:
                - resolved: Dict[ResolvedDependency, Any]
                - unresolved: List[str]
            ValueError: If resolved contains None keys or unresolved contains empty strings
        """
        # Validate 'resolved' is a dict with proper key types
        if not isinstance(self.resolved, dict):
            raise TypeError(
                f"'resolved' must be a dict, got {type(self.resolved).__name__}"
            )

        for dependency in self.resolved:
            if not isinstance(dependency, ResolvedDependency):
                raise TypeError(
                    f"All keys in 'resolved' must be ResolvedDependency instances, "
                    f"found {type(dependency).__name__}"
                )
            if dependency is None:
                raise ValueError("'resolved' cannot contain None keys")

        # Validate 'unresolved' is a list of valid parameter names
        if not isinstance(self.unresolved, list):
            raise TypeError(
                f"'unresolved' must be a list, got {type(self.unresolved).__name__}"
            )

        for param in self.unresolved:
            if not isinstance(param, str):
                raise TypeError(
                    f"All items in 'unresolved' must be strings, "
                    f"found {type(param).__name__}"
                )
            if not param.strip():
                raise ValueError("'unresolved' cannot contain empty parameter names")
            if not param.isidentifier():
                raise ValueError(
                    f"Parameter name '{param}' must be a valid Python identifier"
                )