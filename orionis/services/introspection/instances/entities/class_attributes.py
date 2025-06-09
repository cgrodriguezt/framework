from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True, kw_only=True)
class ClassAttributes:
    """
    Represents the attributes of a class instance.

    Parameters
    ----------
    public : dict of str to Any
        Public attributes of the class instance.
    private : dict of str to Any
        Private attributes of the class instance.
    protected : dict of str to Any
        Protected attributes of the class instance.
    """
    public: Dict[str, Any]
    private: Dict[str, Any]
    protected: Dict[str, Any]