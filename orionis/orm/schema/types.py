from __future__ import annotations
from enum import StrEnum
from orionis.orm.schema.column import ColumnDefinition

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

    INTEGER = "integer"
    BIG_INTEGER = "big_integer"
    SMALL_INTEGER = "small_integer"
    STRING = "string"
    TEXT = "text"
    BOOLEAN = "boolean"
    FLOAT = "float"
    DECIMAL = "decimal"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    JSON = "json"
    UUID = "uuid"
    BINARY = "binary"
    ENUM = "enum"


class Integer(ColumnDefinition):
    """Standard 32-bit integer column."""

    def __init__(self) -> None:
        """
        Initialize an integer column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.INTEGER)


class BigInteger(ColumnDefinition):
    """64-bit integer column."""

    def __init__(self) -> None:
        """
        Initialize a big integer column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.BIG_INTEGER)


class SmallInteger(ColumnDefinition):
    """16-bit integer column."""

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
    """Variable-length string column."""

    def __init__(self, length: int = _DEFAULT_STRING_LENGTH) -> None:
        """
        Initialize a string column definition.

        Parameters
        ----------
        length : int, optional
            Maximum number of characters. Defaults to 255.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If the length is not a positive integer.
        """
        # Guard against invalid lengths before they reach the compiler.
        if not isinstance(length, int) or length <= 0:
            error_msg = "String length must be a positive integer."
            raise ValueError(error_msg)
        super().__init__(ColumnType.STRING, length=length)


class Text(ColumnDefinition):
    """Unbounded text column."""

    def __init__(self) -> None:
        """
        Initialize a text column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.TEXT)


class Boolean(ColumnDefinition):
    """Boolean column."""

    def __init__(self) -> None:
        """
        Initialize a boolean column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.BOOLEAN)


class Float(ColumnDefinition):
    """Floating point column."""

    def __init__(self) -> None:
        """
        Initialize a float column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.FLOAT)


class Decimal(ColumnDefinition):
    """Fixed precision decimal column."""

    def __init__(
        self,
        precision: int = _DEFAULT_DECIMAL_PRECISION,
        scale: int = _DEFAULT_DECIMAL_SCALE,
    ) -> None:
        """
        Initialize a decimal column definition.

        Parameters
        ----------
        precision : int, optional
            Total number of digits. Defaults to 10.
        scale : int, optional
            Number of decimal digits. Defaults to 2.

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
        valid_types = isinstance(precision, int) and isinstance(scale, int)
        if not valid_types or precision <= 0 or scale < 0 or scale > precision:
            error_msg = (
                "Decimal requires a positive precision and a non-negative "
                "scale not greater than the precision."
            )
            raise ValueError(error_msg)
        super().__init__(ColumnType.DECIMAL, precision=precision, scale=scale)


class Date(ColumnDefinition):
    """Calendar date column."""

    def __init__(self) -> None:
        """
        Initialize a date column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.DATE)


class Time(ColumnDefinition):
    """Time of day column."""

    def __init__(self) -> None:
        """
        Initialize a time column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.TIME)


class DateTime(ColumnDefinition):
    """Naive date and time column."""

    def __init__(self) -> None:
        """
        Initialize a datetime column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.DATETIME)


class Timestamp(ColumnDefinition):
    """Timezone-aware timestamp column."""

    def __init__(self) -> None:
        """
        Initialize a timestamp column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.TIMESTAMP)


class JSON(ColumnDefinition):
    """JSON document column."""

    def __init__(self) -> None:
        """
        Initialize a JSON column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.JSON)


class UUID(ColumnDefinition):
    """Universally unique identifier column."""

    def __init__(self) -> None:
        """
        Initialize a UUID column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.UUID)


class Binary(ColumnDefinition):
    """Raw binary column."""

    def __init__(self) -> None:
        """
        Initialize a binary column definition.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(ColumnType.BINARY)


class Enum(ColumnDefinition):
    """String-backed enumeration column."""

    def __init__(self, *values: str) -> None:
        """
        Initialize an enum column definition.

        Parameters
        ----------
        *values : str
            Allowed string values, at least one is required.

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
        if not values or any(not isinstance(v, str) or not v for v in values):
            error_msg = "Enum requires at least one non-empty string value."
            raise ValueError(error_msg)
        super().__init__(ColumnType.ENUM, enumValues=tuple(values))
