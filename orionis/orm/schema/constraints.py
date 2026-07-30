from __future__ import annotations
from dataclasses import dataclass

# Number of segments expected in a qualified reference such as "companies.id".
_REFERENCE_PARTS: int = 2

@dataclass(frozen=True, slots=True)
class ForeignReference:
    """
    Immutable value object describing a foreign key reference.

    Attributes
    ----------
    table : str
        Name of the referenced table.
    column : str
        Name of the referenced column.
    """

    table: str
    column: str

    @classmethod
    def parse(cls, reference: str) -> ForeignReference:
        """
        Build a reference from a ``"table.column"`` qualified string.

        Parameters
        ----------
        reference : str
            Qualified reference in the form ``"table.column"``.

        Returns
        -------
        ForeignReference
            Parsed reference value object.

        Raises
        ------
        ValueError
            If the reference is not a non-empty ``"table.column"`` string.
        """
        # Split into exactly two non-empty segments.
        parts = reference.split(".") if isinstance(reference, str) else []
        if len(parts) != _REFERENCE_PARTS or not parts[0] or not parts[1]:
            error_msg = (
                f"Invalid foreign reference '{reference}'. "
                "Expected the 'table.column' format, e.g. 'companies.id'."
            )
            raise ValueError(error_msg)
        return cls(table=parts[0], column=parts[1])

    def qualified(self) -> str:
        """
        Return the reference in its qualified ``"table.column"`` form.

        Returns
        -------
        str
            Qualified reference string.
        """
        return f"{self.table}.{self.column}"


@dataclass(frozen=True, slots=True)
class UniqueConstraint:
    """
    Composite ``UNIQUE`` constraint spanning one or more columns.

    Attributes
    ----------
    columns : tuple of str
        Column names covered by the constraint, in declaration order.
    name : str or None
        Explicit constraint name, or ``None`` to let the engine assign one.
    """

    columns: tuple[str, ...]
    name: str | None = None


@dataclass(frozen=True, slots=True)
class TableIndex:
    """
    Composite index spanning one or more columns.

    Attributes
    ----------
    columns : tuple of str
        Column names covered by the index, in declaration order.
    name : str or None
        Explicit index name, or ``None`` to derive one from the table.
    unique : bool
        Whether the index also enforces uniqueness.
    """

    columns: tuple[str, ...]
    name: str | None = None
    unique: bool = False


@dataclass(frozen=True, slots=True)
class CompositeForeignKey:
    """
    Multi-column foreign key constraint.

    Attributes
    ----------
    columns : tuple of str
        Local column names, in the same order as ``ref_columns``.
    ref_table : str
        Name of the referenced table.
    ref_columns : tuple of str
        Referenced column names, aligned positionally with ``columns``.
    name : str or None
        Explicit constraint name, or ``None`` to let the engine assign one.
    """

    columns: tuple[str, ...]
    ref_table: str
    ref_columns: tuple[str, ...]
    name: str | None = None
