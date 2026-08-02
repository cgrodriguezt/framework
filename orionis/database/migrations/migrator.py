import time
from typing import TYPE_CHECKING, Any
from orionis.database.contracts.connection import IConnection
from orionis.database.contracts.manager import IConnectionManager
from orionis.database.contracts.migration import Migration
from orionis.database.contracts.migrator import IMigrator
from orionis.database.exceptions import MigrationNotFoundException
from orionis.foundation.contracts.application import IApplication
from orionis.introspection.modules.inspector import ModuleInspector
from orionis.introspection.modules.reflection import ReflectionModule
from orionis.orm.schema.table import TableDefinition
from orionis.orm.schema.types import BigInteger, Integer, String

# ruff: noqa: TC001, TC003

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

# Name of the table used to track already-applied migrations.
_MIGRATIONS_TABLE: str = "migrations"

def _buildMigrationsTable(table: str) -> TableDefinition:
    """
    Build the table definition for the migrations tracking table.

    Parameters
    ----------
    table : str
        Logical table name for tracked migrations.

    Returns
    -------
    TableDefinition
        Definition with ``id`` (primary key), ``migration`` (unique
        name), ``batch`` and ``migrated_at`` (epoch seconds) columns.
    """
    id_column = Integer().primary().autoIncrement()
    id_column.name = "id"

    migration_column = String(255).unique()
    migration_column.name = "migration"

    batch_column = Integer()
    batch_column.name = "batch"

    migrated_at_column = BigInteger()
    migrated_at_column.name = "migrated_at"

    return TableDefinition(
        name=table,
        columns={
            "id": id_column,
            "migration": migration_column,
            "batch": batch_column,
            "migrated_at": migrated_at_column,
        },
        primary_key="id",
    )

# The tracking table shape is fixed; build it once instead of re-allocating
# four ColumnDefinition instances on every migrate()/rollback() call.
_MIGRATIONS_TABLE_DEFINITION: TableDefinition = _buildMigrationsTable(
    _MIGRATIONS_TABLE,
)

class Migrator(IMigrator):
    """Discovers, applies, and reverts migrations under ``database/migrations``."""

    __slots__ = ("__app", "__conn_manager", "__discovered_cache")

    def __init__(self, app: IApplication, conn_manager: IConnectionManager) -> None:
        """
        Initialize the migrator.

        Parameters
        ----------
        app : IApplication
            Application instance used to resolve the migrations directory.
        conn_manager : IConnectionManager
            Connection manager used to resolve the database connection.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__app = app
        self.__conn_manager = conn_manager
        self.__discovered_cache: dict[str, type[Migration]] | None = None

    async def migrate(
        self,
        *,
        on_start: "Callable[[str], None] | None" = None,
        on_success: "Callable[[str, float], None] | None" = None,
        on_error: "Callable[[str, float], None] | None" = None,
    ) -> list[str]:
        """
        Apply every migration that has not been run yet.

        Parameters
        ----------
        on_start : callable, optional
            Invoked with the migration name right before it runs.
        on_success : callable, optional
            Invoked with the migration name and elapsed seconds after it
            applies successfully.
        on_error : callable, optional
            Invoked with the migration name and elapsed seconds when its
            ``up`` method raises, right before the exception propagates.

        Returns
        -------
        list of str
            Names of the migrations applied, in the order they ran.
        """
        connection = self.__conn_manager.connection()
        await self.__ensureMigrationsTable(connection)

        discovered = self.__discover()
        ran = await self.__getRan(connection)
        ran_names = {row["migration"] for row in ran}
        pending = [
            (name, cls) for name, cls in discovered.items() if name not in ran_names
        ]

        if not pending:
            return []

        batch = self.__nextBatch(ran)
        applied: list[str] = []
        for name, cls in pending:
            if on_start is not None:
                on_start(name)

            started_at = time.perf_counter()
            try:
                instance = cls()
                await instance.up()
                await self.__insertRecord(connection, name, batch)
            except Exception:
                if on_error is not None:
                    on_error(name, time.perf_counter() - started_at)
                raise

            if on_success is not None:
                on_success(name, time.perf_counter() - started_at)
            applied.append(name)

        return applied

    async def rollback(
        self,
        steps: int = 1,
        *,
        on_start: "Callable[[str], None] | None" = None,
        on_success: "Callable[[str, float], None] | None" = None,
        on_error: "Callable[[str, float], None] | None" = None,
    ) -> list[str]:
        """
        Revert the most recently applied migration batches.

        Parameters
        ----------
        steps : int, optional
            Number of batches to roll back, starting from the most
            recent one. Defaults to ``1``.
        on_start : callable, optional
            Invoked with the migration name right before it is reverted.
        on_success : callable, optional
            Invoked with the migration name and elapsed seconds after it
            reverts successfully.
        on_error : callable, optional
            Invoked with the migration name and elapsed seconds when its
            ``down`` method raises, right before the exception propagates.

        Returns
        -------
        list of str
            Names of the migrations reverted, in the order they were
            rolled back.

        Raises
        ------
        ValueError
            If ``steps`` is not a positive integer.
        MigrationNotFoundException
            If a recorded migration has no matching migration file.
        """
        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
            error_msg = "The 'steps' argument must be a positive integer."
            raise ValueError(error_msg)

        connection = self.__conn_manager.connection()
        await self.__ensureMigrationsTable(connection)

        ran = await self.__getRan(connection)
        if not ran:
            return []

        target_batches = set(
            sorted({row["batch"] for row in ran}, reverse=True)[:steps],
        )
        to_rollback = sorted(
            (row for row in ran if row["batch"] in target_batches),
            key=lambda row: row["id"],
            reverse=True,
        )

        discovered = self.__discover()
        rolled_back: list[str] = []
        for row in to_rollback:
            name = row["migration"]
            migration_cls = discovered.get(name)
            if migration_cls is None:
                error_msg = f"Migration class for '{name}' could not be found."
                raise MigrationNotFoundException(error_msg)

            if on_start is not None:
                on_start(name)

            started_at = time.perf_counter()
            try:
                instance = migration_cls()
                await instance.down()
                await self.__deleteRecord(connection, name)
            except Exception:
                if on_error is not None:
                    on_error(name, time.perf_counter() - started_at)
                raise

            if on_success is not None:
                on_success(name, time.perf_counter() - started_at)
            rolled_back.append(name)

        return rolled_back

    def __migrationsPath(self) -> "Path":
        """
        Return the directory holding migration files.

        Returns
        -------
        Path
            Absolute path to the ``database/migrations``
            directory under the application base path.
        """
        return self.__app.path("database") / "migrations"

    def __discover(self) -> dict[str, type[Migration]]:
        """
        Discover migration classes defined under the migrations directory.

        The result is cached on the instance after the first call, since
        the migrations directory does not change during a process
        lifetime and discovery involves filesystem traversal, module
        imports, and reflection.

        Returns
        -------
        dict of str to type
            Migration classes keyed by module file stem, ordered
            chronologically (filenames are zero-padded sequential ids).
        """
        # Reuse the previously discovered migrations, if any.
        if self.__discovered_cache is not None:
            return self.__discovered_cache

        migrations_path = self.__migrationsPath()
        if not migrations_path.is_dir():
            self.__discovered_cache = {}
            return self.__discovered_cache

        modules = ModuleInspector.discoverModules(
            base_path=self.__app.basePath,
            target_path=migrations_path,
        )

        found: dict[str, type[Migration]] = {}
        for module_name in modules:
            rf_module = ReflectionModule(module_name)
            for obj in rf_module.getClasses().values():
                if issubclass(obj, Migration) and obj is not Migration:
                    found[module_name.rsplit(".", 1)[-1]] = obj

        self.__discovered_cache = dict(sorted(found.items()))
        return self.__discovered_cache

    async def __ensureMigrationsTable(self, connection: IConnection) -> None:
        """
        Create the migrations tracking table if it does not already exist.

        Parameters
        ----------
        connection : IConnection
            Connection used to perform the schema operation.

        Returns
        -------
        None
            This method does not return a value.
        """
        await connection.createTable(_MIGRATIONS_TABLE_DEFINITION)

    async def __getRan(self, connection: IConnection) -> list[dict[str, Any]]:
        """
        Return every recorded migration, ordered by application order.

        Parameters
        ----------
        connection : IConnection
            Connection used to run the query.

        Returns
        -------
        list of dict
            Rows with ``id``, ``migration``, and ``batch`` keys.
        """
        return await connection.select(
            f"""
            SELECT id, migration, batch FROM {_MIGRATIONS_TABLE}
            ORDER BY id ASC
            """,
        )

    def __nextBatch(self, ran: list[dict[str, Any]]) -> int:
        """
        Compute the batch number to assign to a new migration run.

        Parameters
        ----------
        ran : list of dict
            Previously recorded migrations.

        Returns
        -------
        int
            ``1`` when nothing has run yet, otherwise the highest
            recorded batch plus one.
        """
        if not ran:
            return 1
        return max(row["batch"] for row in ran) + 1

    async def __insertRecord(
        self,
        connection: IConnection,
        name: str,
        batch: int,
    ) -> None:
        """
        Record a migration as applied.

        Parameters
        ----------
        connection : IConnection
            Connection used to run the statement.
        name : str
            Migration name to record.
        batch : int
            Batch number the migration belongs to.

        Returns
        -------
        None
            This method does not return a value.
        """
        await connection.execute(
            f"""
            INSERT INTO {_MIGRATIONS_TABLE}
            (migration, batch, migrated_at)
            VALUES (:migration, :batch, :migrated_at)
            """,
            {"migration": name, "batch": batch, "migrated_at": int(time.time())},
        )

    async def __deleteRecord(self, connection: IConnection, name: str) -> None:
        """
        Remove a migration's tracking record.

        Parameters
        ----------
        connection : IConnection
            Connection used to run the statement.
        name : str
            Migration name to remove.

        Returns
        -------
        None
            This method does not return a value.
        """
        await connection.execute(
            f"""
            DELETE FROM {_MIGRATIONS_TABLE} WHERE migration = :migration
            """,
            {"migration": name},
        )
