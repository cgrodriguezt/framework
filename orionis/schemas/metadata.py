from __future__ import annotations
from dataclasses import dataclass, field
from orionis.schemas.rules.strong_password import StrongPassword

# ---------------------------------------------------------------------------
# Hierarchy roots
# ---------------------------------------------------------------------------

class ValidationMetadata:
    """
    Root marker for all Orionis field-level annotations.

    Every metadata class that can be applied to a ``Schema`` field must
    inherit—directly or indirectly—from this class. This allows the
    ``MetaCompiler`` and other framework components to identify Orionis
    metadata at runtime through instance checks.

    Notes
    -----
    ``__slots__ = ()`` is declared so that frozen dataclass subclasses
    that use ``slots=True`` do not encounter ``__dict__``/slot conflicts.
    """

    __slots__ = ()

class ConstraintMetadata(ValidationMetadata):
    """
    Intermediate marker for validation constraints.

    Constraint metadata participates in value validation at decode time.
    Each concrete subclass may expose a ``message`` keyword-only field
    (default ``None``) reserved for future custom error messaging without
    breaking the public API when that feature is introduced.
    """

    __slots__ = ()

class DocumentMetadata(ValidationMetadata):
    """
    Intermediate marker for documentation / JSON Schema metadata.

    Document metadata does not participate in value validation; it
    provides supplementary information used when generating JSON Schema
    or OpenAPI output (title, description, examples, extra properties).
    """

    __slots__ = ()

# ---------------------------------------------------------------------------
# Numeric constraints
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class GreaterThan(ConstraintMetadata):
    """
    Assert that a numeric value is *strictly* greater than ``value``.

    Parameters
    ----------
    value : int | float
        The exclusive lower bound.
    message : str | None
        Reserved for a future custom validation error message.
    """

    value: int | float
    message: str | None = field(default=None, kw_only=True)

@dataclass(frozen=True, slots=True)
class GreaterThanOrEqual(ConstraintMetadata):
    """
    Assert that a numeric value is greater than or equal to ``value``.

    Parameters
    ----------
    value : int | float
        The inclusive lower bound.
    message : str | None
        Reserved for a future custom validation error message.
    """

    value: int | float
    message: str | None = field(default=None, kw_only=True)

@dataclass(frozen=True, slots=True)
class LessThan(ConstraintMetadata):
    """
    Assert that a numeric value is *strictly* less than ``value``.

    Parameters
    ----------
    value : int | float
        The exclusive upper bound.
    message : str | None
        Reserved for a future custom validation error message.
    """

    value: int | float
    message: str | None = field(default=None, kw_only=True)

@dataclass(frozen=True, slots=True)
class LessThanOrEqual(ConstraintMetadata):
    """
    Assert that a numeric value is less than or equal to ``value``.

    Parameters
    ----------
    value : int | float
        The inclusive upper bound.
    message : str | None
        Reserved for a future custom validation error message.
    """

    value: int | float
    message: str | None = field(default=None, kw_only=True)

@dataclass(frozen=True, slots=True)
class MultipleOf(ConstraintMetadata):
    """
    Assert that a numeric value is a multiple of ``value``.

    Parameters
    ----------
    value : int | float
        The divisor; the field value must be evenly divisible by this.
    message : str | None
        Reserved for a future custom validation error message.
    """

    value: int | float
    message: str | None = field(default=None, kw_only=True)

# ---------------------------------------------------------------------------
# String / collection constraints
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Pattern(ConstraintMetadata):
    """
    Assert that a string value matches the given ``regex`` pattern.

    Parameters
    ----------
    regex : str
        A regular expression that the field value must fully match.
    message : str | None
        Reserved for a future custom validation error message.
    """

    regex: str
    message: str | None = field(default=None, kw_only=True)

@dataclass(frozen=True, slots=True)
class MinLength(ConstraintMetadata):
    """
    Assert that a string or collection has at least ``value`` characters/items.

    Parameters
    ----------
    value : int
        The minimum allowed length (inclusive).
    message : str | None
        Reserved for a future custom validation error message.
    """

    value: int
    message: str | None = field(default=None, kw_only=True)

@dataclass(frozen=True, slots=True)
class MaxLength(ConstraintMetadata):
    """
    Assert that a string or collection has at most ``value`` characters/items.

    Parameters
    ----------
    value : int
        The maximum allowed length (inclusive).
    message : str | None
        Reserved for a future custom validation error message.
    """

    value: int
    message: str | None = field(default=None, kw_only=True)

# ---------------------------------------------------------------------------
# Temporal constraints
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TimezoneAware(ConstraintMetadata):
    """
    Assert timezone-awareness on a ``datetime.datetime`` or ``datetime.time``.

    Requires the annotated value to carry explicit timezone information.

    Parameters
    ----------
    message : str | None
        Reserved for a future custom validation error message.
    """

    message: str | None = field(default=None, kw_only=True)

@dataclass(frozen=True, slots=True)
class TimezoneNaive(ConstraintMetadata):
    """
    Assert timezone-naivety on a ``datetime.datetime`` or ``datetime.time``.

    Requires the annotated value to have *no* timezone information.

    Parameters
    ----------
    message : str | None
        Reserved for a future custom validation error message.
    """

    message: str | None = field(default=None, kw_only=True)

# ---------------------------------------------------------------------------
# Documentation / JSON Schema metadata
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Title(DocumentMetadata):
    """
    Provide a human-readable title for the field in JSON Schema / OpenAPI.

    Parameters
    ----------
    value : str
        The field title shown in generated schema output.
    """

    value: str

@dataclass(frozen=True, slots=True)
class Description(DocumentMetadata):
    """
    Provide a human-readable description for the field in JSON Schema / OpenAPI.

    Parameters
    ----------
    value : str
        The field description shown in generated schema output.
    """

    value: str

@dataclass(frozen=True, slots=True)
class Examples(DocumentMetadata):
    """
    Provide example values for the field in JSON Schema / OpenAPI.

    Parameters
    ----------
    values : list[object]
        A list of example values; each must be JSON-serialisable.
    """

    values: list[object]

@dataclass(frozen=True, slots=True)
class ExtraJsonSchema(DocumentMetadata):
    """
    Inject additional raw JSON Schema properties for the field.

    The ``data`` mapping is merged directly into the generated JSON Schema
    object, allowing arbitrary schema extensions (e.g. ``readOnly``,
    ``deprecated``, vendor-specific ``x-`` properties).

    Parameters
    ----------
    data : dict[str, object]
        Key/value pairs to merge into the JSON Schema object.
    """

    data: dict[str, object]

@dataclass(frozen=True, slots=True)
class Extra(DocumentMetadata):
    """
    Attach arbitrary extra data to the field metadata.

    The ``data`` mapping is passed through as-is and is not interpreted
    by the schema generation pipeline. Use it for application-specific
    annotations that do not belong in the JSON Schema output.

    Parameters
    ----------
    data : dict[str, object]
        Arbitrary key/value pairs to attach to the field.
    """

    data: dict[str, object]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__: list[str] = [
    "ConstraintMetadata",
    "Description",
    "DocumentMetadata",
    "Examples",
    "Extra",
    "ExtraJsonSchema",
    "GreaterThan",
    "GreaterThanOrEqual",
    "LessThan",
    "LessThanOrEqual",
    "MaxLength",
    "MinLength",
    "MultipleOf",
    "Pattern",
    "StrongPassword",
    "TimezoneAware",
    "TimezoneNaive",
    "Title",
    "ValidationMetadata",
]
