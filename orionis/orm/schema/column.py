from __future__ import annotations
from typing import TYPE_CHECKING, Any
from orionis.orm.schema.constraints import ForeignReference

if TYPE_CHECKING:
    from orionis.orm.schema.types import ColumnType

# Sentinel used to distinguish "no default" from a legitimate ``None`` default.
_NO_DEFAULT: object = object()


class ColumnDefinition:
    """
    Framework-agnostic description of a database column.

    Column types such as :class:`~orionis.orm.schema.types.Integer` or
    :class:`~orionis.orm.schema.types.String` subclass this definition and
    expose a fluent API to declare constraints. The definition never touches
    the underlying SQL engine; the database compiler translates it later.
    """

    __slots__ = (
        "columnType",
        "defaultValue",
        "enumValues",
        "foreignRef",
        "hasIndex",
        "isAutoIncrement",
        "isNullable",
        "isPrimary",
        "isUnique",
        "length",
        "name",
        "precision",
        "scale",
    )

    def __init__(
        self,
        columnType: ColumnType,  # noqa: N803 # NOSONAR
        *,
        length: int | None = None,
        precision: int | None = None,
        scale: int | None = None,
        enumValues: tuple[str, ...] = (),  # noqa: N803 # NOSONAR
    ) -> None:
        """
        Initialize the column definition with its type metadata.

        Parameters
        ----------
        columnType : ColumnType
            Logical column type used by the SQL compiler.
        length : int or None, optional
            Maximum length for string-like columns.
        precision : int or None, optional
            Total digits for decimal columns.
        scale : int or None, optional
            Decimal digits for decimal columns.
        enumValues : tuple of str, optional
            Allowed values for enum columns.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Attribute name is attached later by the model metaclass.
        self.name: str = ""
        self.columnType = columnType  # NOSONAR
        self.length = length
        self.precision = precision
        self.scale = scale
        self.enumValues = enumValues  # NOSONAR
        self.isPrimary: bool = False  # NOSONAR
        self.isNullable: bool = False  # NOSONAR
        self.isUnique: bool = False  # NOSONAR
        self.hasIndex: bool = False  # NOSONAR
        self.isAutoIncrement: bool = False  # NOSONAR
        self.defaultValue: Any = _NO_DEFAULT  # NOSONAR
        self.foreignRef: ForeignReference | None = None  # NOSONAR

    # ── Fluent constraints ──────────────────────────────────────────────────

    def primary(self) -> ColumnDefinition:
        """
        Mark the column as the primary key of the table.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.isPrimary = True  # NOSONAR
        return self

    def nullable(self) -> ColumnDefinition:
        """
        Allow the column to store ``NULL`` values.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.isNullable = True  # NOSONAR
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
        self.defaultValue = value  # NOSONAR
        return self

    def unique(self) -> ColumnDefinition:
        """
        Add a unique constraint to the column.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.isUnique = True  # NOSONAR
        return self

    def index(self) -> ColumnDefinition:
        """
        Create a non-unique index on the column.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.hasIndex = True  # NOSONAR
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
        self.foreignRef = ForeignReference.parse(reference)  # NOSONAR
        return self

    def autoIncrement(self) -> ColumnDefinition:
        """
        Mark the column as auto-incrementing.

        Returns
        -------
        ColumnDefinition
            The same definition, enabling fluent chaining.
        """
        self.isAutoIncrement = True  # NOSONAR
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
        return self.defaultValue is not _NO_DEFAULT

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
            f"type={self.columnType!s}>"
        )
