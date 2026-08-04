from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Any
from orionis.orm.attributes import serialize_for_storage
from orionis.orm.collections.paginator import Paginator
from orionis.orm.contracts.builder import IModelQueryBuilder
from orionis.orm.exceptions import InvalidQueryException, ModelNotFoundException
from orionis.orm.query.expressions import (
    SUPPORTED_OPERATORS,
    AggregateClause,
    AggregateFunction,
    DeletePlan,
    InsertPlan,
    OrderClause,
    SelectPlan,
    SortDirection,
    UpdatePlan,
    WhereClause,
    WhereType,
)
from orionis.orm.resolver import ConnectionResolver
from orionis.support.types.collection import Collection

if TYPE_CHECKING:
    from collections.abc import Iterable
    from orionis.database.contracts.connection import IConnection
    from orionis.database.entities.result import InsertResult
    from orionis.orm.model import Model

# Number of values required by a BETWEEN boundary pair.
_BETWEEN_BOUNDS: int = 2

# Number of arguments in the (operator, value) where form.
_WHERE_WITH_OPERATOR: int = 2

# Default page size used by pagination.
_DEFAULT_PER_PAGE: int = 15


class ModelQueryBuilder[TModel: "Model"](IModelQueryBuilder):
    """
    Fluent, chainable query builder bound to a model class.

    The builder accumulates an engine-agnostic :class:`SelectPlan` and
    delegates execution to the model connection, hydrating results into
    model instances wrapped in a :class:`Collection`.
    """

    __slots__ = ("_connection_name", "_meta", "_model", "_plan")

    def __init__(self, model: type[TModel]) -> None:
        """
        Initialize the builder for a model class.

        Parameters
        ----------
        model : type of Model
            Model class the queries run against.

        Returns
        -------
        None
            This method does not return a value.
        """
        meta = model.__meta__
        self._model = model
        self._meta = meta
        self._connection_name = meta.connection
        self._plan = SelectPlan(table=meta.table)

    # ── Projection ──────────────────────────────────────────────────────────

    def select(self, *columns: str) -> ModelQueryBuilder[TModel]:
        """
        Restrict the query projection to the given columns.

        Parameters
        ----------
        *columns : str
            Column names to project; empty selects every column.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.columns = tuple(columns)
        return self

    # ── Where clauses ───────────────────────────────────────────────────────

    def where(
        self,
        column: str | dict[str, Any],
        *args: Any,  # noqa: ANN401
    ) -> ModelQueryBuilder[TModel]:
        """
        Add an AND-combined filtering condition.

        Accepts ``where("col", value)``, ``where("col", op, value)``,
        or a mapping of equality conditions.

        Parameters
        ----------
        column : str or dict
            Column name, or a mapping of column/value equality pairs.
        *args : Any
            Either the bound value, or an operator followed by a value.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.

        Raises
        ------
        InvalidQueryException
            If the arguments do not match a supported form.
        """
        self._addWhere(self._plan.wheres, column, args, boolean="and")
        return self

    def orWhere(
        self,
        column: str | dict[str, Any],
        *args: Any,  # noqa: ANN401
    ) -> ModelQueryBuilder[TModel]:
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
        ModelQueryBuilder
            The same builder, enabling fluent chaining.

        Raises
        ------
        InvalidQueryException
            If the arguments do not match a supported form.
        """
        self._addWhere(self._plan.wheres, column, args, boolean="or")
        return self

    def whereIn(
        self,
        column: str,
        values: Iterable[Any],
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value belongs to the given set.

        Parameters
        ----------
        column : str
            Column name to filter by.
        values : Iterable
            Accepted values; collections are unwrapped automatically.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.IN,
                value=self._materializeValues(values),
            ),
        )
        return self

    def whereNotIn(
        self,
        column: str,
        values: Iterable[Any],
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value is outside the given set.

        Parameters
        ----------
        column : str
            Column name to filter by.
        values : Iterable
            Rejected values; collections are unwrapped automatically.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.NOT_IN,
                value=self._materializeValues(values),
            ),
        )
        return self

    def whereNull(self, column: str) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value is ``NULL``.

        Parameters
        ----------
        column : str
            Column name to filter by.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(column=column, where_type=WhereType.NULL),
        )
        return self

    def whereNotNull(self, column: str) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value is not ``NULL``.

        Parameters
        ----------
        column : str
            Column name to filter by.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(column=column, where_type=WhereType.NOT_NULL),
        )
        return self

    def whereBetween(
        self,
        column: str,
        bounds: Iterable[Any],
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value lies between two boundaries.

        Parameters
        ----------
        column : str
            Column name to filter by.
        bounds : Iterable
            Exactly two values: the lower and upper boundaries.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.

        Raises
        ------
        InvalidQueryException
            If the boundaries are not exactly two values.
        """
        values = tuple(bounds)
        if len(values) != _BETWEEN_BOUNDS:
            error_msg = "whereBetween requires exactly two boundary values."
            raise InvalidQueryException(error_msg)
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.BETWEEN,
                value=values,
            ),
        )
        return self

    def whereLike(
        self,
        column: str,
        pattern: str,
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value matches an SQL LIKE pattern.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            SQL LIKE pattern, using ``%`` and ``_`` wildcards.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.LIKE,
                value=pattern,
            ),
        )
        return self

    def whereNotLike(
        self,
        column: str,
        pattern: str,
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value does not match an SQL LIKE pattern.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            SQL LIKE pattern, using ``%`` and ``_`` wildcards.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.NOT_LIKE,
                value=pattern,
            ),
        )
        return self

    def whereILike(
        self,
        column: str,
        pattern: str,
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows matching a case-insensitive SQL LIKE pattern.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            SQL LIKE pattern, using ``%`` and ``_`` wildcards.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.ILIKE,
                value=pattern,
            ),
        )
        return self

    def whereNotILike(
        self,
        column: str,
        pattern: str,
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows not matching a case-insensitive SQL LIKE pattern.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            SQL LIKE pattern, using ``%`` and ``_`` wildcards.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.NOT_ILIKE,
                value=pattern,
            ),
        )
        return self

    def whereStartsWith(
        self,
        column: str,
        value: str,
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value starts with the given text.

        Parameters
        ----------
        column : str
            Column name to filter by.
        value : str
            Literal prefix to match.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.STARTS_WITH,
                value=value,
            ),
        )
        return self

    def whereEndsWith(
        self,
        column: str,
        value: str,
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value ends with the given text.

        Parameters
        ----------
        column : str
            Column name to filter by.
        value : str
            Literal suffix to match.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.ENDS_WITH,
                value=value,
            ),
        )
        return self

    def whereContains(
        self,
        column: str,
        value: str,
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value contains the given text.

        Parameters
        ----------
        column : str
            Column name to filter by.
        value : str
            Literal substring to match.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.CONTAINS,
                value=value,
            ),
        )
        return self

    def whereRegexpMatch(
        self,
        column: str,
        pattern: str,
    ) -> ModelQueryBuilder[TModel]:
        """
        Filter rows whose column value matches a regular expression.

        The exact regular expression dialect depends on the underlying
        database engine.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            Regular expression pattern.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.wheres.append(
            WhereClause(
                column=column,
                where_type=WhereType.REGEXP,
                value=pattern,
            ),
        )
        return self

    def distinct(self) -> ModelQueryBuilder[TModel]:
        """
        Collapse duplicate rows from the query results.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.distinct = True
        return self

    # ── Ordering, grouping, pagination ──────────────────────────────────────

    def orderBy(
        self,
        column: str,
        direction: str = "asc",
    ) -> ModelQueryBuilder[TModel]:
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
        ModelQueryBuilder
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
        self._plan.orders.append(
            OrderClause(column=column, direction=resolved),
        )
        return self

    def latest(self, column: str | None = None) -> ModelQueryBuilder[TModel]:
        """
        Order the query by a timestamp column in descending order.

        Parameters
        ----------
        column : str or None, optional
            Column to sort by; defaults to the creation timestamp when
            declared, or the primary key otherwise.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        target = column or self._meta.created_column or self._meta.primary_key
        return self.orderBy(target, "desc")

    def oldest(self, column: str | None = None) -> ModelQueryBuilder[TModel]:
        """
        Order the query by a timestamp column in ascending order.

        Parameters
        ----------
        column : str or None, optional
            Column to sort by; defaults to the creation timestamp when
            declared, or the primary key otherwise.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        target = column or self._meta.created_column or self._meta.primary_key
        return self.orderBy(target, "asc")

    def groupBy(self, *columns: str) -> ModelQueryBuilder[TModel]:
        """
        Add grouping columns to the query.

        Parameters
        ----------
        *columns : str
            Columns to group by.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        self._plan.groups.extend(columns)
        return self

    def having(
        self,
        column: str,
        *args: Any,  # noqa: ANN401
    ) -> ModelQueryBuilder[TModel]:
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
        ModelQueryBuilder
            The same builder, enabling fluent chaining.

        Raises
        ------
        InvalidQueryException
            If the arguments do not match a supported form.
        """
        self._addWhere(self._plan.havings, column, args, boolean="and")
        return self

    def limit(self, value: int) -> ModelQueryBuilder[TModel]:
        """
        Limit the number of rows returned by the query.

        Parameters
        ----------
        value : int
            Maximum number of rows, must not be negative.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.

        Raises
        ------
        InvalidQueryException
            If the value is negative.
        """
        if value < 0:
            error_msg = "Limit must not be negative."
            raise InvalidQueryException(error_msg)
        self._plan.limit_value = value
        return self

    def offset(self, value: int) -> ModelQueryBuilder[TModel]:
        """
        Skip the given number of rows before returning results.

        Parameters
        ----------
        value : int
            Number of rows to skip, must not be negative.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.

        Raises
        ------
        InvalidQueryException
            If the value is negative.
        """
        if value < 0:
            error_msg = "Offset must not be negative."
            raise InvalidQueryException(error_msg)
        self._plan.offset_value = value
        return self

    def take(self, value: int) -> ModelQueryBuilder[TModel]:
        """
        Limit the number of rows returned; alias of :meth:`limit`.

        Parameters
        ----------
        value : int
            Maximum number of rows, must not be negative.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        return self.limit(value)

    def skip(self, value: int) -> ModelQueryBuilder[TModel]:
        """
        Skip the given number of rows; alias of :meth:`offset`.

        Parameters
        ----------
        value : int
            Number of rows to skip, must not be negative.

        Returns
        -------
        ModelQueryBuilder
            The same builder, enabling fluent chaining.
        """
        return self.offset(value)

    # ── Retrieval terminals ─────────────────────────────────────────────────

    async def get(self) -> Collection:
        """
        Execute the query and hydrate every matching row.

        Returns
        -------
        Collection
            Collection of hydrated model instances.

        Raises
        ------
        QueryException
            If the statement fails to compile or execute.
        """
        rows = await self._connection().select(self._plan)
        hydrate = self._model._newFromDatabase  # noqa: SLF001
        return Collection([hydrate(row) for row in rows])

    async def first(self) -> TModel | None:
        """
        Execute the query and hydrate only the first matching row.

        Returns
        -------
        Model or None
            First matching model, or ``None`` without matches.

        Raises
        ------
        QueryException
            If the statement fails to compile or execute.
        """
        self._plan.limit_value = 1
        rows = await self._connection().select(self._plan)
        if not rows:
            return None
        return self._model._newFromDatabase(rows[0])  # noqa: SLF001

    async def firstOrFail(self) -> TModel:
        """
        Return the first matching row or raise when none exists.

        Returns
        -------
        Model
            First matching model.

        Raises
        ------
        ModelNotFoundException
            If the query yields no rows.
        """
        instance = await self.first()
        if instance is None:
            error_msg = (
                f"No records found for model [{self._model.__name__}]."
            )
            raise ModelNotFoundException(error_msg)
        return instance

    async def find(self, key: Any) -> TModel | None:  # noqa: ANN401
        """
        Retrieve a model by its primary key.

        Parameters
        ----------
        key : Any
            Primary key value to look up.

        Returns
        -------
        Model or None
            Matching model, or ``None`` when absent.
        """
        return await self.where(self._meta.primary_key, key).first()

    async def findOrFail(self, key: Any) -> TModel:  # noqa: ANN401
        """
        Retrieve a model by primary key or raise when absent.

        Parameters
        ----------
        key : Any
            Primary key value to look up.

        Returns
        -------
        Model
            Matching model.

        Raises
        ------
        ModelNotFoundException
            If no record matches the key.
        """
        instance = await self.find(key)
        if instance is None:
            error_msg = (
                f"No records found for model [{self._model.__name__}] "
                f"with key [{key}]."
            )
            raise ModelNotFoundException(error_msg)
        return instance

    async def paginate(
        self,
        page: int = 1,
        per_page: int = _DEFAULT_PER_PAGE,
    ) -> Paginator:
        """
        Execute the query returning a length-aware page of results.

        Parameters
        ----------
        page : int, optional
            Page number starting at 1. Defaults to the first page.
        per_page : int, optional
            Number of items per page. Defaults to 15.

        Returns
        -------
        Paginator
            Page of hydrated models with pagination metadata.

        Raises
        ------
        InvalidQueryException
            If the page or page size are not positive integers.
        """
        if page < 1 or per_page < 1:
            error_msg = "Page and per_page must be positive integers."
            raise InvalidQueryException(error_msg)

        self._plan.limit_value = per_page
        self._plan.offset_value = (page - 1) * per_page

        if self._connection().inTransaction():
            # A shared transactional connection cannot serve two
            # statements at once; run the count and the page in turn.
            total = int(await self._aggregate(AggregateFunction.COUNT, "*") or 0)
            items = await self.get()
        else:
            # Outside a transaction each query acquires its own pooled
            # connection, so the count and the page can run concurrently.
            count_result, items = await asyncio.gather(
                self._aggregate(AggregateFunction.COUNT, "*"),
                self.get(),
            )
            total = int(count_result or 0)

        return Paginator(items=items, total=total, page=page, per_page=per_page)

    # ── Aggregate terminals ─────────────────────────────────────────────────

    async def count(self) -> int:
        """
        Count the rows matched by the query.

        Returns
        -------
        int
            Number of matching rows.
        """
        return int(await self._aggregate(AggregateFunction.COUNT, "*") or 0)

    async def exists(self) -> bool:
        """
        Report whether the query matches at least one row.

        Returns
        -------
        bool
            ``True`` when a matching row exists.
        """
        probe = self._plan.clone()
        probe.columns = (self._meta.primary_key,)
        probe.limit_value = 1
        probe.offset_value = None
        rows = await self._connection().select(probe)
        return bool(rows)

    async def doesntExist(self) -> bool:
        """
        Report whether the query matches no rows.

        Returns
        -------
        bool
            ``True`` when no matching row exists.
        """
        return not await self.exists()

    async def max(self, column: str) -> Any:  # noqa: ANN401
        """
        Return the maximum value of a column among matching rows.

        Parameters
        ----------
        column : str
            Column to aggregate.

        Returns
        -------
        Any
            Maximum value, or ``None`` without matches.
        """
        return await self._aggregate(AggregateFunction.MAX, column)

    async def min(self, column: str) -> Any:  # noqa: ANN401
        """
        Return the minimum value of a column among matching rows.

        Parameters
        ----------
        column : str
            Column to aggregate.

        Returns
        -------
        Any
            Minimum value, or ``None`` without matches.
        """
        return await self._aggregate(AggregateFunction.MIN, column)

    async def avg(self, column: str) -> float | None:
        """
        Return the average value of a column among matching rows.

        Parameters
        ----------
        column : str
            Column to aggregate.

        Returns
        -------
        float or None
            Average value, or ``None`` without matches.
        """
        value = await self._aggregate(AggregateFunction.AVG, column)
        return float(value) if value is not None else None

    async def sum(self, column: str) -> Any:  # noqa: ANN401
        """
        Return the sum of a column among matching rows.

        Parameters
        ----------
        column : str
            Column to aggregate.

        Returns
        -------
        Any
            Sum of the values, or ``0`` without matches.
        """
        value = await self._aggregate(AggregateFunction.SUM, column)
        return value if value is not None else 0

    # ── Mutation terminals ──────────────────────────────────────────────────

    async def insert(
        self,
        values: dict[str, Any] | list[dict[str, Any]],
    ) -> InsertResult:
        """
        Insert one or many rows into the model table.

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

        serialized = [
            serialize_for_storage(self._meta, row) for row in rows
        ]
        plan = InsertPlan(table=self._meta.table, values=serialized)
        return await self._connection().insert(plan)

    async def update(self, values: dict[str, Any]) -> int:
        """
        Mass update the rows matched by the query.

        The update timestamp is refreshed automatically when the model
        maintains timestamps.

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

        payload = dict(values)
        updated_column = self._meta.updated_column
        if updated_column and updated_column not in payload:
            payload[updated_column] = self._model.freshTimestamp()

        plan = UpdatePlan(
            table=self._meta.table,
            values=serialize_for_storage(self._meta, payload),
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
        plan = DeletePlan(
            table=self._meta.table,
            wheres=list(self._plan.wheres),
        )
        return await self._connection().delete(plan)

    # ── Internal helpers ────────────────────────────────────────────────────

    def _connection(self) -> IConnection:
        """
        Resolve the database connection for the bound model.

        Returns
        -------
        IConnection
            Connection declared by the model, or the default one.
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
                error_msg = (
                    "Mapping conditions do not accept extra arguments."
                )
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

        error_msg = (
            "where() expects (column, value) or (column, operator, value)."
        )
        raise InvalidQueryException(error_msg)

    async def _aggregate(
        self,
        function: AggregateFunction,
        column: str,
    ) -> Any:  # noqa: ANN401
        """
        Execute an aggregate projection over the current plan.

        Parameters
        ----------
        function : AggregateFunction
            Aggregate function to apply.
        column : str
            Target column, or ``"*"`` for ``COUNT``.

        Returns
        -------
        Any
            Aggregate scalar value.
        """
        probe = self._plan.clone()
        probe.aggregate = AggregateClause(function=function, column=column)
        probe.limit_value = None
        probe.offset_value = None
        return await self._connection().scalar(probe)

    @staticmethod
    def _materializeValues(values: Iterable[Any]) -> tuple[Any, ...]:
        """
        Materialize an iterable of bound values into a tuple.

        Parameters
        ----------
        values : Iterable
            Values to materialize; collections are unwrapped.

        Returns
        -------
        tuple
            Materialized values.
        """
        if isinstance(values, Collection):
            return tuple(values.all())
        return tuple(values)
