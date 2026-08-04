from __future__ import annotations
from typing import TYPE_CHECKING, Any
from orionis.orm.contracts.raw_builder import IRawQueryBuilder
from orionis.orm.exceptions import InvalidQueryException
from orionis.orm.query.expressions import (
    SUPPORTED_OPERATORS,
    AggregateClause,
    AggregateFunction,
    DeletePlan,
    InsertPlan,
    JoinCondition,
    JoinExpression,
    JoinType,
    OrderClause,
    SelectPlan,
    SortDirection,
    UpdatePlan,
    WhereClause,
    WhereType,
)
from orionis.orm.resolver import ConnectionResolver
from orionis.orm.schema.table import TableDefinition
from orionis.support.types.collection import Collection

if TYPE_CHECKING:
    from collections.abc import Iterable
    from orionis.database.contracts.connection import IConnection
    from orionis.database.entities.result import InsertResult

# Number of arguments in the (operator, value) where form.
_WHERE_WITH_OPERATOR: int = 2

class RawQueryBuilder(IRawQueryBuilder):
    """
    Fluent, chainable query builder over a plain table name.

    Unlike :class:`orionis.orm.query.builder.ModelQueryBuilder`, it is not
    bound to a :class:`Model`: rows are returned as plain dictionaries
    and the underlying table carries no declared schema, so the SQL
    compiler declares each referenced column lazily. Built by
    :meth:`orionis.support.facades.db.DB.table`.

    This covers the most common fluent surface (where/join/order/group/
    having/limit/offset and the get/first/count/insert/update/delete
    terminals); it intentionally does not replicate every convenience
    method of :class:`ModelQueryBuilder` (``whereBetween``, ``whereLike``,
    pagination, and similar helpers) yet.
    """

    __slots__ = ("_connection_name", "_plan")

    def __init__(
        self,
        name: str,
        *,
        alias: str | None = None,
        connection: str | None = None,
    ) -> None:
        """
        Initialize the builder for a table reached only by its name.

        Parameters
        ----------
        name : str
            Logical table name, without the connection prefix.
        alias : str or None, optional
            Alias the table is referred to by inside the query.
        connection : str or None, optional
            Named connection to run the query against, or ``None`` for
            the default connection.

        Returns
        -------
        None
            This method does not return a value.
        """
        self._connection_name = connection
        self._plan = SelectPlan(table=TableDefinition(name=name), alias=alias)

    # ── Projection ───────────────────────────────────────────────────────────

    def select(self, *columns: str) -> RawQueryBuilder:
        """
        Restrict the query projection to the given columns.

        Parameters
        ----------
        *columns : str
            Column names to project; empty selects every column.

        Returns
        -------
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.columns = tuple(columns)
        return self

    def distinct(self) -> RawQueryBuilder:
        """
        Collapse duplicate rows from the query results.

        Returns
        -------
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.distinct = True
        return self

    # ── Where clauses ────────────────────────────────────────────────────────

    def where(
        self,
        column: str | dict[str, Any],
        *args: Any,  # noqa: ANN401
    ) -> RawQueryBuilder:
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
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._addWhere(self._plan.wheres, column, args, boolean="and")
        return self

    def orWhere(
        self,
        column: str | dict[str, Any],
        *args: Any,  # noqa: ANN401
    ) -> RawQueryBuilder:
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
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._addWhere(self._plan.wheres, column, args, boolean="or")
        return self

    def whereIn(self, column: str, values: Iterable[Any]) -> RawQueryBuilder:
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
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(column=column, where_type=WhereType.IN, value=tuple(values)),
        )
        return self

    def whereNotIn(self, column: str, values: Iterable[Any]) -> RawQueryBuilder:
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
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column, where_type=WhereType.NOT_IN, value=tuple(values),
            ),
        )
        return self

    def whereNull(self, column: str) -> RawQueryBuilder:
        """
        Filter rows whose column value is ``NULL``.

        Parameters
        ----------
        column : str
            Column name to filter by.

        Returns
        -------
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(WhereClause(column=column, where_type=WhereType.NULL))
        return self

    def whereNotNull(self, column: str) -> RawQueryBuilder:
        """
        Filter rows whose column value is not ``NULL``.

        Parameters
        ----------
        column : str
            Column name to filter by.

        Returns
        -------
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(column=column, where_type=WhereType.NOT_NULL),
        )
        return self

    # ── Joins ────────────────────────────────────────────────────────────────

    def join(
        self,
        table: str | TableDefinition,
        first: str,
        operator: str,
        second: str,
        *,
        alias: str | None = None,
    ) -> RawQueryBuilder:
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
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        condition = JoinCondition(first=first, operator=operator, second=second)
        self._plan.joins.append(
            JoinExpression(
                join_type=JoinType.INNER,
                table=self._resolveJoinTable(table),
                alias=alias,
                conditions=[condition],
            ),
        )
        return self

    def leftJoin(
        self,
        table: str | TableDefinition,
        first: str,
        operator: str,
        second: str,
        *,
        alias: str | None = None,
    ) -> RawQueryBuilder:
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
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        condition = JoinCondition(first=first, operator=operator, second=second)
        self._plan.joins.append(
            JoinExpression(
                join_type=JoinType.LEFT,
                table=self._resolveJoinTable(table),
                alias=alias,
                conditions=[condition],
            ),
        )
        return self

    def crossJoin(
        self,
        table: str | TableDefinition,
        *,
        alias: str | None = None,
    ) -> RawQueryBuilder:
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
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.joins.append(
            JoinExpression(
                join_type=JoinType.CROSS,
                table=self._resolveJoinTable(table),
                alias=alias,
            ),
        )
        return self

    @staticmethod
    def _resolveJoinTable(table: str | TableDefinition) -> TableDefinition:
        """
        Normalize a join target into a :class:`TableDefinition`.

        Parameters
        ----------
        table : str or TableDefinition
            Table name to join, or its full definition.

        Returns
        -------
        TableDefinition
            A schemaless definition for a bare name, or ``table`` as is.
        """
        if isinstance(table, str):
            return TableDefinition(name=table)
        return table

    # ── Ordering, grouping, pagination ──────────────────────────────────────

    def orderBy(self, column: str, direction: str = "asc") -> RawQueryBuilder:
        """
        Add an ordering rule to the query.

        Parameters
        ----------
        column : str
            Column to sort by.
        direction : str, optional
            ``"asc"`` or ``"desc"``. Defaults to ascending.

        Returns
        -------
        RawQueryBuilder
            The same builder, enabling fluent chaining.

        Raises
        ------
        InvalidQueryException
            If the direction is not ``"asc"`` or ``"desc"``.
        """
        normalized = str(direction).strip().lower()
        try:
            resolved = SortDirection(normalized)
        except ValueError as exc:
            error_msg = (
                f"Invalid sort direction '{direction}'; use 'asc' or 'desc'."
            )
            raise InvalidQueryException(error_msg) from exc
        self._plan.orders.append(OrderClause(column=column, direction=resolved))
        return self

    def groupBy(self, *columns: str) -> RawQueryBuilder:
        """
        Add grouping columns to the query.

        Parameters
        ----------
        *columns : str
            Columns to group by.

        Returns
        -------
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.groups.extend(columns)
        return self

    def having(
        self,
        column: str,
        *args: Any,  # noqa: ANN401
    ) -> RawQueryBuilder:
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
        RawQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._addWhere(self._plan.havings, column, args, boolean="and")
        return self

    def limit(self, value: int) -> RawQueryBuilder:
        """
        Limit the number of rows returned by the query.

        Parameters
        ----------
        value : int
            Maximum number of rows, must not be negative.

        Returns
        -------
        RawQueryBuilder
            The same builder, enabling fluent chaining.

        Raises
        ------
        InvalidQueryException
            If the value is negative.
        """
        if value < 0:
            error_msg = "limit() does not accept a negative value."
            raise InvalidQueryException(error_msg)
        self._plan.limit_value = value
        return self

    def offset(self, value: int) -> RawQueryBuilder:
        """
        Skip the given number of rows.

        Parameters
        ----------
        value : int
            Number of rows to skip, must not be negative.

        Returns
        -------
        RawQueryBuilder
            The same builder, enabling fluent chaining.

        Raises
        ------
        InvalidQueryException
            If the value is negative.
        """
        if value < 0:
            error_msg = "offset() does not accept a negative value."
            raise InvalidQueryException(error_msg)
        self._plan.offset_value = value
        return self

    # ── Retrieval terminals ──────────────────────────────────────────────────

    async def get(self) -> Collection:
        """
        Execute the query and return every matching row.

        Returns
        -------
        Collection
            Collection of plain dictionaries, one per row.

        Raises
        ------
        QueryException
            If the statement fails to compile or execute.
        """
        rows = await self._connection().select(self._plan)
        return Collection(rows)

    async def first(self) -> dict[str, Any] | None:
        """
        Execute the query and return only the first matching row.

        Returns
        -------
        dict or None
            First matching row, or ``None`` without matches.

        Raises
        ------
        QueryException
            If the statement fails to compile or execute.
        """
        probe = self._plan.clone()
        probe.limit_value = 1
        rows = await self._connection().select(probe)
        return rows[0] if rows else None

    async def count(self) -> int:
        """
        Count the rows matched by the query.

        Returns
        -------
        int
            Number of matching rows.
        """
        probe = self._plan.clone()
        probe.aggregate = AggregateClause(function=AggregateFunction.COUNT, column="*")
        probe.limit_value = None
        probe.offset_value = None
        return int(await self._connection().scalar(probe) or 0)

    # ── Mutation terminals ───────────────────────────────────────────────────

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

        Raises
        ------
        InvalidQueryException
            If no values are provided.
        """
        rows = values if isinstance(values, list) else [values]
        if not rows:
            error_msg = "Cannot insert without values."
            raise InvalidQueryException(error_msg)
        plan = InsertPlan(table=self._plan.table, values=[dict(row) for row in rows])
        return await self._connection().insert(plan)

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

        Raises
        ------
        InvalidQueryException
            If no values are provided.
        """
        if not values:
            error_msg = "Cannot update without values."
            raise InvalidQueryException(error_msg)
        plan = UpdatePlan(
            table=self._plan.table,
            values=dict(values),
            wheres=list(self._plan.wheres),
        )
        return await self._connection().update(plan)

    async def delete(self) -> int:
        """
        Delete the rows matched by the query.

        Returns
        -------
        int
            Number of affected rows.
        """
        plan = DeletePlan(table=self._plan.table, wheres=list(self._plan.wheres))
        return await self._connection().delete(plan)

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _connection(self) -> IConnection:
        """
        Resolve the database connection this builder runs against.

        Returns
        -------
        IConnection
            Connection declared at construction time, or the default one.
        """
        return ConnectionResolver.connection(self._connection_name)

    def _addWhere(
        self,
        target: list[WhereClause],
        column: str | dict[str, Any],
        args: tuple[Any, ...],
        boolean: str,
    ) -> None:
        """
        Parse and append a basic condition to a clause list.

        Parameters
        ----------
        target : list of WhereClause
            Clause list receiving the condition.
        column : str or dict
            Column name, or a mapping of column/value equality pairs.
        args : tuple
            Either the bound value, or an operator followed by a value.
        boolean : str
            Logical connector with the previous clause.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        InvalidQueryException
            If the arguments do not match a supported form.
        """
        # Mapping form: a batch of equality conditions.
        if isinstance(column, dict):
            if args:
                error_msg = "Mapping conditions do not accept extra arguments."
                raise InvalidQueryException(error_msg)
            target.extend(
                WhereClause(column=key, value=value, boolean=boolean)
                for key, value in column.items()
            )
            return

        if len(args) == 1:
            target.append(
                WhereClause(column=column, value=args[0], boolean=boolean),
            )
            return

        if len(args) == _WHERE_WITH_OPERATOR:
            operator = str(args[0]).strip().lower()
            if operator not in SUPPORTED_OPERATORS:
                error_msg = f"Unsupported comparison operator '{args[0]}'."
                raise InvalidQueryException(error_msg)
            target.append(
                WhereClause(
                    column=column,
                    operator=operator,
                    value=args[1],
                    boolean=boolean,
                ),
            )
            return

        error_msg = "where() expects (column, value) or (column, operator, value)."
        raise InvalidQueryException(error_msg)
