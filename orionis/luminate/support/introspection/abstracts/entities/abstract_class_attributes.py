from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True, kw_only=True)
class AbstractClassAttributes:
    """
    A class to represent the attributes of an entity.
    """
    public: Dict[str, Any]
    private: Dict[str, Any]
    protected: Dict[str, Any]