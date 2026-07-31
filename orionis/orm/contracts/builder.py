from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable

    from orionis.database.entities.result import InsertResult
    from orionis.orm.collections.paginator import Paginator
    from orionis.support.types.collection import Collection


class IModelQueryBuilder(ABC):
    """
    Contract for the fluent model query builder.

    Fluent methods return the builder itself for chaining; terminal
    methods execute the accumulated query against the model connection.
    """

    # ── Fluent methods ──────────────────────────────────────────────────────

    @abstractmethod
    def select(self, *columns: str) -> IModelQueryBuilder:
        """
        Restrict the query projection to the given columns.

        Parameters
        ----------
        *columns : str
            Column names to project; empty selects every column.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def where(
        self,
        column: str | dict[str, Any],
        *args: Any,  # noqa: ANN401
    ) -> IModelQueryBuilder:
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def orWhere(
        self,
        column: str | dict[str, Any],
        *args: Any,  # noqa: ANN401
    ) -> IModelQueryBuilder:
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereIn(self, column: str, values: Iterable[Any]) -> IModelQueryBuilder:
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereNotIn(
        self,
        column: str,
        values: Iterable[Any],
    ) -> IModelQueryBuilder:
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereNull(self, column: str) -> IModelQueryBuilder:
        """
        Filter rows whose column value is ``NULL``.

        Parameters
        ----------
        column : str
            Column name to filter by.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereNotNull(self, column: str) -> IModelQueryBuilder:
        """
        Filter rows whose column value is not ``NULL``.

        Parameters
        ----------
        column : str
            Column name to filter by.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereBetween(
        self,
        column: str,
        bounds: Iterable[Any],
    ) -> IModelQueryBuilder:
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereLike(self, column: str, pattern: str) -> IModelQueryBuilder:
        """
        Filter rows whose column value matches an SQL LIKE pattern.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            SQL LIKE pattern.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereNotLike(self, column: str, pattern: str) -> IModelQueryBuilder:
        """
        Filter rows whose column value does not match an SQL LIKE pattern.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            SQL LIKE pattern.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereILike(self, column: str, pattern: str) -> IModelQueryBuilder:
        """
        Filter rows matching a case-insensitive SQL LIKE pattern.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            SQL LIKE pattern.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereNotILike(self, column: str, pattern: str) -> IModelQueryBuilder:
        """
        Filter rows not matching a case-insensitive SQL LIKE pattern.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            SQL LIKE pattern.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereStartsWith(self, column: str, value: str) -> IModelQueryBuilder:
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereEndsWith(self, column: str, value: str) -> IModelQueryBuilder:
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereContains(self, column: str, value: str) -> IModelQueryBuilder:
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def whereRegexpMatch(self, column: str, pattern: str) -> IModelQueryBuilder:
        """
        Filter rows whose column value matches a regular expression.

        Parameters
        ----------
        column : str
            Column name to filter by.
        pattern : str
            Regular expression pattern.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def distinct(self) -> IModelQueryBuilder:
        """
        Collapse duplicate rows from the query results.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def orderBy(self, column: str, direction: str = "asc") -> IModelQueryBuilder:
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def groupBy(self, *columns: str) -> IModelQueryBuilder:
        """
        Add grouping columns to the query.

        Parameters
        ----------
        *columns : str
            Columns to group by.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def having(self, column: str, *args: Any) -> IModelQueryBuilder:  # noqa: ANN401
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
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def limit(self, value: int) -> IModelQueryBuilder:
        """
        Limit the number of rows returned by the query.

        Parameters
        ----------
        value : int
            Maximum number of rows.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def offset(self, value: int) -> IModelQueryBuilder:
        """
        Skip the given number of rows before returning results.

        Parameters
        ----------
        value : int
            Number of rows to skip.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def take(self, value: int) -> IModelQueryBuilder:
        """
        Limit the number of rows returned; alias of :meth:`limit`.

        Parameters
        ----------
        value : int
            Maximum number of rows.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def skip(self, value: int) -> IModelQueryBuilder:
        """
        Skip the given number of rows; alias of :meth:`offset`.

        Parameters
        ----------
        value : int
            Number of rows to skip.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def latest(self, column: str | None = None) -> IModelQueryBuilder:
        """
        Order the query by a timestamp column in descending order.

        Parameters
        ----------
        column : str or None, optional
            Column to sort by.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    @abstractmethod
    def oldest(self, column: str | None = None) -> IModelQueryBuilder:
        """
        Order the query by a timestamp column in ascending order.

        Parameters
        ----------
        column : str or None, optional
            Column to sort by.

        Returns
        -------
        IModelQueryBuilder
            The same builder, enabling fluent chaining.
        """

    # ── Terminal methods ────────────────────────────────────────────────────

    @abstractmethod
    async def get(self) -> Collection:
        """
        Execute the query and hydrate every matching row.

        Returns
        -------
        Collection
            Collection of hydrated model instances.
        """

    @abstractmethod
    async def first(self) -> Any:  # noqa: ANN401
        """
        Execute the query and hydrate only the first matching row.

        Returns
        -------
        Model or None
            First matching model, or ``None`` without matches.
        """

    @abstractmethod
    async def firstOrFail(self) -> Any:  # noqa: ANN401
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

    @abstractmethod
    async def find(self, key: Any) -> Any:  # noqa: ANN401
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

    @abstractmethod
    async def findOrFail(self, key: Any) -> Any:  # noqa: ANN401
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

    @abstractmethod
    async def paginate(
        self,
        page: int = 1,
        perPage: int = 15,  # noqa: N803 # NOSONAR
    ) -> Paginator:
        """
        Execute the query returning a length-aware page of results.

        Parameters
        ----------
        page : int, optional
            Page number starting at 1.
        perPage : int, optional
            Number of items per page.

        Returns
        -------
        Paginator
            Page of hydrated models with pagination metadata.
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

    @abstractmethod
    async def exists(self) -> bool:
        """
        Report whether the query matches at least one row.

        Returns
        -------
        bool
            ``True`` when a matching row exists.
        """

    @abstractmethod
    async def doesntExist(self) -> bool:
        """
        Report whether the query matches no rows.

        Returns
        -------
        bool
            ``True`` when no matching row exists.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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
