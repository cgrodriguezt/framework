from dataclasses import dataclass
from typing import Type

@dataclass(frozen=True)
class ResolvedDependency:
    """
    A class to represent a resolved dependency of a class instance.
    """
    module_name: str
    class_name: str
    type: Type
    full_class_path: str