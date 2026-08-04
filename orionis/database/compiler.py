from __future__ import annotations
import operator
from typing import TYPE_CHECKING, Any, ClassVar
import sqlalchemy
from sqlalchemy import Column as SqlColumn
from sqlalchemy import ForeignKey, MetaData, Table, and_, func, or_
from sqlalchemy.schema import CreateTable, DropTable
from orionis.database.exceptions import QueryException
from orionis.orm.query.expressions import (
    AggregateFunction,
    JoinType,
    SortDirection,
    WhereType,
)
from orionis.orm.schema.types import ColumnType

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from sqlalchemy.sql import Delete, Insert, Select, Update
    from sqlalchemy.sql.elements import ColumnElement
    from sqlalchemy.sql.expression import Executable
    from sqlalchemy.types import TypeEngine
    from orionis.orm.query.expressions import (
        AggregateClause,
        DeletePlan,
        InsertPlan,
        JoinCondition,
        JoinExpression,
        SelectPlan,
        UpdatePlan,
        WhereClause,
    )
    from orionis.orm.schema.column import ColumnDefinition
    from orionis.orm.schema.constraints import ForeignReference
    from orionis.orm.schema.table import TableDefinition

    # A resolvable FROM/JOIN source: either the raw engine Table or an
    # aliased projection of it (``Table.alias(name)``).
    type SqlSource = Any
    # Table sources reachable by qualified column references, keyed by
    # alias when present or by logical table name otherwise.
    type SourceMap = dict[str, SqlSource]

# Comparison operators for basic where clauses.
_COMPARATORS: dict[str, Callable[[Any, Any], Any]] = {
    "=": operator.eq,
    "==": operator.eq,
    "!=": operator.ne,
    "<>": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}

# Operators whose NULL comparison must compile to IS / IS NOT.
_EQUALITY_OPERATORS: frozenset[str] = frozenset({"=", "=="})
_INEQUALITY_OPERATORS: frozenset[str] = frozenset({"!=", "<>"})

# Pattern-matching operators accepted by basic where clauses.
_PATTERN_OPERATORS: dict[str, Callable[[Any, Any], Any]] = {
    "like": lambda col, val: col.like(val),
    "not like": lambda col, val: col.not_like(val),
    "ilike": lambda col, val: col.ilike(val),
    "not ilike": lambda col, val: col.not_ilike(val),
}

# Number of boundaries required by a BETWEEN condition.
_BETWEEN_BOUNDS: int = 2

# Handlers for where clause kinds with a single-expression translation.
_SIMPLE_CLAUSES: dict[WhereType, Callable[[Any, Any], Any]] = {
    WhereType.IN: lambda col, val: col.in_(list(val or ())),
    WhereType.NOT_IN: lambda col, val: col.not_in(list(val or ())),
    WhereType.NULL: lambda col, _val: col.is_(None),
    WhereType.NOT_NULL: lambda col, _val: col.is_not(None),
    WhereType.LIKE: lambda col, val: col.like(val),
    WhereType.NOT_LIKE: lambda col, val: col.not_like(val),
    WhereType.ILIKE: lambda col, val: col.ilike(val),
    WhereType.NOT_ILIKE: lambda col, val: col.not_ilike(val),
    WhereType.STARTS_WITH: lambda col, val: col.startswith(val),
    WhereType.ENDS_WITH: lambda col, val: col.endswith(val),
    WhereType.CONTAINS: lambda col, val: col.contains(val),
    WhereType.REGEXP: lambda col, val: col.regexp_match(val),
}

class SQLCompiler:
    """
    Translate Orionis query plans into engine-executable statements.

    This is the only component, together with the connection and the
    dialect helpers, aware of the underlying SQL toolkit. It converts
    :class:`TableDefinition` objects into engine table metadata (cached
    per compiler) and query plans into executable statements.
    """

    __slots__ = ("_metadata", "_prefix", "_tables")

    # Builders translating logical column types into engine types.
    _TYPE_BUILDERS: ClassVar[
        dict[ColumnType, Callable[[ColumnDefinition], TypeEngine[Any]]]
    ] = {
        # Generic "CamelCase" types.
        ColumnType.INTEGER: lambda _c: sqlalchemy.Integer(),
        ColumnType.BIG_INTEGER: lambda _c: sqlalchemy.BigInteger(),
        ColumnType.SMALL_INTEGER: lambda _c: sqlalchemy.SmallInteger(),
        ColumnType.STRING: lambda c: sqlalchemy.String(c.length, c.collation),
        ColumnType.TEXT: lambda c: sqlalchemy.Text(c.length, c.collation),
        ColumnType.UNICODE: lambda c: sqlalchemy.Unicode(c.length, c.collation),
        ColumnType.UNICODE_TEXT: lambda c: sqlalchemy.UnicodeText(
            c.length, c.collation,
        ),
        ColumnType.BOOLEAN: lambda c: sqlalchemy.Boolean(
            create_constraint=c.create_constraint,
            name=c.constraint_name,
        ),
        ColumnType.FLOAT: lambda c: sqlalchemy.Float(
            c.precision, asdecimal=c.as_decimal,
            decimal_return_scale=c.decimal_return_scale,
        ),
        ColumnType.DOUBLE: lambda c: sqlalchemy.Double(
            c.precision, asdecimal=c.as_decimal,
            decimal_return_scale=c.decimal_return_scale,
        ),
        ColumnType.NUMERIC: lambda c: sqlalchemy.Numeric(
            c.precision, c.scale, c.decimal_return_scale, asdecimal=c.as_decimal,
        ),
        ColumnType.DATE: lambda _c: sqlalchemy.Date(),
        ColumnType.TIME: lambda _c: sqlalchemy.Time(),
        ColumnType.DATETIME: lambda c: sqlalchemy.DateTime(timezone=c.timezone),
        ColumnType.INTERVAL: lambda c: sqlalchemy.Interval(
            native=c.native,
            second_precision=c.second_precision,
            day_precision=c.day_precision,
        ),
        ColumnType.LARGE_BINARY: lambda c: sqlalchemy.LargeBinary(c.length),
        ColumnType.UUID: lambda c: sqlalchemy.Uuid(
            as_uuid=c.as_uuid, native_uuid=c.native_uuid,
        ),
        ColumnType.PICKLE_TYPE: lambda c: sqlalchemy.PickleType(
            protocol=c.protocol,
        ),
        ColumnType.ENUM: lambda c: sqlalchemy.Enum(
            *c.enum_values,
            name=c.enum_name,
            native_enum=False,
            create_constraint=False,
        ),

        # SQL standard and multiple vendor "UPPERCASE" types.
        ColumnType.BIGINT: lambda _c: sqlalchemy.BIGINT(),
        ColumnType.SMALLINT: lambda _c: sqlalchemy.SMALLINT(),
        ColumnType.INT: lambda _c: sqlalchemy.INTEGER(),
        ColumnType.CHAR: lambda c: sqlalchemy.CHAR(c.length, c.collation),
        ColumnType.VARCHAR: lambda c: sqlalchemy.VARCHAR(c.length, c.collation),
        ColumnType.NCHAR: lambda c: sqlalchemy.NCHAR(c.length, c.collation),
        ColumnType.NVARCHAR: lambda c: sqlalchemy.NVARCHAR(c.length, c.collation),
        ColumnType.CLOB: lambda c: sqlalchemy.CLOB(c.length, c.collation),
        ColumnType.REAL: lambda c: sqlalchemy.REAL(
            c.precision, asdecimal=c.as_decimal,
            decimal_return_scale=c.decimal_return_scale,
        ),
        ColumnType.DOUBLE_PRECISION: lambda c: sqlalchemy.DOUBLE_PRECISION(
            c.precision, asdecimal=c.as_decimal,
            decimal_return_scale=c.decimal_return_scale,
        ),
        ColumnType.DECIMAL: lambda c: sqlalchemy.DECIMAL(
            c.precision, c.scale, c.decimal_return_scale, asdecimal=c.as_decimal,
        ),
        ColumnType.TIMESTAMP: lambda c: sqlalchemy.TIMESTAMP(timezone=c.timezone),
        ColumnType.BINARY: lambda c: sqlalchemy.BINARY(c.length),
        ColumnType.VARBINARY: lambda c: sqlalchemy.VARBINARY(c.length),
        ColumnType.BLOB: lambda c: sqlalchemy.BLOB(c.length),
        ColumnType.JSON: lambda c: sqlalchemy.JSON(none_as_null=c.none_as_null),
    }

    def __init__(self, prefix: str = "") -> None:
        """
        Initialize the compiler with an optional table name prefix.

        Parameters
        ----------
        prefix : str, optional
            Prefix prepended to every physical table name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self._prefix = prefix or ""
        self._metadata = MetaData()
        self._tables: dict[str, Table] = {}

    # ── Statement compilation ───────────────────────────────────────────────

    def compileSelect(self, plan: SelectPlan) -> Select[Any]:
        """
        Compile a select plan into an executable SELECT statement.

        Parameters
        ----------
        plan : SelectPlan
            Engine-agnostic select description.

        Returns
        -------
        Select
            Executable SELECT statement.

        Raises
        ------
        QueryException
            If the plan references unknown columns or invalid clauses.
        """
        self._ensureSelectRawColumns(plan)
        default, sources, from_clause = self._resolveSources(plan)
        statement = self._selectProjection(default, sources, plan)
        if plan.joins:
            statement = statement.select_from(from_clause)
        if plan.distinct and plan.aggregate is None:
            statement = statement.distinct()

        # Apply filtering conditions.
        condition = self._whereExpression(sources, default, plan.wheres)
        if condition is not None:
            statement = statement.where(condition)

        # Apply grouping and post-grouping conditions.
        if plan.groups:
            groups = [
                self._resolveColumn(sources, default, name)
                for name in plan.groups
            ]
            statement = statement.group_by(*groups)
        having = self._whereExpression(sources, default, plan.havings)
        if having is not None:
            statement = statement.having(having)

        # Ordering and pagination are meaningless for aggregates.
        if plan.aggregate is None:
            statement = self._applyOrderingAndPaging(
                sources, default, statement, plan,
            )

        return statement

    # ── Schemaless (raw) table support ──────────────────────────────────────

    def _bareNameForIdentifier(self, name: str, identifier: str) -> str | None:
        """
        Return the bare column name when a reference targets an identifier.

        Parameters
        ----------
        name : str
            Column reference, optionally qualified as ``"table.column"``.
        identifier : str
            Alias or logical table name being checked against.

        Returns
        -------
        str or None
            The bare column name when unqualified or matching
            ``identifier``, otherwise ``None``.
        """
        qualifier, column = self._splitQualifiedColumn(name)
        if qualifier is None or qualifier == identifier:
            return column
        return None

    def _collectPlanColumnNames(self, plan: SelectPlan) -> set[str]:
        """
        Collect every column reference touched anywhere in a select plan.

        Parameters
        ----------
        plan : SelectPlan
            Engine-agnostic select description.

        Returns
        -------
        set of str
            Every column name referenced by the plan, qualified or not.
        """
        names: set[str] = set(plan.columns)
        names.update(clause.column for clause in plan.wheres)
        names.update(clause.column for clause in plan.havings)
        names.update(order.column for order in plan.orders)
        names.update(plan.groups)
        if plan.aggregate is not None and plan.aggregate.column != "*":
            names.add(plan.aggregate.column)
        for join in plan.joins:
            for condition in join.conditions:
                names.add(condition.first)
                names.add(condition.second)
        return names

    def _ensureRawColumns(
        self,
        table: TableDefinition,
        alias: str | None,
        names: set[str],
    ) -> None:
        """
        Lazily declare columns a plan references against a raw table.

        A schemaless :class:`TableDefinition` (no declared columns, used
        by model-less builders such as ``DB.table("users")``) has no
        upfront column list for the compiler to validate against. Every
        name the plan actually references for it is appended to its
        engine table here, before any alias gets created, since
        ``Table.alias().c`` memoizes on first access and would silently
        miss columns appended afterwards.

        Parameters
        ----------
        table : TableDefinition
            Table to inspect; a no-op unless it declares no columns.
        alias : str or None
            Alias this table is referred to by inside the query.
        names : set of str
            Every column reference collected from the owning plan.

        Returns
        -------
        None
            This method does not return a value.
        """
        if table.columns:
            return  # already has a real, declared schema

        identifier = alias or table.name
        bare_names = {
            column
            for name in names
            if (column := self._bareNameForIdentifier(name, identifier)) is not None
        }
        if not bare_names:
            return

        engine_table = self._sqlTable(table)
        for column in bare_names:
            if column not in engine_table.c:
                engine_table.append_column(SqlColumn(column))

    def _ensureSelectRawColumns(self, plan: SelectPlan) -> None:
        """
        Lazily declare raw columns referenced by a select plan's sources.

        Parameters
        ----------
        plan : SelectPlan
            Engine-agnostic select description.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Every source already has a declared schema in the common,
        # model-backed case; skip scanning every clause for nothing.
        if plan.table.columns and all(join.table.columns for join in plan.joins):
            return
        names = self._collectPlanColumnNames(plan)
        self._ensureRawColumns(plan.table, plan.alias, names)
        for join in plan.joins:
            self._ensureRawColumns(join.table, join.alias, names)

    def _resolveSources(
        self,
        plan: SelectPlan,
    ) -> tuple[SqlSource, SourceMap, SqlSource]:
        """
        Build the main source, the resolvable source map, and the FROM.

        The main table and every joined table are registered under the
        identifier queries use to qualify their columns: the alias when
        present, otherwise the logical table name. This is what lets
        ``_resolveColumn`` find ``"users.id"`` or ``"posts.title"``
        regardless of how many tables participate in the query.

        Parameters
        ----------
        plan : SelectPlan
            Engine-agnostic select description.

        Returns
        -------
        tuple of (SqlSource, SourceMap, SqlSource)
            The main source (for unqualified projections), the source
            map keyed by alias or table name, and the compiled FROM
            clause (the main source joined with every configured join).
        """
        table = self._sqlTable(plan.table)
        default = table.alias(plan.alias) if plan.alias else table
        sources: SourceMap = {plan.alias or plan.table.name: default}

        from_clause = default
        for join in plan.joins:
            from_clause, joined_name, joined_source = self._applyJoin(
                from_clause, sources, join,
            )
            sources[joined_name] = joined_source

        return default, sources, from_clause

    def _applyJoin(
        self,
        from_clause: SqlSource,
        sources: SourceMap,
        join: JoinExpression,
    ) -> tuple[SqlSource, str, SqlSource]:
        """
        Extend a FROM clause with a single joined table.

        Parameters
        ----------
        from_clause : SqlSource
            FROM clause assembled so far.
        sources : SourceMap
            Table sources already reachable by qualified references.
        join : JoinExpression
            Join description to compile.

        Returns
        -------
        tuple of (SqlSource, str, SqlSource)
            The extended FROM clause, the identifier the joined table is
            reachable by, and the joined source itself.

        Raises
        ------
        QueryException
            If the join type is not supported yet, or its ON conditions
            cannot be resolved.
        """
        joined_table = self._sqlTable(join.table)
        joined_source = joined_table.alias(join.alias) if join.alias else joined_table
        joined_name = join.alias or join.table.name

        if join.join_type is JoinType.CROSS:
            return from_clause.join(joined_source, sqlalchemy.true()), \
                joined_name, joined_source

        condition = self._joinCondition(sources, joined_name, joined_source, join)
        if join.join_type is JoinType.INNER:
            joined = from_clause.join(joined_source, condition)
        elif join.join_type is JoinType.LEFT:
            joined = from_clause.join(joined_source, condition, isouter=True)
        else:
            error_msg = (
                f"Join type '{join.join_type}' is not supported yet."
            )
            raise QueryException(error_msg)
        return joined, joined_name, joined_source

    def _joinCondition(
        self,
        sources: SourceMap,
        joined_name: str,
        joined_source: SqlSource,
        join: JoinExpression,
    ) -> ColumnElement[bool]:
        """
        Fold a join's ON conditions into a single boolean expression.

        Parameters
        ----------
        sources : SourceMap
            Table sources reachable before this join is applied.
        joined_name : str
            Identifier the joined table is reachable by.
        joined_source : SqlSource
            The joined table source itself.
        join : JoinExpression
            Join description whose conditions are compiled.

        Returns
        -------
        ColumnElement
            Combined boolean expression for the ON clause.

        Raises
        ------
        QueryException
            If the join declares no ON conditions.
        """
        if not join.conditions:
            error_msg = (
                f"Join on '{joined_name}' requires at least one ON condition."
            )
            raise QueryException(error_msg)

        local_sources: SourceMap = {**sources, joined_name: joined_source}
        expression: ColumnElement[bool] | None = None
        for condition in join.conditions:
            piece = self._joinConditionExpression(
                local_sources, joined_source, condition,
            )
            if expression is None:
                expression = piece
            elif condition.boolean == "or":
                expression = or_(expression, piece)
            else:
                expression = and_(expression, piece)
        return expression

    def _joinConditionExpression(
        self,
        sources: SourceMap,
        default: SqlSource,
        condition: JoinCondition,
    ) -> ColumnElement[bool]:
        """
        Compile a single ON condition into a column-to-column comparison.

        Parameters
        ----------
        sources : SourceMap
            Table sources reachable while resolving this condition.
        default : SqlSource
            Source an unqualified column reference resolves against.
        condition : JoinCondition
            ON condition to compile.

        Returns
        -------
        ColumnElement
            Boolean expression comparing both column references.

        Raises
        ------
        QueryException
            If the operator is not supported.
        """
        left = self._resolveColumn(sources, default, condition.first)
        right = self._resolveColumn(sources, default, condition.second)
        comparator = _COMPARATORS.get(condition.operator.strip().lower())
        if comparator is None:
            error_msg = f"Unsupported join operator '{condition.operator}'."
            raise QueryException(error_msg)
        return comparator(left, right)

    def _selectProjection(
        self,
        default: SqlSource,
        sources: SourceMap,
        plan: SelectPlan,
    ) -> Select[Any]:
        """
        Build the base SELECT statement with its projection.

        Parameters
        ----------
        default : SqlSource
            Source an unqualified column reference resolves against.
        sources : SourceMap
            Table sources reachable by qualified column references.
        plan : SelectPlan
            Engine-agnostic select description.

        Returns
        -------
        Select
            Statement projecting the aggregate, explicit columns, or
            every column of the main table.
        """
        if plan.aggregate is not None:
            return sqlalchemy.select(
                self._aggregateExpression(sources, default, plan.aggregate),
            ).select_from(default)
        if plan.columns:
            projected = [
                self._resolveColumn(sources, default, name)
                for name in plan.columns
            ]
            return sqlalchemy.select(*projected)
        if not plan.table.columns:
            # Schemaless table: its real column list is unknowable up
            # front, so project literally instead of guessing a subset.
            return sqlalchemy.select(
                sqlalchemy.literal_column("*"),
            ).select_from(default)
        return sqlalchemy.select(default)

    def _applyOrderingAndPaging(
        self,
        sources: SourceMap,
        default: SqlSource,
        statement: Select[Any],
        plan: SelectPlan,
    ) -> Select[Any]:
        """
        Apply ordering, limit, and offset clauses to a statement.

        Parameters
        ----------
        sources : SourceMap
            Table sources reachable by qualified column references.
        default : SqlSource
            Source an unqualified column reference resolves against.
        statement : Select
            Statement being assembled.
        plan : SelectPlan
            Engine-agnostic select description.

        Returns
        -------
        Select
            Statement with ordering and pagination applied.
        """
        for order in plan.orders:
            column = self._resolveColumn(sources, default, order.column)
            descending = order.direction is SortDirection.DESC
            statement = statement.order_by(
                column.desc() if descending else column.asc(),
            )
        if plan.limit_value is not None:
            statement = statement.limit(plan.limit_value)
        if plan.offset_value is not None:
            statement = statement.offset(plan.offset_value)
        return statement

    def compileInsert(self, plan: InsertPlan) -> Insert:
        """
        Compile an insert plan into an executable INSERT statement.

        Parameters
        ----------
        plan : InsertPlan
            Engine-agnostic insert description.

        Returns
        -------
        Insert
            Executable INSERT statement.

        Raises
        ------
        QueryException
            If the plan carries no rows to insert.
        """
        if not plan.values:
            error_msg = "Cannot compile an INSERT statement without values."
            raise QueryException(error_msg)

        # Schemaless tables need their referenced columns backfilled first;
        # model-backed tables already declare them, so this is skipped.
        if not plan.table.columns:
            names: set[str] = set()
            for row in plan.values:
                names.update(row)
            self._ensureRawColumns(plan.table, None, names)

        table = self._sqlTable(plan.table)
        rows = plan.values if len(plan.values) > 1 else plan.values[0]
        return sqlalchemy.insert(table).values(rows)

    def compileUpdate(self, plan: UpdatePlan) -> Update:
        """
        Compile an update plan into an executable UPDATE statement.

        Parameters
        ----------
        plan : UpdatePlan
            Engine-agnostic update description.

        Returns
        -------
        Update
            Executable UPDATE statement.

        Raises
        ------
        QueryException
            If the plan carries no values to assign.
        """
        if not plan.values:
            error_msg = "Cannot compile an UPDATE statement without values."
            raise QueryException(error_msg)

        if not plan.table.columns:
            names = set(plan.values) | {clause.column for clause in plan.wheres}
            self._ensureRawColumns(plan.table, None, names)

        table = self._sqlTable(plan.table)
        sources: SourceMap = {plan.table.name: table}
        statement = sqlalchemy.update(table).values(dict(plan.values))
        condition = self._whereExpression(sources, table, plan.wheres)
        if condition is not None:
            statement = statement.where(condition)
        return statement

    def compileDelete(self, plan: DeletePlan) -> Delete:
        """
        Compile a delete plan into an executable DELETE statement.

        Parameters
        ----------
        plan : DeletePlan
            Engine-agnostic delete description.

        Returns
        -------
        Delete
            Executable DELETE statement.
        """
        if not plan.table.columns:
            names = {clause.column for clause in plan.wheres}
            self._ensureRawColumns(plan.table, None, names)

        table = self._sqlTable(plan.table)
        sources: SourceMap = {plan.table.name: table}
        statement = sqlalchemy.delete(table)
        condition = self._whereExpression(sources, table, plan.wheres)
        if condition is not None:
            statement = statement.where(condition)
        return statement

    def compileCreateTable(
        self,
        definition: TableDefinition,
        *,
        if_not_exists: bool = True,
    ) -> Executable:
        """
        Compile a table definition into a CREATE TABLE statement.

        Parameters
        ----------
        definition : TableDefinition
            Table definition to materialize.
        if_not_exists : bool, optional
            Whether to guard the statement with ``IF NOT EXISTS`` so that
            an already existing table is silently kept.

        Returns
        -------
        Executable
            DDL statement creating the table.
        """
        table = self._sqlTable(definition)
        return CreateTable(table, if_not_exists=if_not_exists)

    def compileDropTable(
        self,
        name: str,
        schema: str | None = None,
        *,
        if_exists: bool = True,
    ) -> Executable:
        """
        Compile a DROP TABLE statement for the given logical name.

        Parameters
        ----------
        name : str
            Logical table name; the compiler prefix is applied.
        schema : str or None, optional
            Database schema owning the table, or ``None`` for the default.
        if_exists : bool, optional
            Whether to guard the statement with ``IF EXISTS`` so that a
            missing table does not raise an error.

        Returns
        -------
        Executable
            DDL statement dropping the table.
        """
        physical = self._physicalName(name)
        table = self._tables.get(self._cacheKey(physical, schema))
        if table is None:
            # Build a lightweight standalone table object for the DDL.
            table = Table(physical, MetaData(), schema=schema)
        return DropTable(table, if_exists=if_exists)

    # ── Table and column resolution ─────────────────────────────────────────

    def _physicalName(self, name: str) -> str:
        """
        Prepend the connection prefix to a logical table name.

        Parameters
        ----------
        name : str
            Logical table name.

        Returns
        -------
        str
            Physical table name including the configured prefix.
        """
        return f"{self._prefix}{name}"

    def _cacheKey(self, physical: str, schema: str | None) -> str:
        """
        Build the internal table cache key, disambiguating by schema.

        Parameters
        ----------
        physical : str
            Physical table name including the connection prefix.
        schema : str or None
            Database schema owning the table, or ``None`` for the default.

        Returns
        -------
        str
            Cache key unique per physical name and schema.
        """
        return f"{schema}.{physical}" if schema else physical

    def _sqlTable(self, definition: TableDefinition) -> Table:
        """
        Resolve and cache the engine table for a table definition.

        Parameters
        ----------
        definition : TableDefinition
            Orionis table definition.

        Returns
        -------
        Table
            Engine table metadata.
        """
        physical = self._physicalName(definition.name)
        cache_key = self._cacheKey(physical, definition.schema)
        cached = self._tables.get(cache_key)
        if cached is not None:
            return cached

        # Pre-register referenced tables so foreign key DDL can resolve
        # them even when their models are compiled later.
        for column in definition.columns.values():
            if column.foreign_ref is not None:
                self._ensureReferencedTable(column.foreign_ref)
        for foreign_key in definition.foreign_keys:
            self._ensureReferencedColumns(
                foreign_key.ref_table, foreign_key.ref_columns,
            )

        columns = [
            self._sqlColumn(column)
            for column in definition.columns.values()
        ]
        table = Table(
            physical,
            self._metadata,
            *columns,
            *self._tableConstraints(definition),
            schema=definition.schema,
            comment=definition.comment,
            extend_existing=True,
        )
        self._tables[cache_key] = table
        return table

    def _tableConstraints(self, definition: TableDefinition) -> list[Any]:
        """
        Build the composite, table-level constraints for a definition.

        Parameters
        ----------
        definition : TableDefinition
            Orionis table definition.

        Returns
        -------
        list of Any
            SQLAlchemy schema items to attach alongside the columns.
        """
        constraints: list[Any] = []
        if definition.composite_primary_key:
            constraints.append(
                sqlalchemy.PrimaryKeyConstraint(*definition.composite_primary_key),
            )
        constraints.extend(
            sqlalchemy.UniqueConstraint(*unique.columns, name=unique.name)
            for unique in definition.unique_constraints
        )
        for foreign_key in definition.foreign_keys:
            ref_table = self._physicalName(foreign_key.ref_table)
            ref_columns = [
                f"{ref_table}.{column}"
                for column in foreign_key.ref_columns
            ]
            constraints.append(
                sqlalchemy.ForeignKeyConstraint(
                    foreign_key.columns, ref_columns, name=foreign_key.name,
                ),
            )
        for index in definition.indexes:
            name = index.name or f"ix_{definition.name}_{'_'.join(index.columns)}"
            constraints.append(
                sqlalchemy.Index(name, *index.columns, unique=index.unique),
            )
        return constraints

    def _ensureReferencedTable(self, reference: ForeignReference) -> None:
        """
        Register a stub for a referenced table when it is unknown.

        The stub only carries the referenced column so foreign key DDL
        can resolve its target; compiling the real model later replaces
        the stub through ``extend_existing``.

        Parameters
        ----------
        reference : ForeignReference
            Foreign reference to resolve.

        Returns
        -------
        None
            This method does not return a value.
        """
        self._ensureReferencedColumns(reference.table, (reference.column,))

    def _ensureReferencedColumns(
        self,
        table_name: str,
        columns: Sequence[str],
    ) -> None:
        """
        Register a stub table exposing the given referenced columns.

        Parameters
        ----------
        table_name : str
            Logical name of the referenced table.
        columns : Sequence of str
            Referenced column names, each stubbed as an integer key.

        Returns
        -------
        None
            This method does not return a value.
        """
        physical = self._physicalName(table_name)
        if physical in self._metadata.tables:
            return
        Table(
            physical,
            self._metadata,
            *(
                SqlColumn(column, sqlalchemy.Integer(), primary_key=True)
                for column in columns
            ),
        )

    def _sqlColumn(self, definition: ColumnDefinition) -> SqlColumn[Any]:
        """
        Translate a column definition into an engine column.

        Parameters
        ----------
        definition : ColumnDefinition
            Orionis column definition.

        Returns
        -------
        Column
            Engine column with type and constraints applied.

        Raises
        ------
        QueryException
            If the logical column type has no registered builder.
        """
        builder = self._TYPE_BUILDERS.get(definition.column_type)
        if builder is None:
            error_msg = (
                f"No SQL type registered for column type "
                f"'{definition.column_type}'."
            )
            raise QueryException(error_msg)

        args: list[Any] = [definition.name, builder(definition)]
        if definition.foreign_ref is not None:
            reference = definition.foreign_ref
            args.append(
                ForeignKey(f"{self._prefix}{reference.table}.{reference.column}"),
            )

        options: dict[str, Any] = {
            "primary_key": definition.is_primary,
            "nullable": definition.is_nullable and not definition.is_primary,
            "unique": definition.is_unique or None,
            "index": definition.has_index or None,
            "autoincrement": True if definition.is_auto_increment else "auto",
            "comment": definition.comment_text,
        }
        if definition.hasDefault():
            options["default"] = definition.default_value

        return SqlColumn(*args, **options)

    def _splitQualifiedColumn(self, name: str) -> tuple[str | None, str]:
        """
        Split a column reference into its table qualifier and column name.

        Parameters
        ----------
        name : str
            Column reference, optionally qualified as ``"table.column"``.

        Returns
        -------
        tuple of (str or None, str)
            The qualifier (``None`` when unqualified) and the bare
            column name.
        """
        if "." in name:
            qualifier, _, column = name.rpartition(".")
            return qualifier, column
        return None, name

    def _resolveColumn(
        self,
        sources: SourceMap,
        default: SqlSource,
        name: str,
    ) -> ColumnElement[Any]:
        """
        Resolve a column reference against the tables reachable in a plan.

        A qualified reference such as ``"posts.title"`` is looked up in
        ``sources`` by its table alias or name; an unqualified reference
        resolves against ``default`` (the plan's main table). This is the
        single place that understands multiple table origins, so joins,
        aliases, and future table expressions never need bespoke column
        lookup logic elsewhere in the compiler.

        Parameters
        ----------
        sources : SourceMap
            Table sources reachable by alias or logical table name.
        default : SqlSource
            Source an unqualified column reference resolves against.
        name : str
            Column reference, optionally qualified as ``"table.column"``.

        Returns
        -------
        ColumnElement
            Engine column element.

        Raises
        ------
        QueryException
            If the qualifier is unknown, or the column is not declared
            on the resolved table.
        """
        qualifier, column = self._splitQualifiedColumn(name)
        if qualifier is None:
            source = default
        else:
            source = sources.get(qualifier)
            if source is None:
                error_msg = f"Unknown table reference '{qualifier}' in '{name}'."
                raise QueryException(error_msg)
        try:
            return source.c[column]
        except KeyError as exc:
            origin = qualifier or getattr(default, "name", "?")
            error_msg = f"Unknown column '{column}' on table '{origin}'."
            raise QueryException(error_msg) from exc

    # ── Clause compilation ──────────────────────────────────────────────────

    def _whereExpression(
        self,
        sources: SourceMap,
        default: SqlSource,
        clauses: Sequence[WhereClause],
    ) -> ColumnElement[bool] | None:
        """
        Fold a sequence of where clauses into a boolean expression.

        Clauses are combined left to right honoring each clause boolean
        connector, mirroring the semantics of fluent query builders.

        Parameters
        ----------
        sources : SourceMap
            Table sources reachable by qualified column references.
        default : SqlSource
            Source an unqualified column reference resolves against.
        clauses : Sequence of WhereClause
            Conditions to combine.

        Returns
        -------
        ColumnElement or None
            Combined boolean expression, or ``None`` without clauses.
        """
        expression: ColumnElement[bool] | None = None
        for clause in clauses:
            piece = self._clauseExpression(sources, default, clause)
            if expression is None:
                expression = piece
            elif clause.boolean == "or":
                expression = or_(expression, piece)
            else:
                expression = and_(expression, piece)
        return expression

    def _clauseExpression(
        self,
        sources: SourceMap,
        default: SqlSource,
        clause: WhereClause,
    ) -> ColumnElement[bool]:
        """
        Compile a single where clause into a boolean expression.

        Parameters
        ----------
        sources : SourceMap
            Table sources reachable by qualified column references.
        default : SqlSource
            Source an unqualified column reference resolves against.
        clause : WhereClause
            Condition to compile.

        Returns
        -------
        ColumnElement
            Boolean expression for the clause.

        Raises
        ------
        QueryException
            If the clause uses an unsupported operator or shape.
        """
        column = self._resolveColumn(sources, default, clause.column)
        kind = clause.where_type

        if kind is WhereType.BASIC:
            return self._basicExpression(column, clause)
        if kind is WhereType.BETWEEN:
            bounds = tuple(clause.value or ())
            if len(bounds) != _BETWEEN_BOUNDS:
                error_msg = (
                    "BETWEEN conditions require exactly two boundary values."
                )
                raise QueryException(error_msg)
            return column.between(bounds[0], bounds[1])

        handler = _SIMPLE_CLAUSES.get(kind)
        if handler is None:
            error_msg = f"Unsupported where clause type '{kind}'."
            raise QueryException(error_msg)
        return handler(column, clause.value)

    def _basicExpression(
        self,
        column: ColumnElement[Any],
        clause: WhereClause,
    ) -> ColumnElement[bool]:
        """
        Compile a basic comparison clause into a boolean expression.

        ``NULL`` comparisons with equality operators are transparently
        promoted to ``IS NULL`` / ``IS NOT NULL``.

        Parameters
        ----------
        column : ColumnElement
            Column the comparison applies to.
        clause : WhereClause
            Basic condition to compile.

        Returns
        -------
        ColumnElement
            Boolean expression for the comparison.

        Raises
        ------
        QueryException
            If the operator is not supported.
        """
        op = clause.operator.strip().lower()

        # Promote NULL equality checks to IS NULL / IS NOT NULL semantics.
        if clause.value is None and op in _EQUALITY_OPERATORS:
            return column.is_(None)
        if clause.value is None and op in _INEQUALITY_OPERATORS:
            return column.is_not(None)

        pattern_handler = _PATTERN_OPERATORS.get(op)
        if pattern_handler is not None:
            return pattern_handler(column, clause.value)

        comparator = _COMPARATORS.get(op)
        if comparator is None:
            error_msg = f"Unsupported comparison operator '{clause.operator}'."
            raise QueryException(error_msg)
        return comparator(column, clause.value)

    def _aggregateExpression(
        self,
        sources: SourceMap,
        default: SqlSource,
        aggregate: AggregateClause,
    ) -> ColumnElement[Any]:
        """
        Compile an aggregate clause into a projection expression.

        Parameters
        ----------
        sources : SourceMap
            Table sources reachable by qualified column references.
        default : SqlSource
            Source an unqualified column reference resolves against.
        aggregate : AggregateClause
            Aggregate projection description.

        Returns
        -------
        ColumnElement
            Aggregate expression such as ``COUNT(*)`` or ``MAX(col)``.

        Raises
        ------
        QueryException
            If a non-count aggregate targets ``"*"``.
        """
        if aggregate.function is AggregateFunction.COUNT:
            if aggregate.column == "*":
                return func.count()
            return func.count(
                self._resolveColumn(sources, default, aggregate.column),
            )

        if aggregate.column == "*":
            error_msg = (
                f"Aggregate '{aggregate.function}' requires a column name."
            )
            raise QueryException(error_msg)

        column = self._resolveColumn(sources, default, aggregate.column)
        builder = getattr(func, aggregate.function.value)
        return builder(column)
