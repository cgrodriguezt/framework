# ruff: noqa: N815 (camelCase attributes are an Orionis convention)
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.orm.schema.column import ColumnDefinition


@dataclass(frozen=True, slots=True, eq=False)
class TableDefinition:
    """
    Framework-agnostic description of a database table.

    Built once per model by the metaclass and consumed by the database
    compiler to produce engine-specific SQL. It carries no reference to
    the underlying SQL toolkit.

    Attributes
    ----------
    name : str
        Logical table name without any connection prefix.
    columns : dict of str to ColumnDefinition
        Column definitions keyed by attribute name.
    primaryKey : str
        Name of the primary key column.
    """

    name: str
    columns: dict[str, ColumnDefinition] = field(default_factory=dict)
    primaryKey: str = "id"  # NOSONAR

    def columnNames(self) -> tuple[str, ...]:
        """
        Return the declared column names in definition order.

        Returns
        -------
        tuple of str
            Ordered column names.
        """
        return tuple(self.columns)

    def hasColumn(self, name: str) -> bool:
        """
        Report whether a column is declared on the table.

        Parameters
        ----------
        name : str
            Column name to look up.

        Returns
        -------
        bool
            ``True`` when the column exists in the definition.
        """
        return name in self.columns
