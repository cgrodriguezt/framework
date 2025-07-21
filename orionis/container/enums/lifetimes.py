from enum import Enum, auto

class Lifetime(Enum):
    """
    Defines the lifecycle types for dependency injection.

    Numpy style docstring:

    Attributes
    ----------
    TRANSIENT : Lifetime
        A new instance is provided every time the dependency is requested.
    SINGLETON : Lifetime
        A single shared instance is provided for the entire application lifetime.
    SCOPED : Lifetime
        An instance is provided per scope (e.g., per request or session).
    """

    TRANSIENT = auto()
    SINGLETON = auto()
    SCOPED = auto()
