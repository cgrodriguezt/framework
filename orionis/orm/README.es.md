# ORM de Orionis

> ORM Active Record async-first para Orionis Framework — una experiencia de
> desarrollo tipo Eloquent con una arquitectura completamente propia.
>
> 🇬🇧 English version: [README.md](README.md)

La API pública pertenece 100 % a Orionis. SQLAlchemy Core se usa internamente
**solo** como motor de generación/ejecución de SQL y nunca se filtra al código
de usuario: las consultas aceptan y devuelven exclusivamente tipos del
framework (`Model`, `Collection`, `Paginator`, `dict`, `int`).

---

## Tabla de contenidos

1. [Arquitectura](#arquitectura)
2. [Bases de datos soportadas](#bases-de-datos-soportadas)
3. [Configuración](#configuración)
4. [La capa de base de datos](#la-capa-de-base-de-datos)
   - [Gestor de conexiones y la facade `DB`](#gestor-de-conexiones-y-la-facade-db)
   - [Consultas crudas](#consultas-crudas)
   - [Transacciones](#transacciones)
5. [Definición de modelos](#definición-de-modelos)
   - [Tipos de columna](#tipos-de-columna)
   - [Restricciones de columna](#restricciones-de-columna)
   - [Convenciones y configuración del modelo](#convenciones-y-configuración-del-modelo)
6. [Operaciones CRUD](#operaciones-crud)
7. [Query Builder](#query-builder)
8. [Agregados](#agregados)
9. [Paginación](#paginación)
10. [Atributos, casts y serialización](#atributos-casts-y-serialización)
11. [Seguimiento de estado del modelo](#seguimiento-de-estado-del-modelo)
12. [Excepciones](#excepciones)
13. [Utilidades para pruebas](#utilidades-para-pruebas)
14. [Alcance v1 y hoja de ruta](#alcance-v1-y-hoja-de-ruta)

---

## Arquitectura

La dirección de dependencias es estricta y está garantizada por diseño:

```
Model
  │
  ▼
ModelQueryBuilder ──► IR de consultas (SelectPlan / InsertPlan / UpdatePlan / DeletePlan)
  │                       (dataclasses puras — cero imports del motor SQL)
  ▼
Connection
  │
  ▼
SQLCompiler ──► SQLAlchemy Core (solo interno) ──► Base de datos
```

| Capa | Paquete | Responsabilidad |
| --- | --- | --- |
| Model | `orionis/orm/model.py` | API Active Record, atributos, persistencia |
| Metaclase | `orionis/orm/metaclass.py` | Descubrimiento de columnas, nombre de tabla, metadatos |
| Query Builder | `orionis/orm/query/builder.py` | Construcción fluida y encadenable de consultas |
| IR de consultas | `orionis/orm/query/expressions.py` | Planes agnósticos del motor (objetos de valor) |
| Schema | `orionis/orm/schema/` | Tipos de columna, restricciones, definiciones de tabla |
| Resolver | `orionis/orm/resolver.py` | Puente estático Model → ConnectionManager |
| Gestor de conexiones | `orionis/database/connection_manager.py` | Registro, caché y ciclo de vida de conexiones |
| Connection | `orionis/database/connection.py` | Ejecución de planes/SQL crudo, transacciones |
| Compilador | `orionis/database/compiler.py` | IR de consultas → sentencias SQL ejecutables |
| Dialecto | `orionis/database/dialect.py` | URLs por driver, opciones de motor, PRAGMAs |

El ORM se cablea automáticamente con `DatabaseProvider` (registrado en los
core providers del framework): vincula `IConnectionManager` como singleton, lo
instala en `ConnectionResolver` (los modelos resuelven conexiones sin tocar el
contenedor) y hace pin de la facade `DB`.

## Bases de datos soportadas

| Nombre del driver | Base de datos | Driver async | Instalación |
| --- | --- | --- | --- |
| `sqlite` | SQLite | `aiosqlite` | incluido |
| `mysql` | MySQL / MariaDB | `aiomysql` | `pip install orionis[mysql]` |
| `pgsql` | PostgreSQL | `asyncpg` | `pip install orionis[pgsql]` |
| `oracle` | Oracle Database | `oracledb` | `pip install orionis[oracle]` |
| `sqlserver` | Microsoft SQL Server | `aioodbc` | `pip install orionis[sqlserver]` |

Instala todos los drivers a la vez con `pip install orionis[database]`.
Si falta el paquete de un driver, la conexión lanza
`MissingDatabaseDependencyException` con la instrucción exacta de instalación.

## Configuración

Las conexiones se declaran en `config/database.py` mediante entidades
validadas:

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

Detalles por driver:

- **SQLite** — ruta de archivo o `:memory:`; `foreign_key_constraints`,
  `busy_timeout`, `journal_mode` y `synchronous` se aplican como PRAGMAs en
  cada conexión del pool. Las bases en memoria comparten automáticamente una
  única conexión del pool. La clave informativa `url` no la usa el motor
  async: la conexión se construye siempre desde `database`.
- **MySQL** — `charset` y `unix_socket` viajan en la URL; `collation` se
  aplica por conexión con `SET NAMES ... COLLATE ...`, y `strict` activa el
  preset estricto de `sql_mode` (flags compatibles con Laravel).
- **PostgreSQL** — `sslmode` se reenvía a `asyncpg` (`disable`, `prefer`,
  `require`, `verify-ca`, `verify-full`); `charset` y `search_path` se
  aplican como server settings `client_encoding` / `search_path`.
- **Oracle** — direccionamiento por `service_name`, `sid`, o `dsn`/`tns_name`
  completos (pasados como argumentos de conexión del driver).
  `encoding`/`nencoding` se conservan por compatibilidad: python-oracledb
  (modo thin) siempre usa UTF-8.
- **SQL Server** — `odbc_driver` (por defecto *ODBC Driver 18 for SQL
  Server*), `encrypt` y `trust_server_certificate` se normalizan a la
  convención ODBC `yes`/`no`.

`prefix_indexes` y la opción `engine` de MySQL son ajustes de DDL reservados
para el próximo sistema de migraciones.

## La capa de base de datos

### Gestor de conexiones y la facade `DB`

```python
from orionis.support.facades import DB

connection = DB.connection()             # conexión por defecto
replica    = DB.connection("pgsql")      # conexión nombrada

DB.addConnection("audit", {"driver": "sqlite", "database": "audit.sqlite"})
DB.hasConnection("audit")                # True
DB.getDefaultName()                      # "sqlite"
DB.setDefaultName("pgsql")
await DB.disconnect()                    # libera uno o todos los motores
```

Las conexiones se crean de forma perezosa en el primer uso y se cachean por
nombre. Cada conexión posee su compilador SQL configurado con el `prefix` de
la conexión.

### Consultas crudas

Cada método devuelve valores Python planos — nunca objetos del motor:

```python
rows = await connection.select(
    "SELECT * FROM users WHERE id = :id", {"id": 1},
)                                            # -> list[dict]

affected = await connection.execute(
    "UPDATE users SET active = :active", {"active": True},
)                                            # -> int (filas afectadas)

await connection.statement("DROP VIEW IF EXISTS report")   # -> bool (DDL)
```

Las sentencias crudas usan placeholders con nombre `:param` y siempre se
ejecutan con parámetros vinculados (sin interpolación de cadenas, sin
superficie de inyección SQL).

### Transacciones

Las transacciones son **task-local** (seguras bajo concurrencia asyncio) y
soportan anidamiento mediante savepoints:

```python
# Context manager: commit al salir bien, rollback ante excepción.
async with connection.transaction():
    await Order.create({...})

    async with connection.transaction():   # anidada -> SAVEPOINT
        await Line.create({...})

# Control explícito:
await connection.begin()
try:
    ...
    await connection.commit()
except Exception:
    await connection.rollback()
    raise

connection.inTransaction()   # -> bool
```

## Definición de modelos

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

### Tipos de columna

| Tipo | Descripción |
| --- | --- |
| `Integer()` | Entero de 32 bits |
| `BigInteger()` | Entero de 64 bits |
| `SmallInteger()` | Entero de 16 bits |
| `String(length=255)` | VARCHAR acotado |
| `Text()` | Texto sin límite |
| `Boolean()` | Booleano |
| `Float()` | Punto flotante |
| `Decimal(precision=10, scale=2)` | Numérico de precisión fija |
| `Date()` / `Time()` / `DateTime()` | Temporales (naive) |
| `Timestamp()` | Timestamp con zona horaria |
| `JSON()` | Documento JSON |
| `UUID()` | Identificador único universal |
| `Binary()` | Bytes crudos |
| `Enum("a", "b", ...)` | Enumeración respaldada por cadenas |

### Restricciones de columna

Todas las restricciones son fluidas y encadenables:

```python
id        = Integer().primary().autoIncrement()
email     = String().unique().index()
bio       = Text().nullable()
status    = String().default("draft")          # valor o callable sin argumentos
companyId = Integer().foreign("companies.id")  # "tabla.columna"
```

### Convenciones y configuración del modelo

| Atributo | Por defecto | Significado |
| --- | --- | --- |
| `table` | snake_case pluralizado del nombre de la clase (`User` → `users`, `Category` → `categories`, `Box` → `boxes`) | nombre físico de la tabla |
| `connection` | `None` (conexión por defecto) | conexión nombrada del modelo |
| `primaryKey` | columna marcada `primary()`, en su defecto `"id"` | nombre de la clave primaria |
| `incrementing` | `True` | adopta la clave generada por la BD tras el insert |
| `timestamps` | `True` | mantiene `created_at` / `updated_at` automáticamente |
| `CREATED_AT` / `UPDATED_AT` | `"created_at"` / `"updated_at"` | nombres de las columnas de timestamps |
| `fillable` | `[]` | lista blanca de asignación masiva |
| `guarded` | `[]` (soporta `"*"`) | lista negra de asignación masiva |
| `hidden` | `[]` | atributos omitidos en la serialización |
| `casts` | `{}` | conversiones de atributos (ver abajo) |

Se soportan bases abstractas: declara `__abstract__ = True` y sus columnas y
casts se heredan en los hijos concretos.

## Operaciones CRUD

```python
# Crear
user = await User.create({"name": "John"})

# Leer
users  = await User.all()                   # Collection
user   = await User.find(1)                 # Model | None
user   = await User.findOrFail(1)           # lanza ModelNotFoundException
first  = await User.first()
first  = await User.firstOrFail()

# Actualizar (instancia)
user = await User.find(1)
await user.update({"name": "Peter"})        # fill + save
user.name = "Peter"                          # asignación directa
await user.save()                            # escribe solo atributos sucios

# Eliminar
await user.delete()                          # -> bool
await User.destroy(1, 2, 3)                  # -> int (filas eliminadas)
```

`save()` inserta modelos nuevos (adoptando la clave primaria generada) y
actualiza los existentes escribiendo **solo** los atributos sucios.

## Query Builder

Totalmente encadenable; la ejecución ocurre solo en los métodos terminales:

```python
users = await User.where("active", True)\
    .orderBy("name")\
    .limit(20)\
    .get()
```

| Método | Notas |
| --- | --- |
| `select(*columns)` | restringe la proyección |
| `where(col, valor)` / `where(col, op, valor)` / `where({...})` | operadores: `=`, `!=`, `<>`, `<`, `<=`, `>`, `>=`, `like`, `not like`, `ilike`, `not ilike` |
| `orWhere(...)` | condición combinada con OR |
| `whereIn(col, valores)` / `whereNotIn(col, valores)` | acepta iterables o `Collection` |
| `whereNull(col)` / `whereNotNull(col)` | comprobaciones de NULL |
| `whereBetween(col, (min, max))` | rango |
| `whereLike(col, patrón)` / `whereNotLike(col, patrón)` | comodines `%` / `_` |
| `whereILike(col, patrón)` / `whereNotILike(col, patrón)` | LIKE sin distinguir mayúsculas |
| `whereStartsWith(col, valor)` / `whereEndsWith(col, valor)` / `whereContains(col, valor)` | coincidencia literal de prefijo/sufijo/subcadena |
| `whereRegexpMatch(col, patrón)` | coincidencia de expresión regular (según el motor) |
| `distinct()` | descarta filas duplicadas |
| `orderBy(col, "asc"\|"desc")` | ordenación |
| `latest(col=None)` / `oldest(col=None)` | por defecto `created_at`, si no existe usa la clave primaria |
| `groupBy(*cols)` / `having(col, op, valor)` | agrupación |
| `limit(n)` / `take(n)` | máximo de filas |
| `offset(n)` / `skip(n)` | filas omitidas |

Terminales: `get()`, `first()`, `firstOrFail()`, `find(pk)`, `findOrFail(pk)`,
`paginate()`, `count()`, `exists()`, `doesntExist()`, `max()`, `min()`,
`avg()`, `sum()`, `insert()`, `update()`, `delete()`.

`where("col", None)` compila a `IS NULL` (y `!=` a `IS NOT NULL`).
El `update()` masivo refresca `updated_at` automáticamente cuando el modelo
mantiene timestamps.

## Agregados

```python
total  = await User.count()                      # int
hay    = await User.where("active", True).exists()
no_hay = await User.where("active", True).doesntExist()
maxId  = await User.query().max("id")
minId  = await User.query().min("id")
media  = await User.query().avg("age")           # float | None
suma   = await User.query().sum("age")           # 0 si no hay filas
```

## Paginación

```python
page = await User.query().orderBy("id").paginate(page=2, perPage=15)

page.items          # Collection de modelos
page.total          # total de filas en todas las páginas
page.page           # página actual (base 1)
page.perPage        # tamaño de página
page.lastPage       # última página disponible
page.hasNext        # bool
page.hasPrevious    # bool
page.toDict() / page.toJson()
```

Los resultados de consulta siempre se envuelven en la
`orionis.support.types.collection.Collection` del framework — nunca listas
planas.

## Atributos, casts y serialización

```python
user.fill({"name": "John"})       # respeta fillable/guarded
user.getAttribute("name", "n/a")
user.toDict()                     # omite atributos hidden
user.toJson(indent=2)
user.only("id", "name")           # subconjunto
user.except_("email")             # subconjunto inverso (alias: exclude())
```

Casts disponibles (aplicados en hidratación **y** en asignación):

| Cast | Tipo Python |
| --- | --- |
| `int` / `float` / `bool` | primitivos (`"1"`, `"true"`, `"on"` → `True`) |
| `datetime` | `datetime` (acepta cadenas ISO y timestamps POSIX) |
| `date` | `date` |
| `json` | estructura decodificada (`dict` / `list`) |
| `uuid` | `uuid.UUID` |

Al persistir, las estructuras JSON destinadas a columnas no-JSON se
serializan a cadenas y los objetos `UUID` destinados a columnas no-UUID se
convierten a `str`.

La asignación masiva es estricta: atributos desconocidos o columnas
protegidas lanzan `MassAssignmentException`. La asignación directa
(`user.role = "x"`) omite las reglas de asignación masiva, igual que en
Eloquent.

## Seguimiento de estado del modelo

```python
user.isDirty()             # ¿algún cambio desde la última sincronización?
user.isDirty("name")       # comprobación acotada
user.isClean()
user.getDirty()            # {"name": "Peter"}
user.getOriginal("name")   # valor en la hidratación/último save
user.getOriginal()         # snapshot completo
user.syncOriginal()        # adopta los valores actuales como originales
user.wasChanged()          # ¿el último save escribió algo?
user.getChanges()          # atributos escritos por el último save
```

## Excepciones

| Excepción | Se lanza cuando |
| --- | --- |
| `orionis.database.exceptions.DatabaseException` | base de la capa de base de datos |
| `ConnectionNotFoundException` | nombre de conexión desconocido |
| `UnsupportedDriverException` | driver sin implementación |
| `MissingDatabaseDependencyException` | paquete del driver async no instalado |
| `QueryException` | fallo al compilar/ejecutar la sentencia |
| `TransactionException` | control de transacción inválido |
| `orionis.orm.exceptions.OrmException` | base de la capa ORM |
| `OrmConfigurationException` | ORM usado antes del boot/cableado |
| `ModelNotFoundException` | `findOrFail` / `firstOrFail` sin resultados |
| `MassAssignmentException` | violación de fillable/guarded |
| `InvalidQueryException` | argumentos inválidos del builder |

## Utilidades para pruebas

Las conexiones exponen helpers de esquema (también la base de las futuras
migraciones):

```python
await connection.createTable(User.__meta__.table)   # CREATE TABLE IF NOT EXISTS
await connection.dropTable("users")                 # DROP TABLE IF EXISTS
```

Cablear un ORM aislado en pruebas requiere tres líneas:

```python
manager = ConnectionManager(stub_app)        # config sqlite :memory:
ConnectionResolver.setManager(manager)
await manager.connection().createTable(User.__meta__.table)
# ... aserciones ...
ConnectionResolver.clear()
```

## Alcance v1 y hoja de ruta

La v1 entrega la base estable: conexiones, transacciones, tipos de esquema,
modelos, query builder, agregados, colecciones, paginación, seguimiento de
estado y casts. El IR de consultas y el compilador desacoplado están
diseñados para incorporar relaciones, eager loading, scopes, migraciones,
seeders y factories sin cambios incompatibles.
