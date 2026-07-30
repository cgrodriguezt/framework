from __future__ import annotations
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, Any
from orionis.orm.schema.constraints import ForeignReference

if TYPE_CHECKING:
    from collections.abc import Callable
    from orionis.orm.schema.types import ColumnType

# Sentinel used to distinguish "no default" from a legitimate ``None`` default.
_NO_DEFAULT: object = object()

@dataclass(frozen=True, slots=True)
class ColumnOptions:
    """
    Secondary, type-specific knobs mirroring SQLAlchemy constructor args.

    A single options object keeps :class:`ColumnDefinition` constructible
    with a handful of parameters while still exposing every keyword that
    the equivalent SQLAlchemy Core type accepts, one attribute per keyword.

    Attributes
    ----------
    length : int or None
        Maximum length for string-like or binary columns.
    precision : int or None
        Total digits for numeric/decimal columns.
    scale : int or None
        Decimal digits for numeric/decimal columns.
    decimal_return_scale : int or None
        Default scale applied when converting floats to decimals.
    as_decimal : bool
        Whether numeric values are returned as ``Decimal``.
    enum_values : tuple of str
        Allowed values for enum columns.
    enum_name : str or None
        Name of the enumerated database type, when applicable.
    native_enum : bool
        Whether to use the backend's native ``ENUM`` type.
    validate_strings : bool
        Whether to validate string values against enum members.
    create_constraint : bool
        Whether to add a CHECK constraint for non-native enum/boolean.
    constraint_name : str or None
        Explicit name for the generated CHECK constraint.
    timezone : bool
        Whether the datetime column is timezone-aware.
    collation : str or None
        Column-level collation for string columns.
    as_uuid : bool
        Whether UUID values are interpreted as ``uuid.UUID`` objects.
    native_uuid : bool
        Whether to use the backend's native UUID-storing type.
    item_type : ColumnDefinition or None
        Element type declaration for array columns.
    dimensions : int or None
        Fixed number of dimensions for array columns.
    as_tuple : bool
        Whether array results are converted to tuples.
    zero_indexes : bool
        Whether array indexes convert between zero- and one-based
        conventions.
    none_as_null : bool
        Whether ``None`` persists as SQL ``NULL`` in JSON columns.
    native : bool
        Whether to use the backend's native ``INTERVAL`` type.
    second_precision : int or None
        Fractional seconds precision for native interval columns.
    day_precision : int or None
        Day precision for native interval columns.
    protocol : int
        Pickle protocol used by pickle-backed columns.
    pickler : object or None
        Object exposing ``dumps``/``loads``, defaults to ``pickle``.
    comparator : Callable or None
        Predicate used to compare pickled values for equality.
    impl : object or None
        Binary-storing type used in place of the default.
    """

    length: int | None = None
    precision: int | None = None
    scale: int | None = None
    decimal_return_scale: int | None = None
    as_decimal: bool = True
    enum_values: tuple[str, ...] = ()
    enum_name: str | None = None
    native_enum: bool = True
    validate_strings: bool = False
    create_constraint: bool = False
    constraint_name: str | None = None
    timezone: bool = False
    collation: str | None = None
    as_uuid: bool = True
    native_uuid: bool = True
    item_type: ColumnDefinition | None = None
    dimensions: int | None = None
    as_tuple: bool = False
    zero_indexes: bool = False
    none_as_null: bool = False
    native: bool = True
    second_precision: int | None = None
    day_precision: int | None = None
    protocol: int = 5
    pickler: object | None = None
    comparator: Callable[[object, object], bool] | None = None
    impl: object | None = None

# Field names copied from ColumnOptions onto every ColumnDefinition instance.
_OPTION_FIELDS: tuple[str, ...] = tuple(field.name for field in fields(ColumnOptions))

class ColumnDefinition:
    """
    Framework-agnostic description of a database column.

    Column types such as :class:`~orionis.orm.schema.types.Integer` or
    :class:`~orionis.orm.schema.types.String` subclass this definition and
    expose a fluent API to declare constraints. The definition never touches
    the underlying SQL engine; the database compiler translates it later.
    """

    __slots__ = (
        "as_decimal",
        "as_tuple",
        "as_uuid",
        "collation",
        "column_type",
        "comment_text",
        "comparator",
        "constraint_name",
        "create_constraint",
        "day_precision",
        "decimal_return_scale",
        "default_value",
        "dimensions",
        "enum_name",
        "enum_values",
        "foreign_ref",
        "has_index",
        "impl",
        "is_auto_increment",
        "is_nullable",
        "is_primary",
        "is_unique",
        "item_type",
        "length",
        "name",
        "native",
        "native_enum",
        "native_uuid",
        "none_as_null",
        "pickler",
        "precision",
        "protocol",
        "scale",
        "second_precision",
        "timezone",
        "validate_strings",
        "zero_indexes",
    )

    def __init__(
        self,
        column_type: ColumnType,
        options: ColumnOptions | None = None,
    ) -> None:
        """
        Initialize the column definition with its type metadata.

        Parameters
        ----------
        column_type : ColumnType
            Logical column type used by the SQL compiler.
        options : ColumnOptions or None, optional
            Type-specific knobs mirroring the SQLAlchemy constructor
            keywords of the concrete subclass. Defaults to every
            :class:`ColumnOptions` field at its own default value.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Attribute name is attached later by the model metaclass.
        self.name: str = ""
        self.column_type = column_type
        resolved = options if options is not None else ColumnOptions()
        for field_name in _OPTION_FIELDS:
            setattr(self, field_name, getattr(resolved, field_name))
        self.is_primary: bool = False
        self.is_nullable: bool = False
        self.is_unique: bool = False
        self.has_index: bool = False
        self.is_auto_increment: bool = False
        self.default_value: Any = _NO_DEFAULT
        self.foreign_ref: ForeignReference | None = None
        self.comment_text: str | None = None

    # ── Fluent constraints ──────────────────────────────────────────────────

    def primary(self) -> ColumnDefinition:
        """
        Mark the column as the primary key of the table.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.is_primary = True
        return self

    def nullable(self) -> ColumnDefinition:
        """
        Allow the column to store ``NULL`` values.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.is_nullable = True
        return self

    def default(self, value: Any) -> ColumnDefinition:  # noqa: ANN401
        """
        Assign a default value applied when no value is provided on insert.

        Parameters
        ----------
        value : Any
            Static value, or a zero-argument callable evaluated per insert.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.default_value = value
        return self

    def unique(self) -> ColumnDefinition:
        """
        Add a unique constraint to the column.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.is_unique = True
        return self

    def index(self) -> ColumnDefinition:
        """
        Create a non-unique index on the column.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.has_index = True
        return self

    def foreign(self, reference: str) -> ColumnDefinition:
        """
        Declare a foreign key pointing at another table column.

        Parameters
        ----------
        reference : str
            Qualified reference in the form ``"table.column"``.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.

        Raises
        ------
        ValueError
            If the reference is not a valid ``"table.column"`` string.
        """
        self.foreign_ref = ForeignReference.parse(reference)
        return self

    def autoIncrement(self) -> ColumnDefinition:
        """
        Mark the column as auto-incrementing.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.is_auto_increment = True
        return self

    def comment(self, text: str) -> ColumnDefinition:
        """
        Attach a descriptive comment rendered alongside the column DDL.

        Parameters
        ----------
        text : str
            Comment text stored by the database engine.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.comment_text = text
        return self

    # ── Introspection helpers ───────────────────────────────────────────────

    def hasDefault(self) -> bool:
        """
        Report whether a default value has been assigned.

        Returns
        -------
        bool
            ``True`` when :meth:`default` was called with any value.
        """
        return self.default_value is not _NO_DEFAULT

    def __repr__(self) -> str:
        """
        Return a concise developer representation of the column.

        Returns
        -------
        str
            Representation including name and logical type.
        """
        return (
            f"<{type(self).__name__} name={self.name!r} "
            f"type={self.column_type!s}>"
        )
