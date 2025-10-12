from dataclasses import dataclass, field
from enum import Enum
from typing import Union, Optional
from orionis.support.entities.base import BaseEntity

class Color(Enum):
    """Enumeration for available colors."""
    RED = 1
    GREEN = 2

class Priority(Enum):
    """Enumeration for priority levels."""
    LOW = "low"
    HIGH = "high"

def default_callback():
    """Default callback function for testing callable defaults."""
    return "callback_result"

@dataclass
class NestedEntity(BaseEntity):
    """
    Nested entity for testing dataclass composition.

    Attributes
    ----------
    value : str
        A simple string value.
    nested_color : Color
        Color value in nested entity.
    """
    value: str = "nested"
    nested_color: Color = Color.RED

@dataclass
class ExampleEntity(BaseEntity):
    """
    Data structure representing an example entity with an identifier, name, color, and tags.

    Parameters
    ----------
    id : int, optional
        Unique identifier for the entity. Default is 0.
    name : str, optional
        Name of the entity. Default is 'default'.
    color : Color, optional
        Color associated with the entity. Default is Color.RED.
    tags : list, optional
        List of tags associated with the entity. Default is an empty list.

    Attributes
    ----------
    id : int
        Unique identifier for the entity.
    name : str
        Name of the entity.
    color : Color
        Color associated with the entity.
    tags : list
        List of tags associated with the entity.
    """
    id: int = 0                                                                         # Default id is 0
    name: str = "default"                                                               # Default name is 'default'
    color: Color = Color.RED                                                            # Default color is RED
    tags: list = field(default_factory=list, metadata={"default": ["tag1", "tag2"]})    # Default tags list

@dataclass
class ComplexEntity(BaseEntity):
    """
    Complex entity for testing advanced field types and behaviors.

    Attributes
    ----------
    union_field : Union[str, int]
        Field that can be either string or integer.
    optional_field : Optional[str]
        Optional string field.
    nested : NestedEntity
        Nested dataclass entity.
    callable_default : str
        Field with callable default value.
    factory_enum : Priority
        Enum field with factory default.
    metadata_default : str
        Field with metadata-defined default.
    """
    union_field: Union[str, int] = "string_value"
    optional_field: Optional[str] = None
    nested: NestedEntity = field(default_factory=lambda: NestedEntity())
    callable_default: str = field(default_factory=default_callback)
    factory_enum: Priority = field(default_factory=lambda: Priority.LOW)
    metadata_default: str = field(default="meta_value", metadata={"default": "metadata_override"})

@dataclass
class CustomPostInitEntity(BaseEntity):
    """
    Entity with custom __post_init__ logic for testing initialization hooks.

    Attributes
    ----------
    base_value : str
        Base value set during initialization.
    computed_value : str
        Value computed in __post_init__.
    """
    base_value: str = "base"
    computed_value: str = field(init=False)

    def __post_init__(self):
        """Custom post-initialization logic."""
        super().__post_init__()
        self.computed_value = f"computed_from_{self.base_value}"

@dataclass
class EmptyEntity(BaseEntity):
    """Empty entity for testing minimal cases."""
    pass