from dataclasses import dataclass
from typing import Type, Any

@dataclass(frozen=True, kw_only=True)
class ResolvedDependency:
    """
    Represents a fully resolved dependency with complete type information.

    Attributes:
        module_name (str):
            The name of the module where the dependency is defined.
            Must be a non-empty string without spaces.
        class_name (str):
            The name of the class/type being resolved.
            Must be a valid Python identifier.
        type (Type):
            The actual Python type object of the resolved dependency.
        full_class_path (str):
            The full import path to the class (e.g., 'package.module.ClassName').
            Must match 'module_name.class_name' pattern.
    """
    module_name: str
    class_name: str
    type: Type[Any]
    full_class_path: str

    def __post_init__(self):
        """
        Validates all fields during initialization.

        Raises:
            TypeError: If any field has incorrect type.
            ValueError: If string fields are empty or don't meet format requirements.
        """
        # Validate module_name
        if not isinstance(self.module_name, str):
            raise TypeError(f"module_name must be str, got {type(self.module_name).__name__}")
        if not self.module_name:
            raise ValueError("module_name cannot be empty")
        if any(c.isspace() for c in self.module_name):
            raise ValueError("module_name cannot contain whitespace")

        # Validate class_name
        if not isinstance(self.class_name, str):
            raise TypeError(f"class_name must be str, got {type(self.class_name).__name__}")
        if not self.class_name.isidentifier():
            raise ValueError(f"class_name must be valid Python identifier, got '{self.class_name}'")

        # Validate type
        if not isinstance(self.type, type):
            raise TypeError(f"type must be a type object, got {type(self.type).__name__}")

        # Validate full_class_path
        if not isinstance(self.full_class_path, str):
            raise TypeError(f"full_class_path must be str, got {type(self.full_class_path).__name__}")
        expected_path = f"{self.module_name}.{self.class_name}"
        if self.full_class_path != expected_path:
            raise ValueError(
                f"full_class_path must be '{expected_path}', got '{self.full_class_path}'"
            )