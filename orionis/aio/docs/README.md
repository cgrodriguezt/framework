# Orionis Async Loop Manager (`orionis.aio`)

> Thread-safe, platform-aware `asyncio` event loop manager for the Orionis Framework.
>
> 🇪🇸 Versión en español: [README.es.md](README.es.md)

`orionis.aio` centralises every aspect of the event loop lifecycle that an
application built on top of Orionis needs: choosing the fastest loop
implementation available on the current platform, caching a loop per thread,
bridging synchronous and asynchronous code without deadlocks, and cleaning up
pending tasks on exit. The whole module is exposed through a single class,
`Loop`, which is used purely through class/static methods — no instance is
ever created.

---

## Table of contents

1. [Requirements](#requirements)
2. [What problem it solves](#what-problem-it-solves)
3. [API reference](#api-reference)
   - [`Loop.getEventLoop()`](#loopgeteventloop)
   - [`Loop.run(coro)`](#loopruncoro)
   - [`Loop.runSync(coro)`](#looprunsynccoro)
   - [`Loop.execute(func, *args, **kwargs)`](#loopexecutefunc-args-kwargs)
   - [`Loop.createTask(coro, *, name=None)`](#loopcreatetaskcoro-name-none)
   - [`Loop.eventLoopContext()`](#loopeventloopcontext)
   - [`Loop.isLoopRunning()`](#loopisrunning)
4. [Usage examples](#usage-examples)
5. [Design notes](#design-notes)
6. [Performance and concurrency considerations](#performance-and-concurrency-considerations)
7. [Compatibility notes](#compatibility-notes)

---

## Requirements

No installation steps beyond the framework itself are required:

```bash
pip install orionis
```

- **Python:** 3.14 or newer (the module uses PEP 695 generic syntax such as
  `def run[T](...)`).
- **Optional accelerator:** [`uvloop`](https://pypi.org/project/uvloop/) is a
  regular dependency of the framework on non-Windows platforms
  (`uvloop>=0.22.1 ; sys_platform != 'win32'`) and is picked up automatically
  when present — there is nothing to configure manually.
- On Windows, `asyncio.ProactorEventLoop` is selected automatically instead
  (falls back to the asyncio default if unavailable).

## What problem it solves

Mixing synchronous and asynchronous code safely in a multi-threaded,
multi-platform application is error-prone: different platforms favour
different loop implementations, creating a new loop per call is wasteful,
and calling `asyncio.run()` from inside an already-running loop raises a
`RuntimeError`. `Loop` solves all of this behind a small, static API:

- Selects the optimal loop factory once (`uvloop` → `ProactorEventLoop` →
  stdlib default) and caches the decision.
- Keeps a **separate loop per thread** so loops are never shared across
  threads.
- Lets synchronous code call into async code (`runSync`) and async code call
  into synchronous code (`execute`) without deadlocking.
- Cancels and drains pending tasks when a managed context exits.

## API reference

All members below are declared as `@staticmethod` or `@classmethod`. Call
them directly on the class, e.g. `Loop.run(main())` — do not instantiate
`Loop`.

### `Loop.getEventLoop()`

```python
@classmethod
def getEventLoop(cls) -> asyncio.AbstractEventLoop
```

Returns the event loop for the current thread, creating one if necessary.

- If a loop is already running in the calling thread, that loop is returned
  immediately.
- Otherwise, the loop cached for the current thread is returned if it still
  exists and is not closed.
- If no usable loop exists, a new one is created with the platform-optimal
  factory (`uvloop` / `ProactorEventLoop` / stdlib default), registered via
  `asyncio.set_event_loop`, cached for the thread, and returned.

**Parameters:** none.

**Returns:** `asyncio.AbstractEventLoop`.

**Raises:** none.

---

### `Loop.run(coro)`

```python
@staticmethod
def run[T](coro: Coroutine[Any, Any, T]) -> T
```

Executes a coroutine as the **application entry point**. Intended to be
called from a context with **no** running event loop (e.g. a CLI
`if __name__ == "__main__":` block).

- Uses `asyncio.Runner(loop_factory=...)` when an optimal factory (`uvloop`
  or `ProactorEventLoop`) is available, otherwise falls back to
  `asyncio.run(coro)`.
- `KeyboardInterrupt` is caught internally and turned into a return value of
  `0`, so `Ctrl+C` does not propagate as an unhandled exception.

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `coro` | `Coroutine[Any, Any, T]` | The coroutine object to run. |

**Returns:** the value produced by `coro`, or `0` if interrupted with `Ctrl+C`.

**Raises:** `TypeError` if `coro` is not a coroutine object.

> ⚠️ Calling `Loop.run()` from inside an already-running event loop will
> raise, exactly like `asyncio.run()` would — use `Loop.runSync()` in that
> situation instead.

---

### `Loop.runSync(coro)`

```python
@classmethod
def runSync[T](cls, coro: Coroutine[Any, Any, T]) -> T
```

Runs a coroutine to completion **synchronously**, regardless of whether a
loop is already running in the calling thread.

- If no loop is currently running, delegates directly to `Loop.run(coro)`.
- If a loop **is** running (e.g. the caller is inside an ASGI/RSGI handler
  or another async framework), the coroutine is dispatched to a shared,
  single-worker background thread pool where it is executed with its own
  event loop via `Loop.run`, and the result is awaited synchronously with
  `.result()`.

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `coro` | `Coroutine[Any, Any, T]` | The coroutine to run. |

**Returns:** the value produced by `coro`.

**Raises:** propagates any exception raised inside `coro` (surfaced through
`concurrent.futures.Future.result()` when dispatched to the background
thread), plus the same `TypeError` as `Loop.run()` when `coro` is invalid.

> This method **blocks the calling thread** until the coroutine finishes.
> Do not call it from inside the same loop you are trying to bridge from,
> or you may serialise otherwise-concurrent work onto the single worker
> thread.

---

### `Loop.execute(func, *args, **kwargs)`

```python
@staticmethod
async def execute(func: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any
```

Transparently executes a **sync or async** callable from within an
`async def` function, so calling code does not need to branch on the
callable's nature.

- If `func` is a coroutine function (`inspect.iscoroutinefunction`), it is
  awaited directly.
- Otherwise `func` is offloaded to the running loop's default executor via
  `loop.run_in_executor`, so it does not block the event loop thread.
- If the synchronous call unexpectedly returns an awaitable (has
  `__await__`), that awaitable is awaited as well before returning.

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `func` | `Callable[..., Any]` | The function or coroutine function to invoke. Positional-only. |
| `*args` | `Any` | Positional arguments forwarded to `func`. |
| `**kwargs` | `Any` | Keyword arguments forwarded to `func`. |

**Returns:** whatever `func` (or the awaited result) produces.

**Raises:** `TypeError` if `func` is not callable. Must be called from
inside a running event loop (it calls `asyncio.get_running_loop()`
internally).

---

### `Loop.createTask(coro, *, name=None)`

```python
@staticmethod
async def createTask[T](coro: Coroutine[Any, Any, T], *, name: str | None = None) -> asyncio.Task[T]
```

Creates and schedules a new `asyncio.Task` for `coro` on the currently
running loop.

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `coro` | `Coroutine[Any, Any, T]` | The coroutine to schedule. |
| `name` | `str \| None` | Optional descriptive name for the task (keyword-only). |

**Returns:** `asyncio.Task[T]`.

**Raises:** propagates `RuntimeError` from `asyncio.get_running_loop()` if
called with no loop running.

---

### `Loop.eventLoopContext()`

```python
@staticmethod
@contextmanager
def eventLoopContext() -> Generator[asyncio.AbstractEventLoop]
```

Context manager that yields the loop returned by `Loop.getEventLoop()` and
performs cooperative cleanup on exit:

- If the loop is **not** running and still has pending tasks when the
  `with` block exits, every pending task is cancelled and then awaited
  together via `asyncio.gather(*pending, return_exceptions=True)` so no
  cancellation exception escapes the `finally` block.
- `RuntimeError` and `asyncio.CancelledError` raised during cleanup are
  suppressed.

**Parameters:** none.

**Yields:** `asyncio.AbstractEventLoop`.

**Raises:** none (cleanup errors are swallowed by design).

---

### `Loop.isLoopRunning()`

```python
@staticmethod
def isLoopRunning() -> bool
```

Returns `True` if an event loop is currently running in the calling thread.

**Parameters:** none.

**Returns:** `bool`.

**Raises:** none.

## Usage examples

### 1. Application entry point

```python
import asyncio
from orionis.aio import Loop

async def main() -> int:
    print("Application started")
    await asyncio.sleep(0.1)
    return 0

if __name__ == "__main__":
    exit_code = Loop.run(main())
    raise SystemExit(exit_code)
```

### 2. Calling async code from synchronous code (e.g. a CLI command or a signal handler)

```python
from orionis.aio import Loop

async def fetch_greeting() -> str:
    return "Hello from an async task"

def sync_entrypoint() -> None:
    # Works whether or not a loop happens to be running already.
    message = Loop.runSync(fetch_greeting())
    print(message)
```

### 3. Calling a blocking function from async code without stalling the loop

```python
import time
from orionis.aio import Loop

def slow_blocking_call(seconds: float) -> str:
    time.sleep(seconds)  # simulates blocking I/O
    return "done"

async def handler() -> None:
    result = await Loop.execute(slow_blocking_call, 0.5)
    print(result)
```

### 4. Scheduling a background task and inspecting loop state

```python
import asyncio
from orionis.aio import Loop

async def background_job() -> None:
    await asyncio.sleep(1)
    print("background job finished")

async def controller() -> None:
    print("loop running:", Loop.isLoopRunning())  # True
    task = await Loop.createTask(background_job(), name="warmup")
    await task
```

### 5. Managing a loop's lifecycle explicitly with cleanup

```python
from orionis.aio import Loop

def run_batch(coro) -> None:
    with Loop.eventLoopContext() as loop:
        loop.run_until_complete(coro)
        # Any task still pending here is cancelled and drained automatically
        # when the `with` block exits.
```

## Design notes

The following notes describe **existing** design decisions for
informational purposes only — they are not suggestions for change.

- **No instances, only class state.** `Loop` stores all of its state as
  `ClassVar` attributes (`_loop_local`, `_uvloop_factory`,
  `_sync_executor`, etc.) and exposes only `@staticmethod`/`@classmethod`
  members. This mirrors a singleton/namespace pattern: the class itself
  acts as the shared manager.
- **Per-thread loop cache.** `_loop_local` is a `threading.local()`
  instance, so `getEventLoop()` never leaks a loop created in one thread
  into another thread.
- **Double-checked locking.** Both `_detectUvloop()` (uvloop detection) and
  `_getSyncExecutor()` (shared executor creation) use a boolean guard
  checked outside a lock, then re-checked inside it, so the expensive
  operation (module import / thread pool creation) runs at most once even
  under concurrent first-call races.
- **Loop factory resolution order.** `_getLoopFactory()` prefers `uvloop`
  (non-Windows) first, then `asyncio.ProactorEventLoop` (Windows), then
  falls back to `None`, meaning "let asyncio decide" via
  `asyncio.new_event_loop()`.
- **Single-worker bridging pool.** `runSync()` relies on a
  `concurrent.futures.ThreadPoolExecutor(max_workers=1)` to run a coroutine
  in its own loop when called from inside an already-running loop, avoiding
  the classic "cannot run loop while another loop is running" deadlock.
- **Cooperative shutdown.** `eventLoopContext()` cancels pending tasks and
  awaits them with `return_exceptions=True`, so cleanup never raises and
  masks the original exception from the `with` block, if any.

## Performance and concurrency considerations

These are informative notes about existing behaviour, not tuning advice:

- `getEventLoop()`'s fast path (`asyncio.get_running_loop()` inside a
  `try/except`) has negligible overhead when a loop is already running,
  which is the common case inside request handlers.
- `uvloop` detection and loop-factory resolution happen **at most once per
  process** (results are cached in class-level attributes), so repeated
  calls to `getEventLoop()` or `run()` do not re-run platform detection.
- `runSync()` **blocks the calling thread** until the coroutine finishes.
  Because the bridging executor has exactly **one worker**, concurrent
  calls to `runSync()` made while a loop is already running are serialised
  onto that single worker thread — they do not run in parallel with each
  other.
- `execute()` offloads synchronous callables to the loop's **default**
  executor (not the dedicated single-worker pool used by `runSync()`), so
  its concurrency is governed by `asyncio`'s default executor sizing.
- `eventLoopContext()` only cancels/drains pending tasks when the loop is
  **not** running at exit time; if the loop is still running, cleanup is
  skipped for that invocation.
- On non-Windows platforms with `uvloop` installed, both `getEventLoop()`
  and `run()` use `uvloop`'s event loop implementation, which typically
  offers lower I/O latency than the stdlib default; on Windows,
  `ProactorEventLoop` is used instead, which supports subprocess and named
  pipe operations that the default selector loop does not.

## Compatibility notes

- **Minimum Python version:** 3.14 (the module relies on PEP 695 generic
  function syntax: `def run[T](...)`, `def createTask[T](...)`,
  `def runSync[T](...)`).
- **Dependencies:**
  - Standard library only: `asyncio`, `concurrent.futures`, `functools`,
    `inspect`, `sys`, `threading`, `types`, `contextlib`, `typing`.
  - `uvloop` — optional at the Python level but declared as a regular
    project dependency for non-Windows platforms; used automatically when
    importable, silently ignored otherwise (`ImportError` is caught).
- **Platform behaviour differs by design:** the loop implementation
  selected on Windows (`ProactorEventLoop`) differs from the one selected
  on Linux/macOS (`uvloop` or stdlib default) — this is intentional and
  documented, not a bug.
