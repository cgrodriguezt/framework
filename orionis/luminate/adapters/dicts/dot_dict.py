from typing import Any, Optional, Dict

class DotDict(dict):
    """
    A dictionary subclass that allows attribute-style access to keys, with full support for nested dictionaries.
    Nested dicts are automatically converted to DotDict instances, enabling recursive dot notation.
    Missing keys return None instead of raising AttributeError or KeyError.
    """

    # Memory optimization
    __slots__ = ()

    def __getattr__(self, key: str) -> Optional[Any]:
        """Enable dot notation access with automatic nested DotDict conversion."""
        try:
            value = self[key]
            if isinstance(value, dict) and not isinstance(value, DotDict):
                value = DotDict(value)
                self[key] = value
            return value
        except KeyError:
            return None

    def __setattr__(self, key: str, value: Any) -> None:
        """Enable dot notation assignment with nested dictionary conversion."""
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        self[key] = value

    def __delattr__(self, key: str) -> None:
        """Enable dot notation deletion with proper error handling."""
        try:
            del self[key]
        except KeyError as e:
            raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{key}'") from e

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """
        Get a value by key, returning default if not found.
        Nested dicts are automatically converted to DotDict.
        """
        value = super().get(key, default)
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
            self[key] = value
        return value

    def export(self) -> Dict[str, Any]:
        """
        Recursively convert this DotDict and all nested DotDicts to regular dicts.
        """
        return {k: v.export() if isinstance(v, DotDict) else v for k, v in self.items()}

    def copy(self) -> 'DotDict':
        """
        Return a deep copy of this DotDict with all nested dictionaries converted.
        """
        return DotDict({k: v.copy() if isinstance(v, DotDict) else (DotDict(v) if isinstance(v, dict) else v)
                        for k, v in self.items()})

    def __repr__(self) -> str:
        """Official string representation of the DotDict."""
        return f"DotDict({super().__repr__()})"