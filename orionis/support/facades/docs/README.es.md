# Facades de Orionis (`orionis.support.facades`)

> Proxies estáticos al estilo Laravel que exponen los singletons centrales
> del framework (caché, base de datos, cifrado, localización, logging,
> routing, scheduling, sesiones, storage, testing, vistas, el propio
> contenedor de la aplicación, y un helper independiente de fecha/hora)
> como clases simples que se importan y se llaman directamente.
>
> 🇬🇧 English version: [README.md](README.md)

`orionis.support.facades` es el punto de entrada público que usa el
código de la aplicación para acceder a servicios del framework **sin**
solicitarlos mediante inyección de dependencias en el constructor. Cada
clase de este paquete (excepto `DateTime`) es un proxy delgado: no
declara lógica de negocio propia y simplemente le indica a la maquinaria
`Facade` subyacente (`orionis.container.facades`) qué servicio del
contenedor representa.

---

## Tabla de contenidos

1. [Requisitos](#requisitos)
2. [Descripción funcional del módulo](#descripción-funcional-del-módulo)
3. [Cómo resuelve una llamada una facade](#cómo-resuelve-una-llamada-una-facade)
4. [Referencia de API](#referencia-de-api)
   - [Contrato base común](#contrato-base-común)
   - [Catálogo de facades](#catálogo-de-facades)
   - [`DateTime`](#datetime-orionissupportfacadesdatetimedatetime)
5. [Ejemplos de uso](#ejemplos-de-uso)
6. [Consideraciones de rendimiento y concurrencia](#consideraciones-de-rendimiento-y-concurrencia)
7. [Notas de diseño](#notas-de-diseño)
8. [Notas de compatibilidad](#notas-de-compatibilidad)

---

## Requisitos

No se necesita instalación adicional más allá del propio framework:

```bash
pip install orionis
```

- **Python:** 3.14 o superior.
- Todas las facades excepto `DateTime` requieren una instancia de
  `Application` (`orionis.foundation.application.Application`)
  **arrancada** antes de poder resolver nada — ver
  [Notas de diseño](#notas-de-diseño).
- `DateTime` además depende de `pendulum~=3.2` (una dependencia normal,
  no opcional, del framework).

## Descripción funcional del módulo

La mayoría de los servicios de Orionis se registran en el contenedor y
normalmente se obtienen mediante inyección en el constructor
(controladores, comandos, providers). Las facades existen para el caso
restante: código que quiere llamar a un servicio directamente —una
función auxiliar, un script, un global de plantilla, una llamada puntual
en un controlador— sin declarar un parámetro de constructor.

El paquete incluye dos tipos de clases:

- **Facades proxy** — `Application`, `Cache`, `Catch`, `DB`, `Crypt`
  (`encrypter.py`), `Lang`, `Log`, `Reactor`, `Route` (`router.py`),
  `Schedule`, `Session`, `Storage`, `Test`, `View`. Cada una hereda de
  `orionis.container.facades.facade.Facade` y sobrescribe exactamente un
  método, `getFacadeAccessor()`, para indicar qué servicio del contenedor
  proxya. Todo el comportamiento real vive en ese servicio resuelto; el
  cuerpo de la clase facade no aporta nada más en tiempo de ejecución.
- **`DateTime`** — la única clase de este paquete que **no** es una
  `Facade`. Es una utilidad simple, basada en `__slots__`, solo con
  classmethods, que envuelve `pendulum` directamente. Vive aquí por
  convención de ubicación/agrupación (junto a las demás herramientas de
  "acceso rápido"), no porque pase por el contenedor.

Cada facade proxy también incluye un archivo `*.pyi` correspondiente.
Esos stubs son **solo para el chequeo de tipos** —los inspeccionan los
IDEs/type checkers para ofrecer autocompletado de los métodos que expone
el contrato subyacente— y nunca se importan ni se ejecutan en tiempo de
ejecución. La clase real que importas solo define `getFacadeAccessor()`.

## Cómo resuelve una llamada una facade

El mecanismo de proxy en sí —`Facade`, `FacadeMeta`, `IFacade`— vive en
`orionis.container.facades` y está documentado en detalle en
[`orionis/container/docs/README.es.md`](../../../container/docs/README.es.md).
La versión resumida, repetida aquí por conveniencia:

1. Cada facade proxy de este paquete hereda de `Facade` e implementa
   `getFacadeAccessor() -> str | type`, devolviendo un alias de tipo
   cadena (p. ej. `"x-orionis-ILogger"`) o el propio tipo del contrato
   (p. ej. `ICacheManager`) que identifica al servicio vinculado en el
   contenedor.
2. **Acceso sin fijar** (el predeterminado): leer cualquier atributo en la
   clase facade —`Cache.get`, `Log.info`, `View.make`, ...— devuelve una
   función dispatcher asíncrona cacheada. Llamarla
   (`await Cache.get("key")`) resuelve el servicio de nuevo mediante
   `await FacadeClass.resolve()`
   (`Application().make(accessor, *args, **kwargs)`), busca el atributo
   solicitado en la instancia resuelta, lo invoca si es invocable
   (esperando el resultado si es awaitable), o lo devuelve tal cual si es
   un atributo simple. **En este modo toda llamada debe llevar `await`**,
   incluso para atributos que no son invocables.
3. **Acceso fijado (pinned)**: una vez que se llamó a
   `await FacadeClass.pin()` (esto es lo que hacen la mayoría de los
   `ServiceProvider.boot()` centrales — ver el
   [catálogo de facades](#catálogo-de-facades)), la clase cachea la
   instancia resuelta en `cls._pinned_instance`. Desde ese momento, el
   acceso a atributos es un `getattr(cls._pinned_instance, name)` directo
   y síncrono — sin búsqueda en el contenedor, sin `await` forzado para
   miembros síncronos. `FacadeClass.unpin()` limpia la caché y vuelve al
   modo dispatcher.
4. `resolve()` lanza `RuntimeError("Application not booted. Boot your app
   first.")` si la instancia compartida `Application()` aún no completó
   su secuencia de arranque.

## Referencia de API

### Contrato base común

Toda facade proxy hereda los mismos cuatro miembros de `Facade`
(`orionis.container.facades.facade.Facade`, contrato `IFacade`):

| Miembro | Firma | Descripción |
|---|---|---|
| `getFacadeAccessor` | `classmethod() -> str \| type` | Devuelve la clave del contenedor para el servicio proxiado. La implementación base lanza `NotImplementedError`; cada facade concreta de este paquete la sobrescribe. |
| `resolve` | `async classmethod(*args, **kwargs) -> object` | Resuelve el servicio subyacente desde el singleton compartido `Application()`. Lanza `RuntimeError` si la aplicación no ha sido arrancada. |
| `pin` | `async classmethod() -> None` | Resuelve el servicio una vez y lo cachea como instancia fijada, cambiando la facade a acceso directo y síncrono a atributos. |
| `unpin` | `classmethod() -> None` | Limpia la instancia fijada, devolviendo la facade al modo dispatcher (siempre con `await`). |

### Catálogo de facades

| Facade | Módulo | `getFacadeAccessor()` | Contrato proxiado | Fijada (pin) por | Docs |
|---|---|---|---|---|---|
| `Application` | `application.py` | `"x-orionis-IApplication"` | `IApplication` (+ `IContainer`) | Se autorregistra en `Application.create()`/boot (`self.instance(IApplication, self, alias="x-orionis-IApplication")`); ningún provider llama `pin()` sobre esta facade. | [`orionis/container/docs`](../../../container/docs/README.es.md) |
| `Cache` | `cache.py` | `ICacheManager` | `ICacheManager` | `orionis.cache.provider.CacheProvider.boot()` | *(módulo cache)* |
| `Catch` | `catch.py` | `"x-orionis-ICatch"` | `ICatch` | `orionis.failure.provider.CatchProvider.boot()` | *(módulo failure)* |
| `DateTime` | `datetime.py` | *n/a — no es una `Facade`* | *n/a* | *n/a* | ver [abajo](#datetime-orionissupportfacadesdatetimedatetime) |
| `DB` | `db.py` | `IConnectionManager` | `IConnectionManager` | `orionis.database.provider.DatabaseProvider.boot()` | *(módulo database)* |
| `Crypt` | `encrypter.py` | `IEncrypter` | `IEncrypter` | `orionis.encrypter.provider.EncrypterProvider.boot()` | [`orionis/encrypter/docs`](../../../encrypter/docs/README.es.md) |
| `Lang` | `lang.py` | `ITranslator` | `ITranslator` | `orionis.localization.provider.LocalizationProvider.boot()` | [`orionis/localization/docs`](../../../localization/docs/README.es.md) |
| `Log` | `logger.py` | `"x-orionis-ILogger"` | `ILogger` | `orionis.logging.provider.LoggerProvider.boot()` | [`orionis/logging/docs`](../../../logging/docs/README.es.md) |
| `Reactor` | `reactor.py` | `"x-orionis-IReactor"` | `IReactor` | `orionis.console.reactor_provider.ReactorProvider.boot()` | *(módulo console)* |
| `Route` | `router.py` | `"x-orionis-IRouter"` | `IRouter` | `orionis.http.routes.provider.RouterProvider.boot()` | *(módulo http.routes)* |
| `Schedule` | `schedule.py` | `ISchedule` | `ISchedule` | `orionis.console.scheduler_provider.ScheduleProvider.boot()` | *(módulo console)* |
| `Session` | `session.py` | `ISession` | `ISession` | **Por cada request**, dentro de `orionis.http.layer.web.start_session.StartSessionMiddleware.handle()` — se fija justo después de iniciar la sesión y se libera justo antes de devolver la respuesta. **No** se fija una sola vez en el boot. | *(módulo session)* |
| `Storage` | `storage.py` | `IStorageManager` | `IStorageManager` | `orionis.storage.provider.StorageProvider.boot()` | [`orionis/storage/docs`](../../../storage/docs/README.es.md) |
| `Test` | `testing.py` | `ITestingEngine` | `ITestingEngine` | `orionis.test.provider.TestingProvider.boot()` | [`orionis/test/docs`](../../../test/docs/README.es.md) |
| `View` | `view.py` | `IViewFactory` | `IViewFactory` | `orionis.view.provider.ViewServiceProvider.boot()` | [`orionis/view/docs`](../../../view/docs/README.es.md) |

Nota sobre la columna del accesor: algunas facades devuelven un **alias
de tipo cadena** (`"x-orionis-..."`), otras devuelven directamente el
**tipo del contrato** (`ICacheManager`). Ambos funcionan igual con
`Application().make(...)` — cuál usa cada facade depende únicamente de
la clave con la que el provider correspondiente registró el binding.

Cada stub `*.pyi` además declara los métodos concretos disponibles en el
contrato proxiado (solo para autocompletado del editor), p. ej.
`Route.get`, `Route.post`, `Reactor.call`, `Schedule.command`. Consulta
la documentación del módulo enlazado arriba para la referencia completa,
método por método, de lo que hace cada servicio proxiado; este documento
solo cubre las facades en sí.

### `DateTime` (`orionis.support.facades.datetime.DateTime`)

A diferencia de las demás clases de este paquete, `DateTime` **no** es
una subclase de `Facade` — no tiene contrato, ni stub `.pyi`, ni
`getFacadeAccessor`, y no pasa por el contenedor. Es una utilidad
`__slots__ = ()`, solo con classmethods, que envuelve `pendulum`
directamente; está disponible siempre, incluso antes de arrancar la
aplicación (con timezone `"UTC"` y locale `"en"` por defecto hasta que
`Application` los sobrescribe — ver
[Notas de diseño](#notas-de-diseño)).

Cada método devuelve un objeto `pendulum.DateTime` / `pendulum.Date` /
`pendulum.Duration` / `pendulum.Interval` (o un simple `str`/`bool`/
`int`), nunca un tipo propio de Orionis re-envuelto. Encadena los propios
métodos de `pendulum` sobre el valor devuelto (`.format(...)`,
`.add(...)`, `.year`, ...) directamente.

**Configuración**

| Método | Firma | Descripción |
|---|---|---|
| `getTimezone` | `classmethod() -> str` | Devuelve el nombre de la timezone configurada (por defecto `"UTC"`). |
| `getLocale` | `classmethod() -> str` | Devuelve el código de locale configurado (por defecto `"en"`). |
| `getZoneInfo` | `classmethod() -> zoneinfo.ZoneInfo` | Devuelve (y cachea) el objeto `ZoneInfo` de la timezone configurada. |

**Construcción**

| Método | Firma | Descripción |
|---|---|---|
| `now` | `classmethod(tz: str \| None = None) -> pendulum.DateTime` | Fecha y hora actual en `tz` o en el valor configurado por defecto. |
| `today` | `classmethod(tz: str \| None = None) -> pendulum.Date` | Fecha actual (sin componente de hora). |
| `tomorrow` | `classmethod(tz: str \| None = None) -> pendulum.Date` | Fecha de mañana. |
| `yesterday` | `classmethod(tz: str \| None = None) -> pendulum.Date` | Fecha de ayer. |
| `parse` | `classmethod(date_string: str, tz: str \| None = None, *, strict: bool = True) -> pendulum.DateTime` | Parsea una cadena de fecha y la convierte a `tz` o al valor configurado por defecto. |
| `fromFormat` | `classmethod(date_string: str, fmt: str, tz: str \| None = None, locale: str \| None = None) -> pendulum.DateTime` | Parsea usando tokens de formato explícitos de `pendulum` (p. ej. `"YYYY-MM-DD"`). |
| `local` | `classmethod(year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) -> pendulum.DateTime` | Construye una fecha/hora en la timezone **del sistema**. |
| `naive` | `classmethod(year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) -> pendulum.DateTime` | Construye una fecha/hora sin timezone (naive). |
| `datetime` | `classmethod(year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tz: str \| None = None) -> pendulum.DateTime` | Construye una fecha/hora en `tz` o en el valor configurado por defecto. |
| `fromTimestamp` | `classmethod(timestamp: float, tz: str \| None = None) -> pendulum.DateTime` | Convierte un timestamp Unix. |
| `fromDatetime` | `classmethod(dt: datetime.datetime \| pendulum.DateTime, tz: str \| None = None) -> pendulum.DateTime` | Convierte un datetime estándar o de `pendulum`; lanza `TypeError` para tipos no soportados. Los datetimes naive de stdlib se asumen ya en la timezone destino. |
| `duration` | `classmethod(*, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0, years=0, months=0) -> pendulum.Duration` | Construye una `Duration` independiente. |
| `interval` | `classmethod(start: pendulum.DateTime, end: pendulum.DateTime, *, absolute: bool = False) -> pendulum.Interval` | Construye un `Interval` entre dos fechas/horas. |

**Límites (inicio/fin de unidad)**

| Método | Firma | Descripción |
|---|---|---|
| `startOf` / `endOf` | `classmethod(unit: str, dt: pendulum.DateTime \| None = None, tz: str \| None = None) -> pendulum.DateTime` | Límite genérico para cualquier unidad: `"second"`, `"minute"`, `"hour"`, `"day"`, `"week"`, `"month"`, `"quarter"`, `"year"`, `"decade"`, `"century"`. Usa `now()` si se omite `dt`. |
| `startOfDay` / `endOfDay` | `classmethod(dt=None, tz=None) -> pendulum.DateTime` | Atajos para `unit="day"`. |
| `startOfWeek` / `endOfWeek` | `classmethod(dt=None, tz=None) -> pendulum.DateTime` | Atajos para `unit="week"` (lunes–domingo). |
| `startOfMonth` / `endOfMonth` | `classmethod(dt=None, tz=None) -> pendulum.DateTime` | Atajos para `unit="month"`. |
| `startOfYear` / `endOfYear` | `classmethod(dt=None, tz=None) -> pendulum.DateTime` | Atajos para `unit="year"`. |

**Aritmética**

| Método | Firma | Descripción |
|---|---|---|
| `add` / `subtract` | `classmethod(dt: pendulum.DateTime, *, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0.0, microseconds=0) -> pendulum.DateTime` | Suma/resta genérica multi-unidad. |
| `addDays` | `classmethod(dt: pendulum.DateTime, days: int) -> pendulum.DateTime` | Suma días enteros. |
| `addHours` | `classmethod(dt: pendulum.DateTime, hours: int) -> pendulum.DateTime` | Suma horas enteras. |
| `addMinutes` | `classmethod(dt: pendulum.DateTime, minutes: int) -> pendulum.DateTime` | Suma minutos enteros. |

**Comparación y diferencia**

| Método | Firma | Descripción |
|---|---|---|
| `diffInDays` | `classmethod(dt1: pendulum.DateTime, dt2: pendulum.DateTime) -> int` | Diferencia absoluta en días completos. |
| `diffInHours` | `classmethod(dt1: pendulum.DateTime, dt2: pendulum.DateTime) -> int` | Diferencia absoluta en horas completas. |
| `diff` | `classmethod(dt1: pendulum.DateTime, dt2: pendulum.DateTime \| None = None, *, absolute: bool = True) -> pendulum.Interval` | `Interval` completo (expone `in_years()`, `in_months()`, `in_days()`, ...). |
| `diffForHumans` | `classmethod(dt: pendulum.DateTime, other: pendulum.DateTime \| None = None, *, absolute: bool = False, locale: str \| None = None) -> str` | Frase legible (p. ej. `"hace 3 semanas"`). |
| `isWeekend` | `classmethod(dt: pendulum.DateTime \| None = None) -> bool` | `True` para sábado/domingo. |
| `isToday` | `classmethod(dt: pendulum.DateTime) -> bool` | `True` si `dt.date()` es igual a la fecha de hoy. |
| `isFuture` / `isPast` | `classmethod(dt: pendulum.DateTime) -> bool` | Compara `dt` contra `now()`. |
| `isLeapYear` | `classmethod(dt: pendulum.DateTime \| None = None) -> bool` | `True` si el año es bisiesto. |
| `isBirthday` | `classmethod(dt: pendulum.DateTime, other: pendulum.DateTime \| None = None) -> bool` | `True` si `dt` y `other` (por defecto: ahora) comparten mes y día. |
| `closest` / `farthest` | `classmethod(dt: pendulum.DateTime, *others: pendulum.DateTime) -> pendulum.DateTime` | El candidato de `others` más cercano/lejano a `dt`. |
| `average` | `classmethod(dt1: pendulum.DateTime, dt2: pendulum.DateTime \| None = None) -> pendulum.DateTime` | El punto medio entre dos fechas/horas. |

**Modificadores**

| Método | Firma | Descripción |
|---|---|---|
| `next` / `previous` | `classmethod(dt: pendulum.DateTime, day_of_week: int \| None = None, *, keep_time: bool = False) -> pendulum.DateTime` | Avanza/retrocede hasta la siguiente/anterior ocurrencia de `day_of_week` (p. ej. `pendulum.WEDNESDAY`). |
| `firstOf` / `lastOf` | `classmethod(dt: pendulum.DateTime, unit: str, day_of_week: int \| None = None) -> pendulum.DateTime` | Primer/último día de `unit` (`"month"`, `"quarter"`, `"year"`), opcionalmente restringido a un día de la semana. |
| `nthOf` | `classmethod(dt: pendulum.DateTime, unit: str, nth: int, day_of_week: int) -> pendulum.DateTime` | La `nth`-ésima ocurrencia de `day_of_week` dentro de `unit`. Lanza `pendulum.exceptions.PendulumException` si la ocurrencia no existe. |

**Excepciones lanzadas por `DateTime`**

- `ValueError` — `_setTimezone()` (indirectamente vía `_loadConfig()`) recibe un nombre de timezone inválido.
- `TypeError` — `fromDatetime()` / `convertToLocal()` reciben un tipo de entrada no soportado.
- `pendulum.exceptions.PendulumException` — `nthOf()` solicita una ocurrencia que no existe dentro de la unidad dada.

## Ejemplos de uso

### Facade fijada (pinned), código típico de controlador/servicio

La mayor parte del código de aplicación se ejecuta **después** de que el
framework arrancó y fijó sus facades centrales, así que las llamadas se
leen como simples métodos estáticos:

```python
from orionis.support.facades.logger import Log
from orionis.support.facades.view import View

async def show_dashboard(user_id: int):
    Log.info(f"Rendering dashboard for user {user_id}")
    return await View.make("dashboard.index", user_id=user_id)
```

`Log.info(...)` es síncrono sobre la instancia `Logger` fijada, así que
se llama directamente, sin `await`; `View.make(...)` es `async` sobre el
`IViewFactory` resuelto, así que su resultado debe esperarse.

### Acceso sin fijar (dispatcher) — siempre con `await`

Antes de que una facade se fije (o si tú mismo llamas a
`Facade.unpin()`, p. ej. en un test), cada acceso a un atributo devuelve
un dispatcher asíncrono. **Espéralo siempre**, incluso para valores que
no son invocables en la clase destino:

```python
from orionis.support.facades.cache import Cache

async def read_cached_value(key: str):
    # Cache aún no ha sido fijada: esto resuelve ICacheManager en cada llamada
    return await Cache.get(key)
```

### Base de datos y storage

```python
from orionis.support.facades.db import DB
from orionis.support.facades.storage import Storage

async def export_users_csv():
    rows = await DB.connection().select("SELECT * FROM users")

    disk = Storage.disk("public")
    await disk.file("exports/users.csv").put(rows_to_csv(rows))
```

### Localización

```python
from orionis.support.facades.lang import Lang

def greet(name: str) -> str:
    Lang.setLocale("es")
    return Lang.get("Hello :name", name=name)
```

### Cifrado

```python
from orionis.support.facades.encrypter import Crypt

def protect_token(raw_token: str) -> str:
    return Crypt.encrypt(raw_token)

def reveal_token(payload: str) -> str:
    return Crypt.decrypt(payload)
```

### Routing y scheduling (código de arranque/bootstrap)

```python
from orionis.support.facades.router import Route
from orionis.support.facades.schedule import Schedule

# routes/web.py
Route.get("/users", [UserController, "index"])

# app/console/scheduler.py
Schedule.command("app:cleanup").daily()
```

### Leer el propio contenedor de la aplicación

```python
from orionis.support.facades.application import Application

async def current_environment() -> str:
    return "production" if Application.isProduction() else "development"
```

### `DateTime`, independiente del contenedor

```python
from orionis.support.facades.datetime import DateTime

now = DateTime.now()                       # pendulum.DateTime, tz configurada
in_a_week = DateTime.addDays(now, 7)
print(DateTime.formatLocal(in_a_week))     # "2026-08-03 12:00:00"
print(DateTime.diffForHumans(in_a_week))   # "in 1 week"
```

### Fijar y liberar una facade manualmente (p. ej. en tests)

```python
from orionis.support.facades.logger import Log

async def setup_test():
    await Log.pin()      # cachea el ILogger resuelto una sola vez
    ...
    Log.unpin()          # vuelve a la resolución por cada llamada
```

## Consideraciones de rendimiento y concurrencia

- **El modo fijado (pinned) evita la resolución por el contenedor en cada
  llamada.** Una vez que `pin()` se ejecuta, cada acceso a un atributo es
  un `getattr` directo sobre una instancia cacheada — sin
  `await FacadeClass.resolve()`, sin ida y vuelta por
  `Application().make(...)`. Por eso los providers centrales fijan su
  facade durante `boot()`: `Log.info(...)`, `View.make(...)`,
  `Storage.disk(...)`, etc. son rutas críticas (hot paths).
- **El modo sin fijar siempre resuelve a través del contenedor**, y cada
  acceso —incluso para atributos simples no invocables— devuelve una
  corrutina que debe esperarse. `FacadeMeta` cachea la propia función
  dispatcher por cada par `(clase de facade, nombre de atributo)`, así
  que el acceso repetido sin fijar no sigue creando closures nuevos, pero
  igualmente realiza una resolución completa
  `Application().make(accessor, ...)` en cada llamada.
- **`_pinned_instance` es un atributo de *clase*, compartido en todo el
  proceso.** Fijar una facade afecta a toda corrutina/tarea/hilo que lea
  esa clase después, no solo a quien la fijó. Esto es seguro para las
  facades que se fijan una vez en el boot y nunca se liberan (`Cache`,
  `DB`, `Crypt`, `Lang`, `Log`, `Reactor`, `Route`, `Schedule`, `Storage`,
  `Test`, `View`).
- **`Session` es la única facade que se fija y libera por cada request**,
  dentro de `StartSessionMiddleware.handle()`. Como la instancia fijada
  es estado de clase compartido (no estado por tarea/por request como un
  valor de `contextvars`), requests concurrentes que realmente se
  intercalen entre las llamadas `pin()`/`unpin()` de ese middleware
  podrían ver, durante esa ventana, la sesión de otro request a través de
  la facade `Session`. Prefiere `request.state.session` (establecido por
  el mismo middleware) en código de manejo de requests que pueda
  ejecutarse concurrentemente con otros requests, y reserva la facade
  `Session` para código que se ejecute estrictamente dentro de esa
  ventana fijada del middleware.
- **`DateTime` nunca toca el contenedor** y no tiene ningún bloqueo
  alrededor de su estado de clase `_timezone`/`_locale`/
  `_zoneinfo_cache`; el framework los establece una sola vez durante el
  arranque de la aplicación (antes de que empiece cualquier manejo de
  requests) y se tratan como de solo lectura después en el uso normal.
- **Todos los métodos de los servicios proxiados son `async` por
  convención** en las facades centrales (`Cache`, `DB`, `Crypt`, `Lang`,
  `Storage`, `Test`, `View`, ...), acorde al modelo de I/O totalmente
  asíncrono del framework; consulta la documentación de cada contrato
  proxiado para saber qué métodos específicos son helpers síncronos
  (p. ej. `Cache.store(...)` devuelve un repositorio de forma síncrona,
  mientras que `repo.get(...)` es `async`).

## Notas de diseño

- **Patrón de proxy estático.** Cada facade de este paquete (excepto
  `DateTime`) no aporta estado ni lógica más allá de
  `getFacadeAccessor()`; existen puramente para que el código de la
  aplicación pueda llamar `Log.info(...)`/`Cache.get(...)` en lugar de
  inyectar `ILogger`/`ICacheManager` en todas partes. Esto refleja el
  patrón de facade de Laravel.
- **Clase en tiempo de ejecución vs. stub `.pyi`.** El archivo `.py`
  define la clase real usada en el momento de importar (normalmente solo
  `getFacadeAccessor()`); el archivo `.pyi` es una declaración paralela,
  que hereda tanto del contrato proxiado como de `IFacade`, usada
  únicamente por editores/type checkers para saber qué métodos hará
  disponibles `FacadeMeta.__getattr__` en tiempo de ejecución. Mantener
  el stub sincronizado con el contrato proxiado es una convención de
  mantenimiento de este módulo, no algo forzado por el interprete.
- **El estilo del accesor se hereda, no se elige por facade.** Algunas
  facades devuelven un alias de tipo cadena
  (`"x-orionis-IApplication"`), otras devuelven directamente el tipo del
  contrato (`ICacheManager`). Ambos funcionan de forma idéntica con
  `Application().make(...)`; la elección simplemente sigue la clave que
  usó el provider correspondiente al registrar el binding.
- **`Application` se autorregistra.** A diferencia de las demás facades,
  nada fija (pin) a `Application`; en su lugar, la instancia arrancada de
  `Application` se registra a *sí misma* bajo su propio alias
  (`self.instance(IApplication, self, alias="x-orionis-IApplication")`)
  durante `create()`, de modo que `Facade.resolve()` (a través del
  dispatcher) siempre devuelve el mismo contenedor en ejecución.
- **`DateTime` deliberadamente no es una `Facade`.** No requiere
  contenedor, ni aplicación arrancada, ni resolución asíncrona — basta
  con una llamada a classmethod— así que se implementó como una utilidad
  independiente `__slots__ = ()` en lugar de añadir una capa de
  indirección innecesaria. Se agrupa en este paquete puramente como
  convención de descubribilidad (un helper de "acceso rápido" junto a las
  demás facades), no porque participe en la maquinaria de
  facade/contenedor.

## Notas de compatibilidad

- **Python:** 3.14 o superior (`pyproject.toml` —
  `requires-python = ">=3.14"`).
- **Dependencias:** `pendulum~=3.2` (usado exclusivamente por
  `DateTime`); el resto de las facades de este paquete no tiene ninguna
  dependencia de terceros propia — solo dependen del contenedor
  (`orionis.container`) y del contrato del servicio que proxian.
- **Se requiere una aplicación arrancada.** Todas las facades excepto
  `DateTime` lanzan `RuntimeError` en el primer uso (sin fijar) si
  `Application().isBooted` es `False`. Este es el estado esperado durante
  la mayor parte del tiempo de importación del propio módulo; llama a
  estas facades solo desde código que se ejecute después de que el
  framework haya terminado de arrancar (manejadores de requests,
  manejadores de comandos de consola, tareas programadas, o código
  invocado desde el `boot()` de un provider).
