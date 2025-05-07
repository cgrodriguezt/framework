from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass(frozen=True)
class ClassDependency:
    """
    A class to represent a dependency of a class instance.
    """
    resolved: Dict[str, Any]
    unresolved: List[str]
