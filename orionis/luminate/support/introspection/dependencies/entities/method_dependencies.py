from dataclasses import dataclass
from typing import Any, Dict, List
from orionis.luminate.support.introspection.dependencies.entities.resolved_dependencies import ResolvedDependency

@dataclass(frozen=True, kw_only=True)
class MethodDependency:
    """
    A class to represent a method dependency of a class instance.
    """
    resolved: Dict[ResolvedDependency, Any]
    unresolved: List[str]