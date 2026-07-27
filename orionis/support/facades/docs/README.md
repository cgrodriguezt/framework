# Orionis Facades (`orionis.support.facades`)

> Laravel-style static proxies that expose the framework's core singletons
> (cache, database, encryption, localization, logging, routing, scheduling,
> sessions, storage, testing, views, the application container itself, and
> an independent date/time helper) as simple, import-and-call classes.
>
> 🇪🇸 Versión en español: [README.es.md](README.es.md)

`orionis.support.facades` is the public entry point application code uses
to reach framework services **without** requesting them through
constructor dependency injection. Every class in this package (except
`DateTime`) is a thin proxy: it declares no business logic of its own and
simply tells the underlying `Facade` machinery (`orionis.container.facades`)
which container service it represents.

---

## Table of contents

1. [Requirements](#requirements)
2. [Module overview](#module-overview)
3. [How a facade resolves a call](#how-a-facade-resolves-a-call)
4. [API reference](#api-reference)
   - [Common base contract](#common-base-contract)
   - [Facade catalog](#facade-catalog)
   - [`DateTime`](#datetime-orionissupportfacadesdatetimedatetime)
5. [Usage examples](#usage-examples)
6. [Performance and concurrency considerations](#performance-and-concurrency-considerations)
7. [Design notes](#design-notes)
8. [Compatibility notes](#compatibility-notes)

---

## Requirements

No extra installation is needed beyond the framework itself:

```bash
pip install orionis
```

- **Python:** 3.14 or newer.
- Every facade other than `DateTime` requires a **booted** `Application`
  instance (`orionis.foundation.application.Application`) before it can
  resolve anything — see [Design notes](#design-notes).
- `DateTime` additionally depends on `pendulum~=3.2` (a regular, non-optional
  dependency of the framework).

## Module overview

Most services in Orionis are registered in the container and normally
reached through constructor injection (controllers, commands, providers).
Facades exist for the remaining case: code that wants to call a service
directly — a helper function, a script, a template global, a quick one-off
call in a controller — without declaring a constructor parameter.

The package ships two kinds of classes:

- **Proxy facades** — `Application`, `Cache`, `Catch`, `DB`, `Crypt`
  (`encrypter.py`), `Lang`, `Log`, `Reactor`, `Route` (`router.py`),
  `Schedule`, `Session`, `Storage`, `Test`, `View`. Each one subclasses
  `orionis.container.facades.facade.Facade` and overrides exactly one
  method, `getFacadeAccessor()`, to name the container service it proxies.
  All actual behavior lives in that resolved service; the facade class
  body contributes nothing else at runtime.
- **`DateTime`** — the one class in this package that is *not* a `Facade`.
  It is a plain, `__slots__`-based, classmethod-only utility that wraps
  `pendulum` directly. It lives here by naming/location convention (grouped
  with the other "quick access" helpers) rather than because it goes
  through the container.

Every proxy facade also ships a matching `*.pyi` stub file. Those stubs are
**type-checking only** — inspected by IDEs/type checkers to offer
autocompletion for the methods the underlying contract exposes — and are
never imported or executed at runtime. The runtime class you actually
import only ever defines `getFacadeAccessor()`.

## How a facade resolves a call

The proxying mechanism itself — `Facade`, `FacadeMeta`, `IFacade` — lives
in `orionis.container.facades` and is documented in full in
[`orionis/container/docs/README.md`](../../../container/docs/README.md#facade--facademeta--ifacade).
The short version, restated here for convenience:

1. Every proxy facade in this package subclasses `Facade` and implements
   `getFacadeAccessor() -> str | type`, returning either a string alias
   (e.g. `"x-orionis-ILogger"`) or the contract type itself
   (e.g. `ICacheManager`) that identifies the bound service in the
   container.
2. **Unpinned access** (the default): reading any attribute on the facade
   class — `Cache.get`, `Log.info`, `View.make`, ... — returns a cached
   async dispatcher function. Calling it (`await Cache.get("key")`)
   resolves the service fresh via `await FacadeClass.resolve()`
   (`Application().make(accessor, *args, **kwargs)`), looks up the
   requested attribute on the resolved instance, calls it if it is
   callable (awaiting the result if it is awaitable), or returns it
   as-is if it is a plain attribute. **In this mode every access must be
   awaited**, even for non-callable attributes.
3. **Pinned access**: once `await FacadeClass.pin()` has been called (this
   is what most core `ServiceProvider.boot()` implementations do — see the
   [facade catalog](#facade-catalog)), the class caches the resolved
   instance on `cls._pinned_instance`. From then on, attribute access is a
   direct, synchronous `getattr(cls._pinned_instance, name)` — no
   container lookup, no forced `await` for synchronous members.
   `FacadeClass.unpin()` clears the cache and reverts to dispatcher mode.
4. `resolve()` raises `RuntimeError("Application not booted. Boot your app
   first.")` if the shared `Application()` instance has not completed its
   boot sequence yet.

## API reference

### Common base contract

Every proxy facade inherits the same four members from `Facade`
(`orionis.container.facades.facade.Facade`, contract `IFacade`):

| Member | Signature | Description |
|---|---|---|
| `getFacadeAccessor` | `classmethod() -> str \| type` | Returns the container key for the proxied service. The base implementation raises `NotImplementedError`; every concrete facade in this package overrides it. |
| `resolve` | `async classmethod(*args, **kwargs) -> object` | Resolves the underlying service from the shared `Application()` singleton. Raises `RuntimeError` if the application has not been booted. |
| `pin` | `async classmethod() -> None` | Resolves the service once and caches it as the pinned instance, switching the facade to direct, synchronous attribute access. |
| `unpin` | `classmethod() -> None` | Clears the pinned instance, switching the facade back to dispatcher (always-await) mode. |

### Facade catalog

| Facade | Module | `getFacadeAccessor()` | Proxied contract | Pinned by | Docs |
|---|---|---|---|---|---|
| `Application` | `application.py` | `"x-orionis-IApplication"` | `IApplication` (+ `IContainer`) | Self-registered by `Application.create()`/boot (`self.instance(IApplication, self, alias="x-orionis-IApplication")`); no provider calls `pin()` on this facade. | [`orionis/container/docs`](../../../container/docs/README.md) |
| `Cache` | `cache.py` | `ICacheManager` | `ICacheManager` | `orionis.cache.provider.CacheProvider.boot()` | *(cache module)* |
| `Catch` | `catch.py` | `"x-orionis-ICatch"` | `ICatch` | `orionis.failure.provider.CatchProvider.boot()` | *(failure module)* |
| `DateTime` | `datetime.py` | *n/a — not a `Facade`* | *n/a* | *n/a* | see [below](#datetime-orionissupportfacadesdatetimedatetime) |
| `DB` | `db.py` | `IConnectionManager` | `IConnectionManager` | `orionis.database.provider.DatabaseProvider.boot()` | *(database module)* |
| `Crypt` | `encrypter.py` | `IEncrypter` | `IEncrypter` | `orionis.encrypter.provider.EncrypterProvider.boot()` | [`orionis/encrypter/docs`](../../../encrypter/docs/README.md) |
| `Lang` | `lang.py` | `ITranslator` | `ITranslator` | `orionis.localization.provider.LocalizationProvider.boot()` | [`orionis/localization/docs`](../../../localization/docs/README.md) |
| `Log` | `logger.py` | `"x-orionis-ILogger"` | `ILogger` | `orionis.logging.provider.LoggerProvider.boot()` | [`orionis/logging/docs`](../../../logging/docs/README.md) |
| `Reactor` | `reactor.py` | `"x-orionis-IReactor"` | `IReactor` | `orionis.console.reactor_provider.ReactorProvider.boot()` | *(console module)* |
| `Route` | `router.py` | `"x-orionis-IRouter"` | `IRouter` | `orionis.http.routes.provider.RouterProvider.boot()` | *(http.routes module)* |
| `Schedule` | `schedule.py` | `ISchedule` | `ISchedule` | `orionis.console.scheduler_provider.ScheduleProvider.boot()` | *(console module)* |
| `Session` | `session.py` | `ISession` | `ISession` | **Per-request**, inside `orionis.http.layer.web.start_session.StartSessionMiddleware.handle()` — pinned right after the session is started and unpinned right before the response is returned. **Not** pinned once at boot. | *(session module)* |
| `Storage` | `storage.py` | `IStorageManager` | `IStorageManager` | `orionis.storage.provider.StorageProvider.boot()` | [`orionis/storage/docs`](../../../storage/docs/README.md) |
| `Test` | `testing.py` | `ITestingEngine` | `ITestingEngine` | `orionis.test.provider.TestingProvider.boot()` | [`orionis/test/docs`](../../../test/docs/README.md) |
| `View` | `view.py` | `IViewFactory` | `IViewFactory` | `orionis.view.provider.ViewServiceProvider.boot()` | [`orionis/view/docs`](../../../view/docs/README.md) |

Notes on the accessor column: some facades return a **string alias**
(`"x-orionis-..."`), others return the **contract type itself**
(`ICacheManager`, `IConnectionManager`, ...). Both are valid container keys
— `Application().make(key, ...)` accepts either. Which style a given
facade uses is simply whatever the underlying service was bound with;
it has no effect on how you call the facade.

Each `*.pyi` stub additionally declares the concrete methods available on
the proxied contract (for editor autocompletion only), e.g. `Route.get`,
`Route.post`, `Reactor.call`, `Schedule.command`. Read the linked module
docs above for the full method-by-method reference of what each proxied
service actually does; this document only covers the facades themselves.

### `DateTime` (`orionis.support.facades.datetime.DateTime`)

Unlike every other class in this package, `DateTime` is **not** a
`Facade` subclass — it has no contract, no `.pyi` stub, no `getFacadeAccessor`,
and does not go through the container. It is a `__slots__ = ()`,
classmethod-only wrapper around `pendulum`, always available, even before
the application has booted (with default timezone `"UTC"` and locale
`"en"` until `Application` overrides them — see
[Design notes](#design-notes)).

Every method returns a `pendulum.DateTime` / `pendulum.Date` /
`pendulum.Duration` / `pendulum.Interval` object (or a plain `str`/`bool`/
`int`), never a re-wrapped Orionis type. Chain the returned object's own
`pendulum` methods (`.format(...)`, `.add(...)`, `.year`, ...) directly.

**Configuration**

| Method | Signature | Description |
|---|---|---|
| `getTimezone` | `classmethod() -> str` | Returns the configured timezone name (default `"UTC"`). |
| `getLocale` | `classmethod() -> str` | Returns the configured locale code (default `"en"`). |
| `getZoneInfo` | `classmethod() -> zoneinfo.ZoneInfo` | Returns (and caches) the `ZoneInfo` object for the configured timezone. |

**Construction**

| Method | Signature | Description |
|---|---|---|
| `now` | `classmethod(tz: str \| None = None) -> pendulum.DateTime` | Current date and time in `tz` or the configured default. |
| `today` | `classmethod(tz: str \| None = None) -> pendulum.Date` | Current date (no time component). |
| `tomorrow` | `classmethod(tz: str \| None = None) -> pendulum.Date` | Tomorrow's date. |
| `yesterday` | `classmethod(tz: str \| None = None) -> pendulum.Date` | Yesterday's date. |
| `parse` | `classmethod(date_string: str, tz: str \| None = None, *, strict: bool = True) -> pendulum.DateTime` | Parses a date string and converts it to `tz` or the configured default. |
| `fromFormat` | `classmethod(date_string: str, fmt: str, tz: str \| None = None, locale: str \| None = None) -> pendulum.DateTime` | Parses using explicit `pendulum` format tokens (e.g. `"YYYY-MM-DD"`). |
| `local` | `classmethod(year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) -> pendulum.DateTime` | Builds a datetime in the local **system** timezone. |
| `naive` | `classmethod(year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) -> pendulum.DateTime` | Builds a timezone-naive datetime. |
| `datetime` | `classmethod(year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tz: str \| None = None) -> pendulum.DateTime` | Builds a datetime in `tz` or the configured default. |
| `fromTimestamp` | `classmethod(timestamp: float, tz: str \| None = None) -> pendulum.DateTime` | Converts a Unix timestamp. |
| `fromDatetime` | `classmethod(dt: datetime.datetime \| pendulum.DateTime, tz: str \| None = None) -> pendulum.DateTime` | Converts a stdlib or `pendulum` datetime; raises `TypeError` for unsupported types. Naive stdlib datetimes are assumed to already be in the target timezone. |
| `duration` | `classmethod(*, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0, years=0, months=0) -> pendulum.Duration` | Builds a standalone `Duration`. |
| `interval` | `classmethod(start: pendulum.DateTime, end: pendulum.DateTime, *, absolute: bool = False) -> pendulum.Interval` | Builds an `Interval` between two datetimes. |

**Boundaries (start/end of unit)**

| Method | Signature | Description |
|---|---|---|
| `startOf` / `endOf` | `classmethod(unit: str, dt: pendulum.DateTime \| None = None, tz: str \| None = None) -> pendulum.DateTime` | Generic boundary for any unit: `"second"`, `"minute"`, `"hour"`, `"day"`, `"week"`, `"month"`, `"quarter"`, `"year"`, `"decade"`, `"century"`. Uses `now()` when `dt` is omitted. |
| `startOfDay` / `endOfDay` | `classmethod(dt=None, tz=None) -> pendulum.DateTime` | Shortcuts for `unit="day"`. |
| `startOfWeek` / `endOfWeek` | `classmethod(dt=None, tz=None) -> pendulum.DateTime` | Shortcuts for `unit="week"` (Monday–Sunday). |
| `startOfMonth` / `endOfMonth` | `classmethod(dt=None, tz=None) -> pendulum.DateTime` | Shortcuts for `unit="month"`. |
| `startOfYear` / `endOfYear` | `classmethod(dt=None, tz=None) -> pendulum.DateTime` | Shortcuts for `unit="year"`. |

**Arithmetic**

| Method | Signature | Description |
|---|---|---|
| `add` / `subtract` | `classmethod(dt: pendulum.DateTime, *, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0.0, microseconds=0) -> pendulum.DateTime` | Generic, multi-unit add/subtract. |
| `addDays` | `classmethod(dt: pendulum.DateTime, days: int) -> pendulum.DateTime` | Adds whole days. |
| `addHours` | `classmethod(dt: pendulum.DateTime, hours: int) -> pendulum.DateTime` | Adds whole hours. |
| `addMinutes` | `classmethod(dt: pendulum.DateTime, minutes: int) -> pendulum.DateTime` | Adds whole minutes. |

**Comparison and difference**

| Method | Signature | Description |
|---|---|---|
| `diffInDays` | `classmethod(dt1: pendulum.DateTime, dt2: pendulum.DateTime) -> int` | Absolute difference in whole days. |
| `diffInHours` | `classmethod(dt1: pendulum.DateTime, dt2: pendulum.DateTime) -> int` | Absolute difference in whole hours. |
| `diff` | `classmethod(dt1: pendulum.DateTime, dt2: pendulum.DateTime \| None = None, *, absolute: bool = True) -> pendulum.Interval` | Full `Interval` (exposes `in_years()`, `in_months()`, `in_days()`, ...). |
| `diffForHumans` | `classmethod(dt: pendulum.DateTime, other: pendulum.DateTime \| None = None, *, absolute: bool = False, locale: str \| None = None) -> str` | Human-readable phrase (e.g. `"3 weeks ago"`). |
| `isWeekend` | `classmethod(dt: pendulum.DateTime \| None = None) -> bool` | `True` for Saturday/Sunday. |
| `isToday` | `classmethod(dt: pendulum.DateTime) -> bool` | `True` if `dt.date()` equals today's date. |
| `isFuture` / `isPast` | `classmethod(dt: pendulum.DateTime) -> bool` | Compares `dt` against `now()`. |
| `isLeapYear` | `classmethod(dt: pendulum.DateTime \| None = None) -> bool` | `True` if the year is a leap year. |
| `isBirthday` | `classmethod(dt: pendulum.DateTime, other: pendulum.DateTime \| None = None) -> bool` | `True` if `dt` and `other` (default: now) share month and day. |
| `closest` / `farthest` | `classmethod(dt: pendulum.DateTime, *others: pendulum.DateTime) -> pendulum.DateTime` | The candidate in `others` closest to / farthest from `dt`. |
| `average` | `classmethod(dt1: pendulum.DateTime, dt2: pendulum.DateTime \| None = None) -> pendulum.DateTime` | The midpoint between two datetimes. |

**Modifiers**

| Method | Signature | Description |
|---|---|---|
| `next` / `previous` | `classmethod(dt: pendulum.DateTime, day_of_week: int \| None = None, *, keep_time: bool = False) -> pendulum.DateTime` | Moves to the next/previous occurrence of `day_of_week` (e.g. `pendulum.WEDNESDAY`). |
| `firstOf` / `lastOf` | `classmethod(dt: pendulum.DateTime, unit: str, day_of_week: int \| None = None) -> pendulum.DateTime` | First/last day of `unit` (`"month"`, `"quarter"`, `"year"`), optionally constrained to a weekday. |
| `nthOf` | `classmethod(dt: pendulum.DateTime, unit: str, nth: int, day_of_week: int) -> pendulum.DateTime` | The `nth` occurrence of `day_of_week` within `unit`. Raises `pendulum.exceptions.PendulumException` if the occurrence does not exist. |

**Locale / local-timezone helpers**

| Method | Signature | Description |
|---|---|---|
| `convertToLocal` | `classmethod(dt: str \| datetime.datetime \| pendulum.DateTime) -> pendulum.DateTime` | Converts a string/stdlib/`pendulum` value to the configured timezone. Raises `TypeError` for unsupported types. |
| `formatLocal` | `classmethod(dt: pendulum.DateTime \| None = None, format_string: str = "YYYY-MM-DD HH:mm:ss") -> str` | Formats `dt` (default: `now()`) in the configured timezone. |

**Exceptions raised by `DateTime`**

- `ValueError` — `_setTimezone()` (indirectly via `_loadConfig()`) receives an invalid timezone name.
- `TypeError` — `fromDatetime()` / `convertToLocal()` receive an unsupported input type.
- `pendulum.exceptions.PendulumException` — `nthOf()` requests an occurrence that does not exist within the given unit.

## Usage examples

### Pinned facade, typical controller/service code

Most application code runs **after** the framework has booted and pinned
its core facades, so calls read like plain static methods:

```python
from orionis.support.facades.logger import Log
from orionis.support.facades.view import View

async def show_dashboard(user_id: int):
    Log.info(f"Rendering dashboard for user {user_id}")
    return await View.make("dashboard.index", user_id=user_id)
```

`Log.info(...)` is synchronous on the pinned `Logger` instance, so it is
called directly, without `await`; `View.make(...)` is `async` on the
resolved `IViewFactory`, so its result must be awaited.

### Unpinned (dispatcher) access — always `await`

Before a facade is pinned (or if you call `Facade.unpin()` yourself, e.g.
in a test), every attribute access returns an async dispatcher. **Always
`await` it**, even for values that are not callables on the target class:

```python
from orionis.support.facades.cache import Cache

async def read_cached_value(key: str):
    # Cache has not been pinned yet: this resolves ICacheManager on every call
    return await Cache.get(key)
```

### Database and storage

```python
from orionis.support.facades.db import DB
from orionis.support.facades.storage import Storage

async def export_users_csv():
    rows = await DB.connection().select("SELECT * FROM users")

    disk = Storage.disk("public")
    await disk.file("exports/users.csv").put(rows_to_csv(rows))
```

### Localization

```python
from orionis.support.facades.lang import Lang

def greet(name: str) -> str:
    Lang.setLocale("es")
    return Lang.get("Hello :name", name=name)
```

### Encryption

```python
from orionis.support.facades.encrypter import Crypt

def protect_token(raw_token: str) -> str:
    return Crypt.encrypt(raw_token)

def reveal_token(payload: str) -> str:
    return Crypt.decrypt(payload)
```

### Routing and scheduling (bootstrap-time code)

```python
from orionis.support.facades.router import Route
from orionis.support.facades.schedule import Schedule

# routes/web.py
Route.get("/users", [UserController, "index"])

# app/console/scheduler.py
Schedule.command("app:cleanup").daily()
```

### Reading the application container itself

```python
from orionis.support.facades.application import Application

async def current_environment() -> str:
    return "production" if Application.isProduction() else "development"
```

### `DateTime`, independent of the container

```python
from orionis.support.facades.datetime import DateTime

now = DateTime.now()                       # pendulum.DateTime, configured tz
in_a_week = DateTime.addDays(now, 7)
print(DateTime.formatLocal(in_a_week))     # "2026-08-03 12:00:00"
print(DateTime.diffForHumans(in_a_week))   # "in 1 week"
```

### Pinning and unpinning a facade manually (e.g. inside tests)

```python
from orionis.support.facades.logger import Log

async def setup_test():
    await Log.pin()      # cache the resolved ILogger once
    ...
    Log.unpin()          # revert to per-call resolution
```

## Performance and concurrency considerations

- **Pinned mode avoids per-call container resolution.** Once
  `pin()` runs, every attribute access is a direct `getattr` on a cached
  instance — no `await FacadeClass.resolve()`, no `Application().make(...)`
  round trip. This is why core providers pin their facade during
  `boot()`: `Log.info(...)`, `View.make(...)`, `Storage.disk(...)`, etc.
  are hot paths.
- **Unpinned mode always resolves through the container**, and every
  access — even for plain, non-callable attributes — returns a coroutine
  that must be awaited. `FacadeMeta` caches the dispatcher function itself
  per `(facade class, attribute name)` pair, so repeated unpinned access
  does not keep allocating new closures, but it still performs a full
  `Application().make(accessor, ...)` resolution on every call.
- **`_pinned_instance` is a *class-level* attribute, shared process-wide.**
  Pinning a facade affects every coroutine/task/thread that reads that
  class afterwards, not just the caller that pinned it. This is safe for
  facades pinned once at boot and never unpinned again (`Cache`, `DB`,
  `Crypt`, `Lang`, `Log`, `Reactor`, `Route`, `Schedule`, `Storage`,
  `Test`, `View`).
- **`Session` is the one facade pinned and unpinned per request**, inside
  `StartSessionMiddleware.handle()`. Because the pinned instance is shared
  class state (not per-task/per-request state such as a `contextvars`
  value), concurrently in-flight requests that are truly interleaved
  between the `pin()`/`unpin()` calls of that middleware could observe
  another request's session through the `Session` facade during that
  window. Prefer `request.state.session` (set by the same middleware)
  inside request-handling code that may run concurrently with other
  requests, and reserve the `Session` facade for code that executes
  strictly within that middleware's pinned window.
- **`DateTime` never touches the container** and has no locking around its
  class-level `_timezone`/`_locale`/`_zoneinfo_cache` state; these are set
  once by the framework during application boot (before any request
  handling starts) and treated as read-only afterwards in normal use.
- **All proxied service methods are `async` by convention** in the core
  facades (`Cache`, `DB`, `Crypt`, `Lang`, `Storage`, `Test`, `View`, ...),
  matching the framework's fully asynchronous I/O model; consult each
  proxied contract's own docs for which specific methods are synchronous
  helpers (e.g. `Cache.store(...)` returns a repository object
  synchronously, while `repo.get(...)` is `async`).

## Design notes

- **Static proxy pattern.** Every facade in this package (except
  `DateTime`) contributes no state or logic beyond `getFacadeAccessor()`;
  they exist purely so application code can call
  `Log.info(...)`/`Cache.get(...)` instead of injecting `ILogger`/
  `ICacheManager` everywhere. This mirrors the Laravel facade pattern.
- **Runtime class vs. `.pyi` stub.** The `.py` file defines the actual
  class used at import time (usually just `getFacadeAccessor()`); the
  `.pyi` file is a parallel declaration, inheriting from both the proxied
  contract and `IFacade`, used only by editors/type checkers to know which
  methods `FacadeMeta.__getattr__` will make available at runtime. Keeping
  the stub in sync with the proxied contract is a maintenance convention
  of this module, not something enforced by the interpreter.
- **Accessor style is inherited, not chosen per-facade.** Some facades
  return a string alias (`"x-orionis-IApplication"`), others return the
  contract type directly (`ICacheManager`). Both work identically with
  `Application().make(...)`; the choice simply follows whatever key the
  corresponding provider used when registering the binding.
- **`Application` self-registers.** Unlike the other facades, nothing
  pins `Application`; instead, the booted `Application` instance
  registers *itself* under its own alias
  (`self.instance(IApplication, self, alias="x-orionis-IApplication")`)
  during `create()`, so `Facade.resolve()` (through the dispatcher) always
  returns the same running container.
- **`DateTime` is intentionally not a `Facade`.** It requires no
  container, no booted application, and no async resolution — a
  classmethod call is enough — so it was implemented as a standalone
  `__slots__ = ()` utility instead of adding an unnecessary indirection
  layer. It is grouped in this package purely as a discoverability
  convention (a "quick access" helper next to the other facades), not
  because it participates in the facade/container machinery.

## Compatibility notes

- **Python:** 3.14 or newer (`pyproject.toml` — `requires-python = ">=3.14"`).
- **Dependencies:** `pendulum~=3.2` (used exclusively by `DateTime`); every
  other facade in this package has no third-party dependency of its own —
  it only depends on the container (`orionis.container`) and the contract
  of the service it proxies.
- **Booted application required.** All facades other than `DateTime` raise
  `RuntimeError` on first (unpinned) use if `Application().isBooted` is
  `False`. This is the expected state during most of a module's own
  import time; only call these facades from code that executes after the
  framework has finished booting (request handlers, console command
  handlers, scheduled tasks, or code invoked from a provider's `boot()`).
