from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable
    from orionis.database.entities.result import InsertResult
    from orionis.orm.schema.table import TableDefinition
    from orionis.support.types.collection import Collection

class IRawQueryBuilder(ABC):
    """
    Contract for the fluent, model-less query builder over a table name.

    Fluent methods return the builder itself for chaining; terminal
    methods execute the accumulated query against the resolved
    connection and return plain dictionaries instead of model instances.
    """

    # ── Projection ───────────────────────────────────────────────────────────

    @abstractmethod
    def select(self, *columns: str) -> IRawQueryBuilder:
        """
        Restrict the query projection to the given columns.

        Parameters
        ----------
        *columns : str
            Column names to project; empty selects every column.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def distinct(self) -> IRawQueryBuilder:
        """
        Collapse duplicate rows from the query results.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    # ── Where clauses ────────────────────────────────────────────────────────

    @abstractmethod
    def where(
        self,
        column: str | dict[str, Any],
        *args: Any,  # noqa: ANN401
    ) -> IRawQueryBuilder:
        """
        Add an AND-combined filtering condition.

        Parameters
        ----------
        column : str or dict
            Column name, or a mapping of column/value equality pairs.
        *args : Any
            Either the bound value, or an operator followed by a value.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def orWhere(
        self,
        column: str | dict[str, Any],
        *args: Any,  # noqa: ANN401
    ) -> IRawQueryBuilder:
        """
        Add an OR-combined filtering condition.

        Parameters
        ----------
        column : str or dict
            Column name, or a mapping of column/value equality pairs.
        *args : Any
            Either the bound value, or an operator followed by a value.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereIn(self, column: str, values: Iterable[Any]) -> IRawQueryBuilder:
        """
        Filter rows whose column value belongs to the given set.

        Parameters
        ----------
        column : str
            Column name to filter by.
        values : Iterable
            Accepted values.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereNotIn(self, column: str, values: Iterable[Any]) -> IRawQueryBuilder:
        """
        Filter rows whose column value is outside the given set.

        Parameters
        ----------
        column : str
            Column name to filter by.
        values : Iterable
            Rejected values.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereNull(self, column: str) -> IRawQueryBuilder:
        """
        Filter rows whose column value is ``NULL``.

        Parameters
        ----------
        column : str
            Column name to filter by.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereNotNull(self, column: str) -> IRawQueryBuilder:
        """
        Filter rows whose column value is not ``NULL``.

        Parameters
        ----------
        column : str
            Column name to filter by.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    # ── Joins ────────────────────────────────────────────────────────────────

    @abstractmethod
    def join(
        self,
        table: str | TableDefinition,
        first: str,
        operator: str,
        second: str,
        *,
        alias: str | None = None,
    ) -> IRawQueryBuilder:
        """
        Add an INNER JOIN to the query.

        Parameters
        ----------
        table : str or TableDefinition
            Table name to join, or its full definition when it declares
            a real schema (for instance ``Model.__meta__.table``).
        first : str
            Left-hand column of the ON condition.
        operator : str
            Comparison operator relating both sides.
        second : str
            Right-hand column of the ON condition.
        alias : str or None, optional
            Alias the joined table is referred to by inside the query.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def leftJoin(
        self,
        table: str | TableDefinition,
        first: str,
        operator: str,
        second: str,
        *,
        alias: str | None = None,
    ) -> IRawQueryBuilder:
        """
        Add a LEFT OUTER JOIN to the query.

        Parameters
        ----------
        table : str or TableDefinition
            Table name to join, or its full definition.
        first : str
            Left-hand column of the ON condition.
        operator : str
            Comparison operator relating both sides.
        second : str
            Right-hand column of the ON condition.
        alias : str or None, optional
            Alias the joined table is referred to by inside the query.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def crossJoin(
        self,
        table: str | TableDefinition,
        *,
        alias: str | None = None,
    ) -> IRawQueryBuilder:
        """
        Add a CROSS JOIN to the query.

        Parameters
        ----------
        table : str or TableDefinition
            Table name to join, or its full definition.
        alias : str or None, optional
            Alias the joined table is referred to by inside the query.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    # ── Ordering, grouping, pagination ──────────────────────────────────────

    @abstractmethod
    def orderBy(self, column: str, direction: str = "asc") -> IRawQueryBuilder:
        """
        Add an ordering rule to the query.

        Parameters
        ----------
        column : str
            Column to sort by.
        direction : str, optional
            ``"asc"`` or ``"desc"``.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def groupBy(self, *columns: str) -> IRawQueryBuilder:
        """
        Add grouping columns to the query.

        Parameters
        ----------
        *columns : str
            Columns to group by.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def having(
        self,
        column: str,
        *args: Any,  # noqa: ANN401
    ) -> IRawQueryBuilder:
        """
        Add a post-grouping condition to the query.

        Parameters
        ----------
        column : str
            Column name the condition applies to.
        *args : Any
            Either the bound value, or an operator followed by a value.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def limit(self, value: int) -> IRawQueryBuilder:
        """
        Limit the number of rows returned by the query.

        Parameters
        ----------
        value : int
            Maximum number of rows, must not be negative.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def offset(self, value: int) -> IRawQueryBuilder:
        """
        Skip the given number of rows.

        Parameters
        ----------
        value : int
            Number of rows to skip, must not be negative.

        Returns
        -------
        IRawQueryBuilder
            The same builder, enabling fluent chaining.
        """

    # ── Retrieval terminals ──────────────────────────────────────────────────

    @abstractmethod
    async def get(self) -> Collection:
        """
        Execute the query and return every matching row.

        Returns
        -------
        Collection
            Collection of plain dictionaries, one per row.
        """

    @abstractmethod
    async def first(self) -> dict[str, Any] | None:
        """
        Execute the query and return only the first matching row.

        Returns
        -------
        dict or None
            First matching row, or ``None`` without matches.
        """

    @abstractmethod
    async def count(self) -> int:
        """
        Count the rows matched by the query.

        Returns
        -------
        int
            Number of matching rows.
        """

    # ── Mutation terminals ───────────────────────────────────────────────────

    @abstractmethod
    async def insert(
        self,
        values: dict[str, Any] | list[dict[str, Any]],
    ) -> InsertResult:
        """
        Insert one or many rows into the table.

        Parameters
        ----------
        values : dict or list of dict
            Column values for one row, or a list of rows.

        Returns
        -------
        InsertResult
            Result carrying the generated key and affected row count.
        """

    @abstractmethod
    async def update(self, values: dict[str, Any]) -> int:
        """
        Mass update the rows matched by the query.

        Parameters
        ----------
        values : dict
            Column values to assign.

        Returns
        -------
        int
            Number of affected rows.
        """

    @abstractmethod
    async def delete(self) -> int:
        """
        Delete the rows matched by the query.

        Returns
        -------
        int
            Number of affected rows.
        """
