from typing import TYPE_CHECKING, Self
from orionis.database.contracts.connection import IConnection
from orionis.database.contracts.manager import IConnectionManager
from orionis.database.contracts.schema import ISchema
from orionis.database.schema.column import Column
from orionis.database.schema.comment import Comment
from orionis.database.schema.definition_bucket import DefinitionBucket
from orionis.database.schema.foreign import ForeignKey
from orionis.database.schema.index import Index
from orionis.database.schema.primary import PrimaryKey
from orionis.database.schema.table_creation import TableCreation
from orionis.database.schema.timestamp import Timestamps
from orionis.database.schema.unique import Unique
from orionis.orm.schema.table import TableDefinition

if TYPE_CHECKING:
    from orionis.database.schema.definitions import SchemaDefinition
    from orionis.orm.schema.column import ColumnDefinition

class Schema(ISchema):

    # ruff: noqa: TC001

    # Number of dot-separated parts in a "schema.table" identifier.
    __SCHEMA_TABLE_PARTS: int = 2

    def __init__(self, conn_manager: IConnectionManager) -> None:
        """Initialize the Schema instance.

        Parameters
        ----------
        conn_manager : IConnectionManager
            The connection manager for database operations.

        Returns
        -------
        None
        """
        # Initialize connection manager and state attributes
        self.__conn_manager: IConnectionManager = conn_manager
        self.__connection_name: str | None = None

    def connection(self, name: str | None = None) -> Self:
        """Set the connection name for schema operations.

        Parameters
        ----------
        name : str | None, optional
            The connection name to use, by default None.

        Returns
        -------
        Self
            The current Schema instance for method chaining.

        Raises
        ------
        ValueError
            If connection name has already been defined.
        """
        # Prevent overwriting an already set connection name
        if self.__connection_name is not None:
            error_msg = "Connection name has already been defined."
            raise ValueError(error_msg)
        self.__connection_name = name
        return self

    def create(self, name: str, *definitions: "SchemaDefinition") -> TableCreation:
        """Create a new table with the given definitions.

        The result can be used two ways:

        - ``await schema.create(name, *definitions)`` creates the table
          immediately from the definitions passed here.
        - ``async with schema.create(name) as table:`` yields a
          :class:`~orionis.database.schema.blueprint.Blueprint` so columns
          can be declared fluently (``table.string("username")``,
          ``table.timestamps()``, ...); the table is created once the
          block exits without raising.

        Parameters
        ----------
        name : str
            The name of the table to create. If the table belongs to a
            non-default schema, use the ``schema.table`` format.
        *definitions : ColumnDefinition | Comment | ForeignKey | Index |
            PrimaryKey | Unique
            Variable length argument list of schema definitions
            (columns, constraints, indexes, etc.). Optional when the
            async context-manager form is used instead.

        Returns
        -------
        TableCreation
            Awaitable and async context manager that performs the
            creation.
        """
        return TableCreation(self, name, definitions)

    async def drop(self, name: str) -> bool:
        """Drop an existing table.

        Parameters
        ----------
        name : str
            The name of the table to drop. If the table belongs to a
            non-default schema, use the ``schema.table`` format.

        Returns
        -------
        bool
            ``True`` when the table is dropped without errors.
        """
        connection: IConnection = self.__resolveConnection()
        schema, table = self.__parseTableName(name)
        return await connection.dropTable(name=table, schema=schema)

    async def _createTable(
        self,
        name: str,
        definitions: tuple["SchemaDefinition", ...],
    ) -> bool:
        """Compile and execute the ``CREATE TABLE`` for ``name``.

        Parameters
        ----------
        name : str
            The name of the table to create.
        definitions : tuple
            Schema definitions collected for the table.

        Returns
        -------
        bool
            ``True`` when the table is created without errors.
        """
        connection: IConnection = self.__resolveConnection()
        return await connection.createTable(self.__buildTable(name, definitions))

    def __resolveConnection(self) -> IConnection:
        """Resolve the connection bound to the configured connection name.

        Returns
        -------
        IConnection
            The connection to use for schema operations.
        """
        # Reuse the connection manager already bound to this instance
        return self.__conn_manager.connection(self.__connection_name)

    def __buildTable(
        self,
        name: str,
        definitions: tuple["SchemaDefinition", ...],
    ) -> TableDefinition:
        """Build the table definition from a name and its definitions.

        Parameters
        ----------
        name : str
            The name of the table to build, possibly ``schema.table``.
        definitions : tuple
            Schema definitions collected for the table.

        Returns
        -------
        TableDefinition
            The complete table definition ready for compilation.
        """
        schema, table = self.__parseTableName(name)
        kwargs = self.__collectDefinitions(definitions)
        return TableDefinition(name=table, schema=schema, **kwargs)

    def __collectDefinitions(
        self,
        definitions: tuple[
            type[
                ColumnDefinition
                | Comment
                | ForeignKey
                | Index
                | PrimaryKey
                | Unique
            ],
            ...,
        ],
    ) -> dict[str, object]:
        """Group heterogeneous schema definitions into constructor kwargs.

        Parameters
        ----------
        definitions : tuple
            Column, constraint, index, and comment definitions to sort.

        Returns
        -------
        dict[str, object]
            Keyword arguments accepted by ``TableDefinition``.
        """
        # Accumulate in O(n); tuples for TableDefinition are built once.
        bucket = DefinitionBucket()
        for definition in definitions:
            self.__classifyDefinition(definition, bucket)

        # Apply primary keys declared via Column.primary() after the
        # loop, so duplicates against an explicit PrimaryKey() raise.
        if bucket.primary_columns:
            self.__setPrimaryKey(bucket.primary_columns, bucket.kwargs)

        bucket.kwargs["columns"] = bucket.columns
        # Omit empty collections so TableDefinition defaults apply.
        if bucket.unique_constraints:
            bucket.kwargs["unique_constraints"] = tuple(
                bucket.unique_constraints,
            )
        if bucket.foreign_keys:
            bucket.kwargs["foreign_keys"] = tuple(bucket.foreign_keys)
        if bucket.indexes:
            bucket.kwargs["indexes"] = tuple(bucket.indexes)
        return bucket.kwargs

    def __classifyDefinition(
        self,
        definition: (
            ColumnDefinition
            | Comment
            | ForeignKey
            | Index
            | PrimaryKey
            | Unique
        ),
        bucket: DefinitionBucket,
    ) -> None:
        """Route a single schema definition into the shared bucket.

        Parameters
        ----------
        definition : ColumnDefinition | Comment | ForeignKey | Index |
            PrimaryKey | Unique
            The schema definition to classify.
        bucket : DefinitionBucket
            Accumulator updated in place with the classified data.

        Returns
        -------
        None
            The ``bucket`` accumulator is mutated in place.
        """
        # Columns make up the bulk of a table's definitions, so they are
        # routed with a single membership check against the marker types.
        if not isinstance(
            definition,
            (Comment, Unique, ForeignKey, Index, PrimaryKey, Timestamps),
        ):
            bucket.columns[definition.name] = definition
            # Column-level .primary() also defines the primary key.
            if definition.is_primary:
                bucket.primary_columns.append(definition.name)
            return

        if isinstance(definition, Comment):
            bucket.kwargs["comment"] = definition.text
        elif isinstance(definition, Unique):
            bucket.unique_constraints.append(definition.constraint)
        elif isinstance(definition, ForeignKey):
            bucket.foreign_keys.append(definition.foreign)
        elif isinstance(definition, Index):
            bucket.indexes.append(definition.constraint)
        elif isinstance(definition, PrimaryKey):
            self.__setPrimaryKey(list(definition.columns), bucket.kwargs)
        else:
            self.__addTimestampColumns(definition, bucket)

    def __addTimestampColumns(
        self,
        definition: Timestamps,
        bucket: DefinitionBucket,
    ) -> None:
        """Expand a ``Timestamps`` marker into its two nullable columns.

        Parameters
        ----------
        definition : Timestamps
            The timestamps marker carrying the ``timezone`` flag.
        bucket : DefinitionBucket
            Accumulator updated in place with the new columns.

        Returns
        -------
        None
            The ``bucket`` accumulator is mutated in place.
        """
        for column_name in ("created_at", "updated_at"):
            column = Column.dateTime(column_name, timezone=definition.timezone)
            column.nullable()
            bucket.columns[column_name] = column

    def __setPrimaryKey(
        self,
        column_names: list[str],
        kwargs: dict[str, object],
    ) -> None:
        """Assign the primary key columns, rejecting duplicate definitions.

        Parameters
        ----------
        column_names : list[str]
            Names of the columns composing the primary key.
        kwargs : dict[str, object]
            Accumulated ``TableDefinition`` keyword arguments, updated
            in place.

        Returns
        -------
        None
            The ``kwargs`` mapping is mutated in place.

        Raises
        ------
        ValueError
            If a primary key was already defined.
        """
        if "primary_key" in kwargs or "composite_primary_key" in kwargs:
            error_msg = "Primary key has already been defined."
            raise ValueError(error_msg)
        # A single column keeps the simple form; more than one composes
        # a composite primary key instead.
        if len(column_names) > 1:
            kwargs["composite_primary_key"] = tuple(column_names)
        else:
            kwargs["primary_key"] = column_names[0]

    def __parseTableName(self, name: str) -> tuple[str | None, str]:
        """Parse the table name to extract schema and table components.

        Parameters
        ----------
        name : str
            The full table name, which may include a schema prefix.

        Returns
        -------
        tuple[str | None, str]
            A tuple containing the schema name (or None if not specified)
            and the table name.
        """
        parts = name.split(".")
        if len(parts) == self.__SCHEMA_TABLE_PARTS:
            return parts[0], parts[1]  # schema, table
        return None, parts[0]  # no schema, just table
