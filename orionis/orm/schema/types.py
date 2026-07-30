from __future__ import annotations
from enum import StrEnum
from orionis.orm.schema.column import ColumnDefinition, ColumnOptions

# Default maximum length applied to VARCHAR-like columns.
_DEFAULT_STRING_LENGTH: int = 255

# Default precision and scale applied to decimal columns.
_DEFAULT_DECIMAL_PRECISION: int = 10
_DEFAULT_DECIMAL_SCALE: int = 2

class ColumnType(StrEnum):
    """
    Logical column types understood by the Orionis SQL compiler.

    Each member is mapped internally to the corresponding engine type by
    the database layer; models never interact with SQL types directly.
    """

    # Generic Types
    BIG_INTEGER = "big_integer"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    DOUBLE = "double"
    ENUM = "enum"
    FLOAT = "float"
    INTEGER = "integer"
    INTERVAL = "interval"
    LARGE_BINARY = "large_binary"
    MATCH_TYPE = "match_type"
    NUMERIC = "numeric"
    NUMERIC_COMMON = "numeric_common"
    PICKLE_TYPE = "pickle_type"
    SCHEMA_TYPE = "schema_type"
    SMALL_INTEGER = "small_integer"
    STRING = "string"
    TEXT = "text"
    TIME = "time"
    UNICODE = "unicode"
    UNICODE_TEXT = "unicode_text"
    UUID = "uuid"

    # Specific Types
    ARRAY = "array"
    BIGINT = "bigint"
    BINARY = "binary"
    BLOB = "blob"
    CHAR = "char"
    CLOB = "clob"
    DECIMAL = "decimal"
    DOUBLE_PRECISION = "double_precision"
    INT = "int"
    JSON = "json"
    NCHAR = "nchar"
    NVARCHAR = "nvarchar"
    REAL = "real"
    SMALLINT = "smallint"
    TIMESTAMP = "timestamp"
    VARBINARY = "varbinary"
    VARCHAR = "varchar"

# ─────────────────────────────────────────────────────────────────────────────
# Generic "CamelCase" Types
#
# Database-agnostic types. SQLAlchemy chooses the best matching engine type
# for the target backend when compiling DDL.
# ─────────────────────────────────────────────────────────────────────────────

class BigInteger(ColumnDefinition):
    """A type for bigger ``int`` integers. Typically generates ``BIGINT``."""

    def __init__(self) -> None:
        """
        Initialize a big integer column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.BIG_INTEGER)

class Boolean(ColumnDefinition):
    """A bool datatype, typically ``BOOLEAN`` or ``SMALLINT`` in DDL."""

    def __init__(
        self,
        *,
        create_constraint: bool = False,
        name: str | None = None,
    ) -> None:
        """
        Construct a Boolean.

        Parameters
        ----------
        create_constraint : bool, optional
            When the boolean is emulated as int/smallint, also create a
            CHECK constraint ensuring 1 or 0 as a value.
        name : str or None, optional
            Name of the CHECK constraint, when generated.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.BOOLEAN,
            ColumnOptions(create_constraint=create_constraint, constraint_name=name),
        )

class Date(ColumnDefinition):
    """A type for ``datetime.date()`` objects."""

    def __init__(self) -> None:
        """
        Initialize a date column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.DATE)

class DateTime(ColumnDefinition):
    """A type for ``datetime.datetime()`` objects."""

    def __init__(self, *, timezone: bool = False) -> None:
        """
        Construct a new DateTime.

        Parameters
        ----------
        timezone : bool, optional
            Whether the datetime type should enable timezone support, if
            available on the base date/time-holding type.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.DATETIME, ColumnOptions(timezone=timezone))

class Double(ColumnDefinition):
    """A type for double ``FLOAT``. Typically generates ``DOUBLE``."""

    def __init__(
        self,
        precision: int | None = None,
        *,
        asdecimal: bool = False,
        decimal_return_scale: int | None = None,
    ) -> None:
        """
        Construct a Double.

        Parameters
        ----------
        precision : int or None, optional
            Numeric precision for use in DDL ``CREATE TABLE``.
        asdecimal : bool, optional
            Whether values are coerced to ``decimal.Decimal``.
        decimal_return_scale : int or None, optional
            Default scale used when converting floats to decimals.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.DOUBLE,
            ColumnOptions(
                precision=precision,
                as_decimal=asdecimal,
                decimal_return_scale=decimal_return_scale,
            ),
        )

class Enum(ColumnDefinition):
    """String-backed enumeration column."""

    def __init__(
        self,
        *enums: str,
        name: str | None = None,
        create_constraint: bool = False,
        native_enum: bool = True,
        length: int | None = None,
        validate_strings: bool = False,
    ) -> None:
        """
        Construct an enum.

        Parameters
        ----------
        *enums : str
            Allowed string values, at least one is required.
        name : str or None, optional
            Name of the enumerated database type.
        create_constraint : bool, optional
            When emulating a non-native enum, also build a CHECK
            constraint against the allowed values.
        native_enum : bool, optional
            Whether to use the backend's native ``ENUM`` type.
        length : int or None, optional
            Custom ``VARCHAR`` length for non-native enumerations.
        validate_strings : bool, optional
            Whether to validate string literals against allowed values.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If no values are provided or any value is not a string.
        """
        # Enum columns are meaningless without at least one allowed value.
        if not enums or any(not isinstance(v, str) or not v for v in enums):
            error_msg = "Enum requires at least one non-empty string value."
            raise ValueError(error_msg)
        super().__init__(
            ColumnType.ENUM,
            ColumnOptions(
                enum_values=tuple(enums),
                enum_name=name,
                create_constraint=create_constraint,
                native_enum=native_enum,
                length=length,
                validate_strings=validate_strings,
            ),
        )

class Float(ColumnDefinition):
    """Type representing floating point types, such as ``FLOAT`` or ``REAL``."""

    def __init__(
        self,
        precision: int | None = None,
        *,
        asdecimal: bool = False,
        decimal_return_scale: int | None = None,
    ) -> None:
        """
        Construct a Float.

        Parameters
        ----------
        precision : int or None, optional
            Numeric precision for use in DDL ``CREATE TABLE``.
        asdecimal : bool, optional
            Whether values are coerced to ``decimal.Decimal``.
        decimal_return_scale : int or None, optional
            Default scale used when converting floats to decimals.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.FLOAT,
            ColumnOptions(
                precision=precision,
                as_decimal=asdecimal,
                decimal_return_scale=decimal_return_scale,
            ),
        )

class Integer(ColumnDefinition):
    """A type for ``int`` integers."""

    def __init__(self) -> None:
        """
        Initialize an integer column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.INTEGER)

class Interval(ColumnDefinition):
    """A type for ``datetime.timedelta()`` objects."""

    def __init__(
        self,
        *,
        native: bool = True,
        second_precision: int | None = None,
        day_precision: int | None = None,
    ) -> None:
        """
        Construct an Interval object.

        Parameters
        ----------
        native : bool, optional
            Whether to use the backend's native ``INTERVAL`` type, when
            supported (PostgreSQL, Oracle Database).
        second_precision : int or None, optional
            Fractional seconds precision for native interval types.
        day_precision : int or None, optional
            Day precision for native interval types.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.INTERVAL,
            ColumnOptions(
                native=native,
                second_precision=second_precision,
                day_precision=day_precision,
            ),
        )

class LargeBinary(ColumnDefinition):
    """A type for large binary byte data, such as ``BLOB``/``BYTEA``."""

    def __init__(self, length: int | None = None) -> None:
        """
        Construct a LargeBinary type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL statements, for those
            binary types that accept a length.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If the length is not a positive integer or None.
        """
        if length is not None and (not isinstance(length, int) or length <= 0):
            error_msg = "LargeBinary length must be a positive integer or None."
            raise ValueError(error_msg)
        super().__init__(ColumnType.LARGE_BINARY, ColumnOptions(length=length))

class MatchType(ColumnDefinition):
    """Refers to the return type of the ``MATCH`` operator."""

    def __init__(self) -> None:
        """
        Initialize a match type column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.MATCH_TYPE)

class Numeric(ColumnDefinition):
    """Base for non-integer numeric types, such as ``NUMERIC``/``DECIMAL``."""

    def __init__(
        self,
        precision: int | None = None,
        scale: int | None = None,
        decimal_return_scale: int | None = None,
        *,
        asdecimal: bool = True,
    ) -> None:
        """
        Construct a Numeric.

        Parameters
        ----------
        precision : int or None, optional
            Numeric precision for use in DDL ``CREATE TABLE``.
        scale : int or None, optional
            Numeric scale for use in DDL ``CREATE TABLE``.
        decimal_return_scale : int or None, optional
            Default scale used when converting floats to decimals.
        asdecimal : bool, optional
            Whether values are returned as ``decimal.Decimal`` objects.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If precision or scale are negative or inconsistent.
        """
        # Validate the numeric shape early to fail fast at class definition.
        if precision is not None or scale is not None:
            valid_types = isinstance(precision, int) and isinstance(scale, int)
            if not valid_types or precision <= 0 or scale < 0 or scale > precision:
                error_msg = (
                    "Numeric requires a positive precision and a non-negative "
                    "scale not greater than the precision."
                )
                raise ValueError(error_msg)
        super().__init__(
            ColumnType.NUMERIC,
            ColumnOptions(
                precision=precision,
                scale=scale,
                decimal_return_scale=decimal_return_scale,
                as_decimal=asdecimal,
            ),
        )

class NumericCommon(ColumnDefinition):
    """Common mixin placeholder shared by :class:`Numeric` and :class:`Float`."""

    def __init__(self) -> None:
        """
        Initialize the numeric-common placeholder definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.NUMERIC_COMMON)

class PickleType(ColumnDefinition):
    """Holds Python objects, serialized using ``pickle``."""

    def __init__(
        self,
        protocol: int = 5,
        pickler: object | None = None,
        impl: object | None = None,
    ) -> None:
        """
        Construct a PickleType.

        Parameters
        ----------
        protocol : int, optional
            Pickle protocol, defaults to ``pickle.HIGHEST_PROTOCOL``.
        pickler : object or None, optional
            Object exposing pickle-compatible ``dumps``/``loads`` methods.
        impl : object or None, optional
            Binary-storing type used in place of the default ``LargeBinary``.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.PICKLE_TYPE,
            ColumnOptions(protocol=protocol, pickler=pickler, impl=impl),
        )

class SchemaType(ColumnDefinition):
    """Adds schema-level DDL, mixed into :class:`Boolean`/:class:`Enum`."""

    def __init__(self, name: str | None = None) -> None:
        """
        Initialize the schema-type placeholder definition.

        Parameters
        ----------
        name : str or None, optional
            Name of the associated schema-level construct.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.SCHEMA_TYPE, ColumnOptions(constraint_name=name))

class SmallInteger(ColumnDefinition):
    """A type for smaller ``int`` integers. Typically generates ``SMALLINT``."""

    def __init__(self) -> None:
        """
        Initialize a small integer column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.SMALL_INTEGER)

class String(ColumnDefinition):
    """The base for all string and character types. In SQL, ``VARCHAR``."""

    def __init__(
        self,
        length: int | None = _DEFAULT_STRING_LENGTH,
        collation: str | None = None,
    ) -> None:
        """
        Create a string-holding type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL and CAST expressions.
        collation : str or None, optional
            Column-level collation for use in DDL and CAST expressions.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If the length is not a positive integer or None.
        """
        if length is not None and (not isinstance(length, int) or length <= 0):
            error_msg = "String length must be a positive integer or None."
            raise ValueError(error_msg)
        super().__init__(
            ColumnType.STRING,
            ColumnOptions(length=length, collation=collation),
        )

class Text(ColumnDefinition):
    """A variably sized string type. In SQL, usually ``CLOB``/``TEXT``."""

    def __init__(
        self,
        length: int | None = None,
        collation: str | None = None,
    ) -> None:
        """
        Create a string-holding type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL and CAST expressions.
        collation : str or None, optional
            Column-level collation for use in DDL and CAST expressions.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.TEXT,
            ColumnOptions(length=length, collation=collation),
        )

class Time(ColumnDefinition):
    """A type for ``datetime.time()`` objects."""

    def __init__(self) -> None:
        """
        Initialize a time column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.TIME)

class Unicode(ColumnDefinition):
    """A variable length Unicode string type, e.g. ``NVARCHAR``."""

    def __init__(
        self,
        length: int | None = None,
        collation: str | None = None,
    ) -> None:
        """
        Create a string-holding type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL and CAST expressions.
        collation : str or None, optional
            Column-level collation for use in DDL and CAST expressions.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.UNICODE,
            ColumnOptions(length=length, collation=collation),
        )

class UnicodeText(ColumnDefinition):
    """An unbounded-length Unicode string type, e.g. ``NCLOB``/``NTEXT``."""

    def __init__(
        self,
        length: int | None = None,
        collation: str | None = None,
    ) -> None:
        """
        Create a string-holding type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL and CAST expressions.
        collation : str or None, optional
            Column-level collation for use in DDL and CAST expressions.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.UNICODE_TEXT,
            ColumnOptions(length=length, collation=collation),
        )

class Uuid(ColumnDefinition):
    """Represent a database agnostic UUID datatype."""

    def __init__(
        self,
        *,
        as_uuid: bool = True,
        native_uuid: bool = True,
    ) -> None:
        """
        Construct a Uuid type.

        Parameters
        ----------
        as_uuid : bool, optional
            Whether values are interpreted as Python ``uuid.UUID`` objects.
        native_uuid : bool, optional
            Whether to use the backend's native UUID-storing type.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.UUID,
            ColumnOptions(as_uuid=as_uuid, native_uuid=native_uuid),
        )


# ─────────────────────────────────────────────────────────────────────────────
# SQL Standard and Multiple Vendor "UPPERCASE" Types
#
# Exact SQL types that always render their name regardless of backend
# support. Prefixed with "Strict" to keep them distinguishable from the
# database-agnostic generic types above.
# ─────────────────────────────────────────────────────────────────────────────

class StrictArray(ColumnDefinition):
    """Represent a SQL ``ARRAY`` type."""

    def __init__(
        self,
        item_type: ColumnDefinition,
        *,
        as_tuple: bool = False,
        dimensions: int | None = None,
        zero_indexes: bool = False,
    ) -> None:
        """
        Construct an ARRAY.

        Parameters
        ----------
        item_type : ColumnDefinition
            Column definition of the array elements.
        as_tuple : bool, optional
            Whether results are converted to tuples instead of lists.
        dimensions : int or None, optional
            Fixed number of dimensions, when not ``None``.
        zero_indexes : bool, optional
            Whether to convert between zero- and one-based indexes.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.ARRAY,
            ColumnOptions(
                item_type=item_type,
                as_tuple=as_tuple,
                dimensions=dimensions,
                zero_indexes=zero_indexes,
            ),
        )

class StrictBigInt(ColumnDefinition):
    """The SQL ``BIGINT`` type."""

    def __init__(self) -> None:
        """
        Initialize a BIGINT column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.BIGINT)

class StrictBinary(ColumnDefinition):
    """The SQL ``BINARY`` type."""

    def __init__(self, length: int | None = None) -> None:
        """
        Construct a BINARY type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL statements.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.BINARY, ColumnOptions(length=length))

class StrictBlob(ColumnDefinition):
    """The SQL ``BLOB`` type."""

    def __init__(self, length: int | None = None) -> None:
        """
        Construct a LargeBinary type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL statements.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.BLOB, ColumnOptions(length=length))

class StrictChar(ColumnDefinition):
    """The SQL ``CHAR`` type."""

    def __init__(
        self,
        length: int | None = None,
        collation: str | None = None,
    ) -> None:
        """
        Create a string-holding type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL and CAST expressions.
        collation : str or None, optional
            Column-level collation for use in DDL and CAST expressions.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.CHAR,
            ColumnOptions(length=length, collation=collation),
        )

class StrictClob(ColumnDefinition):
    """The ``CLOB`` type, found in Oracle Database and Informix."""

    def __init__(
        self,
        length: int | None = None,
        collation: str | None = None,
    ) -> None:
        """
        Create a string-holding type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL and CAST expressions.
        collation : str or None, optional
            Column-level collation for use in DDL and CAST expressions.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.CLOB,
            ColumnOptions(length=length, collation=collation),
        )

class StrictDecimal(ColumnDefinition):
    """The SQL ``DECIMAL`` type."""

    def __init__(
        self,
        precision: int | None = _DEFAULT_DECIMAL_PRECISION,
        scale: int | None = _DEFAULT_DECIMAL_SCALE,
        decimal_return_scale: int | None = None,
        *,
        asdecimal: bool = True,
    ) -> None:
        """
        Construct a Numeric.

        Parameters
        ----------
        precision : int or None, optional
            Numeric precision for use in DDL ``CREATE TABLE``.
        scale : int or None, optional
            Numeric scale for use in DDL ``CREATE TABLE``.
        decimal_return_scale : int or None, optional
            Default scale used when converting floats to decimals.
        asdecimal : bool, optional
            Whether values are returned as ``decimal.Decimal`` objects.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If precision or scale are negative or inconsistent.
        """
        if precision is not None or scale is not None:
            valid_types = isinstance(precision, int) and isinstance(scale, int)
            if not valid_types or precision <= 0 or scale < 0 or scale > precision:
                error_msg = (
                    "StrictDecimal requires a positive precision and a "
                    "non-negative scale not greater than the precision."
                )
                raise ValueError(error_msg)
        super().__init__(
            ColumnType.DECIMAL,
            ColumnOptions(
                precision=precision,
                scale=scale,
                decimal_return_scale=decimal_return_scale,
                as_decimal=asdecimal,
            ),
        )

class StrictDoublePrecision(ColumnDefinition):
    """The SQL ``DOUBLE PRECISION`` type."""

    def __init__(
        self,
        precision: int | None = None,
        *,
        asdecimal: bool = False,
        decimal_return_scale: int | None = None,
    ) -> None:
        """
        Construct a Float.

        Parameters
        ----------
        precision : int or None, optional
            Numeric precision for use in DDL ``CREATE TABLE``.
        asdecimal : bool, optional
            Whether values are coerced to ``decimal.Decimal``.
        decimal_return_scale : int or None, optional
            Default scale used when converting floats to decimals.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.DOUBLE_PRECISION,
            ColumnOptions(
                precision=precision,
                as_decimal=asdecimal,
                decimal_return_scale=decimal_return_scale,
            ),
        )

class StrictInt(ColumnDefinition):
    """Alias of ``INTEGER``."""

    def __init__(self) -> None:
        """
        Initialize an INT column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.INT)

class StrictJson(ColumnDefinition):
    """Represent a SQL ``JSON`` type."""

    def __init__(self, *, none_as_null: bool = False) -> None:
        """
        Construct a JSON type.

        Parameters
        ----------
        none_as_null : bool, optional
            When ``True``, persist Python ``None`` as SQL ``NULL`` instead
            of the JSON encoding of ``null``.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.JSON, ColumnOptions(none_as_null=none_as_null))

class StrictNChar(ColumnDefinition):
    """The SQL ``NCHAR`` type."""

    def __init__(
        self,
        length: int | None = None,
        collation: str | None = None,
    ) -> None:
        """
        Create a string-holding type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL and CAST expressions.
        collation : str or None, optional
            Column-level collation for use in DDL and CAST expressions.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.NCHAR,
            ColumnOptions(length=length, collation=collation),
        )

class StrictNVarChar(ColumnDefinition):
    """The SQL ``NVARCHAR`` type."""

    def __init__(
        self,
        length: int | None = None,
        collation: str | None = None,
    ) -> None:
        """
        Create a string-holding type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL and CAST expressions.
        collation : str or None, optional
            Column-level collation for use in DDL and CAST expressions.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.NVARCHAR,
            ColumnOptions(length=length, collation=collation),
        )

class StrictReal(ColumnDefinition):
    """The SQL ``REAL`` type."""

    def __init__(
        self,
        precision: int | None = None,
        *,
        asdecimal: bool = False,
        decimal_return_scale: int | None = None,
    ) -> None:
        """
        Construct a Float.

        Parameters
        ----------
        precision : int or None, optional
            Numeric precision for use in DDL ``CREATE TABLE``.
        asdecimal : bool, optional
            Whether values are coerced to ``decimal.Decimal``.
        decimal_return_scale : int or None, optional
            Default scale used when converting floats to decimals.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.REAL,
            ColumnOptions(
                precision=precision,
                as_decimal=asdecimal,
                decimal_return_scale=decimal_return_scale,
            ),
        )

class StrictSmallInt(ColumnDefinition):
    """The SQL ``SMALLINT`` type."""

    def __init__(self) -> None:
        """
        Initialize a SMALLINT column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.SMALLINT)

class StrictTimestamp(ColumnDefinition):
    """The SQL ``TIMESTAMP`` type."""

    def __init__(self, *, timezone: bool = False) -> None:
        """
        Construct a new TIMESTAMP.

        Parameters
        ----------
        timezone : bool, optional
            Whether the TIMESTAMP type should enable timezone support,
            if available on the target database.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.TIMESTAMP, ColumnOptions(timezone=timezone))

class StrictVarBinary(ColumnDefinition):
    """The SQL ``VARBINARY`` type."""

    def __init__(self, length: int | None = None) -> None:
        """
        Construct a VARBINARY type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL statements.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.VARBINARY, ColumnOptions(length=length))

class StrictVarChar(ColumnDefinition):
    """The SQL ``VARCHAR`` type."""

    def __init__(
        self,
        length: int | None = _DEFAULT_STRING_LENGTH,
        collation: str | None = None,
    ) -> None:
        """
        Create a string-holding type.

        Parameters
        ----------
        length : int or None, optional
            Length for the column for use in DDL and CAST expressions.
        collation : str or None, optional
            Column-level collation for use in DDL and CAST expressions.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(
            ColumnType.VARCHAR,
            ColumnOptions(length=length, collation=collation),
        )
