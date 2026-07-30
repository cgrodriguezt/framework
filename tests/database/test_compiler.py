from __future__ import annotations
from orionis.database.compiler import SQLCompiler
from orionis.database.exceptions import QueryException
from orionis.orm.query.expressions import (
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
from orionis.orm.schema.table import TableDefinition
from orionis.orm.schema.types import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    Integer,
    SmallInteger,
    StrictBinary,
    StrictDecimal,
    StrictJson,
    StrictTimestamp,
    String,
    Text,
    Time,
    Uuid,
)
from orionis.test import TestCase

def _makeTable() -> TableDefinition:
    """Build a small table definition used across the compiler tests."""
    columns = {
        "id": Integer().primary().autoIncrement(),
        "name": String(),
        "active": Boolean(),
    }
    for key, column in columns.items():
        column.name = key
    return TableDefinition(name="users", columns=columns, primary_key="id")

class TestSQLCompiler(TestCase):

    def setUp(self) -> None:
        """
        Create a fresh compiler and table definition per test.

        Guarantees isolation of the internal table cache.
        """
        self._compiler = SQLCompiler()
        self._table = _makeTable()

    def _sql(self, statement) -> str:
        """Render a statement to normalized lowercase SQL."""
        return str(statement.compile()).lower()

    # ── SELECT ────────────────────────────────────────────────────────────────

    def testCompileSelectAllColumns(self) -> None:
        """
        Compile a bare select into SELECT ... FROM table.

        Validates the default full projection.
        """
        sql = self._sql(self._compiler.compileSelect(SelectPlan(table=self._table)))
        self.assertIn("select", sql)
        self.assertIn("from users", sql)

    def testCompileSelectProjectsColumns(self) -> None:
        """
        Compile an explicit projection into a column list.

        Validates that only the requested columns are projected.
        """
        plan = SelectPlan(table=self._table, columns=("name",))
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("users.name", sql)
        self.assertNotIn("users.active", sql)

    def testCompileSelectWithWhereAndOrConnector(self) -> None:
        """
        Fold consecutive clauses honoring their boolean connectors.

        Validates AND/OR folding order in the where expression.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(WhereClause(column="active", value=True))
        plan.wheres.append(
            WhereClause(column="name", value="john", boolean="or"),
        )
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("where", sql)
        self.assertIn("or", sql)

    def testCompileSelectNullPromotion(self) -> None:
        """
        Promote equality with None to IS NULL.

        Validates the NULL comparison promotion rule.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(WhereClause(column="name", value=None))
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("is null", sql)

    def testCompileSelectInClause(self) -> None:
        """
        Compile IN conditions with bound value lists.

        Validates the IN clause expansion.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(
            WhereClause(column="id", whereType=WhereType.IN, value=(1, 2)),
        )
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("in", sql)

    def testCompileSelectBetweenRequiresTwoBounds(self) -> None:
        """
        Raise QueryException for malformed BETWEEN boundaries.

        Validates the boundary arity check.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(
            WhereClause(column="id", whereType=WhereType.BETWEEN, value=(1,)),
        )
        with self.assertRaises(QueryException):
            self._compiler.compileSelect(plan)

    def testCompileSelectOrderLimitOffset(self) -> None:
        """
        Compile ordering and pagination into the statement.

        Validates ORDER BY, LIMIT, and OFFSET emission.
        """
        plan = SelectPlan(table=self._table)
        plan.orders.append(
            OrderClause(column="name", direction=SortDirection.DESC),
        )
        plan.limitValue = 10
        plan.offsetValue = 5
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("order by", sql)
        self.assertIn("desc", sql)
        self.assertIn("limit", sql)
        self.assertIn("offset", sql)

    def testCompileSelectUnknownColumnRaises(self) -> None:
        """
        Raise QueryException for references to unknown columns.

        Validates the descriptive column resolution error.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(WhereClause(column="ghost", value=1))
        with self.assertRaises(QueryException):
            self._compiler.compileSelect(plan)

    def testCompileSelectCountAggregate(self) -> None:
        """
        Compile COUNT(*) aggregates into the projection.

        Validates the aggregate projection replacement.
        """
        plan = SelectPlan(
            table=self._table,
            aggregate=AggregateClause(function=AggregateFunction.COUNT),
        )
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("count", sql)

    def testCompileSelectAggregateStarRequiresCount(self) -> None:
        """
        Reject non-count aggregates targeting the star column.

        Validates the aggregate column requirement.
        """
        plan = SelectPlan(
            table=self._table,
            aggregate=AggregateClause(function=AggregateFunction.MAX),
        )
        with self.assertRaises(QueryException):
            self._compiler.compileSelect(plan)

    # ── INSERT / UPDATE / DELETE ─────────────────────────────────────────────

    def testCompileInsertSingleRow(self) -> None:
        """
        Compile a single-row insert statement.

        Validates the INSERT statement shape.
        """
        plan = InsertPlan(table=self._table, values=[{"name": "john"}])
        sql = self._sql(self._compiler.compileInsert(plan))
        self.assertIn("insert into users", sql)

    def testCompileInsertWithoutValuesRaises(self) -> None:
        """
        Raise QueryException for inserts without any row.

        Validates the empty insert guard.
        """
        with self.assertRaises(QueryException):
            self._compiler.compileInsert(InsertPlan(table=self._table))

    def testCompileUpdateWithWhere(self) -> None:
        """
        Compile an update restricted by conditions.

        Validates SET and WHERE emission.
        """
        plan = UpdatePlan(
            table=self._table,
            values={"name": "peter"},
            wheres=[WhereClause(column="id", value=1)],
        )
        sql = self._sql(self._compiler.compileUpdate(plan))
        self.assertIn("update users", sql)
        self.assertIn("where", sql)

    def testCompileUpdateWithoutValuesRaises(self) -> None:
        """
        Raise QueryException for updates without values.

        Validates the empty update guard.
        """
        with self.assertRaises(QueryException):
            self._compiler.compileUpdate(UpdatePlan(table=self._table))

    def testCompileDeleteWithWhere(self) -> None:
        """
        Compile a delete restricted by conditions.

        Validates DELETE and WHERE emission.
        """
        plan = DeletePlan(
            table=self._table,
            wheres=[WhereClause(column="id", value=1)],
        )
        sql = self._sql(self._compiler.compileDelete(plan))
        self.assertIn("delete from users", sql)
        self.assertIn("where", sql)

    # ── Prefix and DDL ────────────────────────────────────────────────────────

    def testPrefixIsAppliedToPhysicalTables(self) -> None:
        """
        Prepend the configured prefix to physical table names.

        Validates prefix application at compile time.
        """
        compiler = SQLCompiler(prefix="app_")
        sql = str(
            compiler.compileSelect(SelectPlan(table=self._table)).compile(),
        ).lower()
        self.assertIn("app_users", sql)

    def testNotLikeOperatorCompiles(self) -> None:
        """
        Compile the "not like" comparison operator.

        Validates the negated pattern comparison.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(
            WhereClause(column="name", operator="not like", value="a%"),
        )
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("not like", sql)

    def testNotInClauseCompiles(self) -> None:
        """
        Compile NOT IN conditions with bound value lists.

        Validates the NOT IN clause expansion.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(
            WhereClause(column="id", whereType=WhereType.NOT_IN, value=(1,)),
        )
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("not in", sql)

    def testNullChecksCompileToIsExpressions(self) -> None:
        """
        Compile NULL and NOT NULL checks into IS expressions.

        Validates both nullability clause kinds.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(
            WhereClause(column="name", whereType=WhereType.NULL),
        )
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("is null", sql)

        plan_not = SelectPlan(table=self._table)
        plan_not.wheres.append(
            WhereClause(column="name", whereType=WhereType.NOT_NULL),
        )
        sql_not = self._sql(self._compiler.compileSelect(plan_not))
        self.assertIn("is not null", sql_not)

    def testInequalityWithNonePromotesToIsNotNull(self) -> None:
        """
        Promote inequality with None to IS NOT NULL.

        Validates the negative NULL promotion rule.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(
            WhereClause(column="name", operator="!=", value=None),
        )
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("is not null", sql)

    def testUnsupportedOperatorRaises(self) -> None:
        """
        Raise QueryException for unsupported comparison operators.

        Validates the operator guard at compile time.
        """
        plan = SelectPlan(table=self._table)
        plan.wheres.append(
            WhereClause(column="name", operator="~", value="x"),
        )
        with self.assertRaises(QueryException):
            self._compiler.compileSelect(plan)

    def testGroupByAndHavingCompile(self) -> None:
        """
        Compile grouping columns and post-grouping conditions.

        Validates GROUP BY and HAVING emission.
        """
        plan = SelectPlan(table=self._table)
        plan.groups.append("active")
        plan.havings.append(WhereClause(column="active", value=True))
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("group by", sql)
        self.assertIn("having", sql)

    def testAggregateAppliesWhereConditions(self) -> None:
        """
        Apply filtering conditions to aggregate projections.

        Validates the aggregate + where combination.
        """
        plan = SelectPlan(
            table=self._table,
            aggregate=AggregateClause(
                function=AggregateFunction.SUM,
                column="id",
            ),
        )
        plan.wheres.append(WhereClause(column="active", value=True))
        sql = self._sql(self._compiler.compileSelect(plan))
        self.assertIn("sum", sql)
        self.assertIn("where", sql)

    def testEveryColumnTypeCompilesInDdl(self) -> None:
        """
        Compile a table using every supported column type.

        Validates the complete logical-to-engine type registry.
        """
        columns = {
            "id": Integer().primary().autoIncrement(),
            "big": BigInteger(),
            "small": SmallInteger(),
            "name": String(50),
            "body": Text(),
            "flag": Boolean(),
            "ratio": Float(),
            "price": StrictDecimal(10, 2),
            "born": Date(),
            "at": Time(),
            "seen": DateTime(),
            "stamped": StrictTimestamp(),
            "payload": StrictJson(),
            "token": Uuid(),
            "blob": StrictBinary(),
            "state": Enum("draft", "published"),
        }
        for key, column in columns.items():
            column.name = key
        table = TableDefinition(name="samples", columns=columns, primary_key="id")

        ddl = str(SQLCompiler().compileCreateTable(table)).lower()
        for key in columns:
            self.assertIn(key, ddl)
        self.assertIn("varchar(50)", ddl)
        self.assertIn("decimal(10, 2)", ddl)

    def testForeignKeyAppearsInDdlWithPrefix(self) -> None:
        """
        Emit prefixed foreign key references in the DDL.

        Validates foreign key propagation and prefixing.
        """
        columns = {
            "id": Integer().primary(),
            "company_id": Integer().foreign("companies.id"),
        }
        for key, column in columns.items():
            column.name = key
        table = TableDefinition(name="staff", columns=columns, primary_key="id")

        ddl = str(SQLCompiler(prefix="app_").compileCreateTable(table)).lower()
        self.assertIn("foreign key", ddl)
        self.assertIn("app_companies", ddl)

    def testDefaultValueIsAppliedOnInsertCompilation(self) -> None:
        """
        Keep column defaults available in the engine metadata.

        Validates that declared defaults reach the engine column so
        the execution context applies them on insert.
        """
        columns = {
            "id": Integer().primary().autoIncrement(),
            "status": String().default("draft"),
        }
        for key, column in columns.items():
            column.name = key
        table = TableDefinition(name="drafts", columns=columns, primary_key="id")

        compiler = SQLCompiler()
        engine_table = compiler._sqlTable(table)
        self.assertEqual(engine_table.c["status"].default.arg, "draft")


    def testCompileCreateTableEmitsColumns(self) -> None:
        """
        Compile the table definition into a CREATE TABLE statement.

        Validates the DDL generation used by the schema helpers.
        """
        ddl = str(self._compiler.compileCreateTable(self._table)).lower()
        self.assertIn("create table", ddl)
        self.assertIn("id", ddl)
        self.assertIn("name", ddl)

    def testCompileDropTableTargetsName(self) -> None:
        """
        Compile a DROP TABLE statement for a logical name.

        Validates the drop DDL generation.
        """
        ddl = str(self._compiler.compileDropTable("users")).lower()
        self.assertIn("drop table", ddl)
        self.assertIn("users", ddl)
