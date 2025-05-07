from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass(frozen=True, kw_only=True)
class MethodDependency:
    """
    A class to represent a method dependency of a class instance.
    """
    resolved: Dict[str, Any]
    unresolved: List[str]