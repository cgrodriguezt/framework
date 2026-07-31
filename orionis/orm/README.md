# Orionis ORM

> Async-first Active Record ORM for the Orionis Framework — an Eloquent-like
> developer experience with a fully independent architecture.
>
> 🇪🇸 Versión en español: [README.es.md](README.es.md)

The public API is 100 % Orionis-owned. SQLAlchemy Core is used internally
**only** as the SQL generation/execution engine and never leaks into user
code: queries accept and return framework types exclusively (`Model`,
`Collection`, `Paginator`, `dict`, `int`).

---

## Table of contents

1. [Architecture](#architecture)
2. [Supported databases](#supported-databases)
3. [Configuration](#configuration)
4. [The database layer](#the-database-layer)
   - [Connection manager and the `DB` facade](#connection-manager-and-the-db-facade)
   - [Raw queries](#raw-queries)
   - [Transactions](#transactions)
5. [Defining models](#defining-models)
   - [Column types](#column-types)
   - [Column constraints](#column-constraints)
   - [Conventions and model configuration](#conventions-and-model-configuration)
6. [CRUD operations](#crud-operations)
7. [Query Builder](#query-builder)
8. [Aggregates](#aggregates)
9. [Pagination](#pagination)
10. [Attributes, casts, and serialization](#attributes-casts-and-serialization)
11. [Model state tracking](#model-state-tracking)
12. [Exceptions](#exceptions)
13. [Testing utilities](#testing-utilities)
14. [v1 scope and roadmap](#v1-scope-and-roadmap)

---

## Architecture

The dependency direction is strict and enforced by design:

```
Model
  │
  ▼
ModelQueryBuilder ──► Query IR (SelectPlan / InsertPlan / UpdatePlan / DeletePlan)
  │                       (pure dataclasses — zero SQL engine imports)
  ▼
Connection
  │
  ▼
SQLCompiler ──► SQLAlchemy Core (internal only) ──► Database
```

| Layer | Package | Responsibility |
| --- | --- | --- |
| Model | `orionis/orm/model.py` | Active Record API, attributes, persistence |
| Metaclass | `orionis/orm/metaclass.py` | Column discovery, table naming, metadata |
| Query Builder | `orionis/orm/query/builder.py` | Fluent, chainable query construction |
| Query IR | `orionis/orm/query/expressions.py` | Engine-agnostic query plans (value objects) |
| Schema | `orionis/orm/schema/` | Column types, constraints, table definitions |
| Resolver | `orionis/orm/resolver.py` | Static bridge Model → ConnectionManager |
| Connection manager | `orionis/database/connection_manager.py` | Registry, cache, and lifecycle of connections |
| Connection | `orionis/database/connection.py` | Plan/raw-SQL execution, transactions |
| Compiler | `orionis/database/compiler.py` | Query IR → executable SQL statements |
| Dialect | `orionis/database/dialect.py` | Driver URLs, engine options, PRAGMAs |

The ORM is wired automatically by `DatabaseProvider` (registered in the
framework core providers): it binds `IConnectionManager` as a singleton,
installs it into `ConnectionResolver` (so models resolve connections without
touching the container), and pins the `DB` facade.

## Supported databases

| Driver name | Database | Async driver | Install |
| --- | --- | --- | --- |
| `sqlite` | SQLite | `aiosqlite` | included |
| `mysql` | MySQL / MariaDB | `aiomysql` | `pip install orionis[mysql]` |
| `pgsql` | PostgreSQL | `asyncpg` | `pip install orionis[pgsql]` |
| `oracle` | Oracle Database | `oracledb` | `pip install orionis[oracle]` |
| `sqlserver` | Microsoft SQL Server | `aioodbc` | `pip install orionis[sqlserver]` |

Install every driver at once with `pip install orionis[database]`.
If a driver package is missing, the connection raises
`MissingDatabaseDependencyException` with the exact install hint.

## Configuration

Connections are declared in `config/database.py` through validated entities:

```python
from orionis.foundation.config.database.entities.database import Database

@dataclass(frozen=True, kw_only=True)
class BootstrapDatabase(Database):
    default: str = field(default_factory=lambda: Env.get("DB_CONNECTION", "sqlite"))
    connections: Connections | dict = field(
        default_factory=lambda: Connections(
            sqlite=SQLite(...),
            mysql=MySQL(...),
            pgsql=PGSQL(...),
            oracle=Oracle(...),
            sqlserver=SQLServer(...),
        ),
    )
```

Highlights per driver:

- **SQLite** — file path or `:memory:`; `foreign_key_constraints`,
  `busy_timeout`, `journal_mode`, and `synchronous` are applied as PRAGMAs on
  every pooled connection. In-memory databases automatically share a single
  pooled connection. The informational `url` key is not used by the async
  engine: the connection is always built from `database`.
- **MySQL** — `charset` and `unix_socket` travel in the URL; `collation`
  is applied per connection with `SET NAMES ... COLLATE ...`, and `strict`
  toggles the strict `sql_mode` preset (Laravel-compatible flags).
- **PostgreSQL** — `sslmode` is forwarded to `asyncpg` (`disable`, `prefer`,
  `require`, `verify-ca`, `verify-full`); `charset` and `search_path` are
  applied as `client_encoding` / `search_path` server settings.
- **Oracle** — addressing by `service_name`, `sid`, or a full `dsn`/`tns_name`
  (passed through driver connect arguments). `encoding`/`nencoding` are kept
  for compatibility: python-oracledb (thin mode) always uses UTF-8.
- **SQL Server** — `odbc_driver` (defaults to *ODBC Driver 18 for SQL
  Server*), `encrypt`, and `trust_server_certificate` are normalized to the
  ODBC `yes`/`no` convention.

`prefix_indexes` and the MySQL `engine` option are DDL-time settings reserved
for the upcoming migration system.

## The database layer

### Connection manager and the `DB` facade

```python
from orionis.support.facades import DB

connection = DB.connection()             # default connection
replica    = DB.connection("pgsql")      # named connection

DB.addConnection("audit", {"driver": "sqlite", "database": "audit.sqlite"})
DB.hasConnection("audit")                # True
DB.getDefaultName()                      # "sqlite"
DB.setDefaultName("pgsql")
await DB.disconnect()                    # dispose one or every engine
```

Connections are created lazily on first use and cached per name. Each
connection owns its SQL compiler configured with the connection `prefix`.

### Raw queries

Every method returns plain Python values — never engine objects:

```python
rows = await connection.select(
    "SELECT * FROM users WHERE id = :id", {"id": 1},
)                                            # -> list[dict]

affected = await connection.execute(
    "UPDATE users SET active = :active", {"active": True},
)                                            # -> int (row count)

await connection.statement("DROP VIEW IF EXISTS report")   # -> bool (DDL)
```

Raw statements use named `:param` placeholders and are always executed with
bound parameters (no string interpolation, no SQL injection surface).

### Transactions

Transactions are **task-local** (safe under asyncio concurrency) and support
nesting through savepoints:

```python
# Context manager: commits on success, rolls back on exception.
async with connection.transaction():
    await Order.create({...})

    async with connection.transaction():   # nested -> SAVEPOINT
        await Line.create({...})

# Explicit control:
await connection.begin()
try:
    ...
    await connection.commit()
except Exception:
    await connection.rollback()
    raise

connection.inTransaction()   # -> bool
```

## Defining models

```python
from orionis.orm import Boolean, Integer, Model, String, Timestamp


class User(Model):
    id = Integer().primary().autoIncrement()
    name = String()
    email = String(150).unique()
    active = Boolean().default(True)
    created_at = Timestamp().nullable()
    updated_at = Timestamp().nullable()

    casts = {"active": "bool"}
    hidden = ["email"]
```

### Column types

| Type | Description |
| --- | --- |
| `Integer()` | 32-bit integer |
| `BigInteger()` | 64-bit integer |
| `SmallInteger()` | 16-bit integer |
| `String(length=255)` | Bounded VARCHAR |
| `Text()` | Unbounded text |
| `Boolean()` | Boolean |
| `Float()` | Floating point |
| `Decimal(precision=10, scale=2)` | Fixed precision numeric |
| `Date()` / `Time()` / `DateTime()` | Temporal (naive) |
| `Timestamp()` | Timezone-aware timestamp |
| `JSON()` | JSON document |
| `UUID()` | Universally unique identifier |
| `Binary()` | Raw bytes |
| `Enum("a", "b", ...)` | String-backed enumeration |

### Column constraints

All constraints are fluent and chainable:

```python
id        = Integer().primary().autoIncrement()
email     = String().unique().index()
bio       = Text().nullable()
status    = String().default("draft")          # value or zero-arg callable
companyId = Integer().foreign("companies.id")  # "table.column"
```

### Conventions and model configuration

| Attribute | Default | Meaning |
| --- | --- | --- |
| `table` | pluralized snake_case class name (`User` → `users`, `Category` → `categories`, `Box` → `boxes`) | physical table name |
| `connection` | `None` (default connection) | named connection for the model |
| `primaryKey` | primary column flag, else `"id"` | primary key name |
| `incrementing` | `True` | adopt the DB-generated key after insert |
| `timestamps` | `True` | maintain `created_at` / `updated_at` automatically |
| `CREATED_AT` / `UPDATED_AT` | `"created_at"` / `"updated_at"` | timestamp column names |
| `fillable` | `[]` | mass assignment whitelist |
| `guarded` | `[]` (supports `"*"`) | mass assignment blacklist |
| `hidden` | `[]` | attributes omitted from serialization |
| `casts` | `{}` | attribute casts (see below) |

Abstract bases are supported: declare `__abstract__ = True` and its columns
and casts are inherited by concrete children.

## CRUD operations

```python
# Create
user = await User.create({"name": "John"})

# Read
users  = await User.all()                   # Collection
user   = await User.find(1)                 # Model | None
user   = await User.findOrFail(1)           # raises ModelNotFoundException
first  = await User.first()
first  = await User.firstOrFail()

# Update (instance)
user = await User.find(1)
await user.update({"name": "Peter"})        # fill + save
user.name = "Peter"                          # direct assignment
await user.save()                            # writes only dirty attributes

# Delete
await user.delete()                          # -> bool
await User.destroy(1, 2, 3)                  # -> int (deleted rows)
```

`save()` inserts new models (adopting the generated primary key) and updates
existing ones writing **only** the dirty attributes.

## Query Builder

Fully chainable; execution happens only at terminal methods:

```python
users = await User.where("active", True)\
    .orderBy("name")\
    .limit(20)\
    .get()
```

| Method | Notes |
| --- | --- |
| `select(*columns)` | restrict the projection |
| `where(col, value)` / `where(col, op, value)` / `where({...})` | operators: `=`, `!=`, `<>`, `<`, `<=`, `>`, `>=`, `like`, `not like`, `ilike`, `not ilike` |
| `orWhere(...)` | OR-combined condition |
| `whereIn(col, values)` / `whereNotIn(col, values)` | accepts iterables or `Collection` |
| `whereNull(col)` / `whereNotNull(col)` | NULL checks |
| `whereBetween(col, (min, max))` | range check |
| `whereLike(col, pattern)` / `whereNotLike(col, pattern)` | `%` / `_` wildcards |
| `whereILike(col, pattern)` / `whereNotILike(col, pattern)` | case-insensitive LIKE |
| `whereStartsWith(col, value)` / `whereEndsWith(col, value)` / `whereContains(col, value)` | literal prefix/suffix/substring match |
| `whereRegexpMatch(col, pattern)` | regular expression match (engine-dependent) |
| `distinct()` | collapse duplicate rows |
| `orderBy(col, "asc"\|"desc")` | ordering |
| `latest(col=None)` / `oldest(col=None)` | defaults to `created_at`, falls back to the primary key |
| `groupBy(*cols)` / `having(col, op, value)` | grouping |
| `limit(n)` / `take(n)` | max rows |
| `offset(n)` / `skip(n)` | skipped rows |

Terminals: `get()`, `first()`, `firstOrFail()`, `find(pk)`, `findOrFail(pk)`,
`paginate()`, `count()`, `exists()`, `doesntExist()`, `max()`, `min()`,
`avg()`, `sum()`, `insert()`, `update()`, `delete()`.

`where("col", None)` compiles to `IS NULL` (and `!=` to `IS NOT NULL`).
Mass `update()` refreshes `updated_at` automatically when the model keeps
timestamps.

## Aggregates

```python
total  = await User.count()                      # int
any_   = await User.where("active", True).exists()
none   = await User.where("active", True).doesntExist()
maxId  = await User.query().max("id")
minId  = await User.query().min("id")
avgAge = await User.query().avg("age")           # float | None
sumAge = await User.query().sum("age")           # 0 when empty
```

## Pagination

```python
page = await User.query().orderBy("id").paginate(page=2, perPage=15)

page.items          # Collection of models
page.total          # total rows across all pages
page.page           # current page (1-based)
page.perPage        # page size
page.lastPage       # last available page
page.hasNext        # bool
page.hasPrevious    # bool
page.toDict() / page.toJson()
```

Query results are always wrapped in the framework-wide
`orionis.support.types.collection.Collection` — never plain lists.

## Attributes, casts, and serialization

```python
user.fill({"name": "John"})       # honors fillable/guarded
user.getAttribute("name", "n/a")
user.toDict()                     # omits hidden attributes
user.toJson(indent=2)
user.only("id", "name")           # subset
user.except_("email")             # inverse subset (alias: exclude())
```

Available casts (applied on hydration **and** on assignment):

| Cast | Python type |
| --- | --- |
| `int` / `float` / `bool` | primitives (`"1"`, `"true"`, `"on"` → `True`) |
| `datetime` | `datetime` (ISO strings and POSIX timestamps accepted) |
| `date` | `date` |
| `json` | decoded structure (`dict` / `list`) |
| `uuid` | `uuid.UUID` |

On persistence, JSON structures targeting non-JSON columns are serialized to
strings and `UUID` objects targeting non-UUID columns are stringified.

Mass assignment is strict: unknown attributes or guarded columns raise
`MassAssignmentException`. Direct assignment (`user.role = "x"`) bypasses
mass-assignment rules, mirroring Eloquent.

## Model state tracking

```python
user.isDirty()             # any change since last sync?
user.isDirty("name")       # scoped check
user.isClean()
user.getDirty()            # {"name": "Peter"}
user.getOriginal("name")   # value at hydration/last save
user.getOriginal()         # full snapshot
user.syncOriginal()        # adopt current values as original
user.wasChanged()          # did the last save write anything?
user.getChanges()          # attributes written by the last save
```

## Exceptions

| Exception | Raised when |
| --- | --- |
| `orionis.database.exceptions.DatabaseException` | base of the database layer |
| `ConnectionNotFoundException` | unknown connection name |
| `UnsupportedDriverException` | driver without implementation |
| `MissingDatabaseDependencyException` | async driver package not installed |
| `QueryException` | statement failed to compile/execute |
| `TransactionException` | invalid transaction control |
| `orionis.orm.exceptions.OrmException` | base of the ORM layer |
| `OrmConfigurationException` | ORM used before boot/wiring |
| `ModelNotFoundException` | `findOrFail` / `firstOrFail` misses |
| `MassAssignmentException` | fillable/guarded violation |
| `InvalidQueryException` | invalid builder arguments |

## Testing utilities

Connections expose schema helpers (also the foundation for future
migrations):

```python
await connection.createTable(User.__meta__.table)   # CREATE TABLE IF NOT EXISTS
await connection.dropTable("users")                 # DROP TABLE IF EXISTS
```

Wiring an isolated ORM in tests takes three lines:

```python
manager = ConnectionManager(stub_app)        # sqlite :memory: config
ConnectionResolver.setManager(manager)
await manager.connection().createTable(User.__meta__.table)
# ... assertions ...
ConnectionResolver.clear()
```

## v1 scope and roadmap

v1 delivers the stable foundation: connections, transactions, schema types,
models, query builder, aggregates, collections, pagination, state tracking,
and casts. The query IR and the decoupled compiler are designed so that
relationships, eager loading, scopes, migrations, seeders, and factories can
be added without breaking changes.
