<p align="center">
  <img src="https://docs.orionis-framework.com/prologue/logo.png" alt="Orionis Framework" width="300" />
</p>

<h1 align="center">Orionis Framework</h1>

<p align="center">
  <strong>Async-first full-stack framework for modern Python applications.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/orionis/"><img src="https://img.shields.io/pypi/v/orionis?color=blue&style=flat-square" alt="PyPI version"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.14%2B-blue?style=flat-square" alt="Python"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License: MIT"></a>
  <a href="https://github.com/orgs/orionis-framework/discussions"><img src="https://img.shields.io/badge/discussions-GitHub-black?style=flat-square&logo=github" alt="GitHub Discussions"></a>
  <a href="https://github.com/sponsors/rmunate"><img src="https://img.shields.io/badge/sponsor-GitHub-pink?style=flat-square&logo=github-sponsors" alt="Sponsor"></a>
</p>

---

Orionis is a modern, opinionated Python framework built from the ground up for **async/await** patterns. It brings together a high-performance HTTP core powered by Rust, a full dependency injection container, a CLI toolchain, an integrated testing engine, and a rich set of support services — everything you need to build APIs, web apps, background workers, and scheduled tasks without stitching together libraries yourself.

---

## Why Orionis?

Most Python frameworks hand you pieces. Orionis hands you a complete, coherent system.

| Concern | Orionis answer |
|---|---|
| HTTP server | [Granian](https://github.com/emmett-framework/granian) — Rust-backed, ASGI & RSGI native |
| Protocol support | ASGI, RSGI, and WSGI in a single binary |
| Dependency injection | IoC container with Singleton, Scoped, and Transient lifetimes |
| Service wiring | Service providers with deferred loading |
| CLI tooling | Reactor CLI — extensible command bus |
| Task scheduling | Cron-style scheduler with event listeners and concurrency control |
| Testing | Integrated engine with async support and rich console output |
| Reflection | Full runtime introspection API for classes, instances, callables, and modules |
| Environment | Typed `.env` management with auto-casting and validation |
| Encryption | AES-128/256 CBC & GCM via a clean `Crypt` facade |
| Logging | Multi-channel logger with rotation and runtime channel switching |
| String utilities | Fluent, immutable `Stringable` wrapper with chainable transformations |

---

## Routing

Orionis provides three dedicated routing files, each with a clear responsibility.

### HTTP routes — `routes/web.py` and `routes/api.py`

Routes are registered via the `Route` facade. Every route maps an HTTP method and path to a controller action using the `[ControllerClass, 'method_name']` convention. Path parameters are declared inline with their type — `{slug:str}`, `{id:int}` — and validated automatically before your controller is called.

```python
# routes/web.py
from app.http.controllers.home_controller import HomeController
from orionis.support.facades.router import Route

# Grouped routes share a common prefix
Route.prefix("/home").group(
    Route.get("/{slug:str}/{id:int}", [HomeController, "index"]),
    Route.post("/", [HomeController, "store"]),
    Route.put("/{id:int}", [HomeController, "update"]),
    Route.delete("/{id:int}", [HomeController, "destroy"]),
)

# Fallback route — catches any unmatched request
# Route.fallback([HomeController, "notFound"])
```

```python
# routes/api.py
from app.http.controllers.home_controller import HomeController
from orionis.support.facades.router import Route

Route.get("/status", [HomeController, "status"])
Route.get("/users/{id:int}", [HomeController, "show"])
Route.post("/users", [HomeController, "create"])
```

### Console routes — `routes/console.py`

Console commands are registered via the `Reactor` facade. A command signature maps directly to a service method, so you can expose existing business logic to the CLI without writing a dedicated command class.

```python
# routes/console.py
from app.services.welcome_service import WelcomeService
from orionis.console.args.argument import Argument
from orionis.support.facades.reactor import Reactor

Reactor.command("app:greet", [WelcomeService, "greetUser"]) \
    .timestamp() \
    .description("Say hello from the CLI") \
    .arguments([
        Argument(
            name_or_flags=["--name", "-n"],
            type_=str,
            required=False,
        )
    ])
```

```bash
python -B reactor app:greet --name=Orionis
```

---

## HTTP Core — Performance by Design

Orionis uses **[Granian](https://github.com/emmett-framework/granian)** as its network engine — a production HTTP server written in Rust, built on [Hyper](https://github.com/hyperium/hyper) and [Tokio](https://github.com/tokio-rs/tokio). This eliminates the Python interpreter from the hot path for network I/O.

```bash
# Start the development server
python -B reactor serve
# http://localhost:8000
```

**Supported interfaces**

- **ASGI** — compatible with the entire Python async ecosystem (Uvicorn, Hypercorn, Daphne).
- **RSGI** — Granian-native interface; network I/O runs entirely in Rust, bypassing the GIL.

Switching between ASGI and RSGI is transparent to your application code — routes, controllers, and middleware work identically in both modes.

---

## Dependency Injection Container

The IoC container is the heart of Orionis. It resolves dependencies automatically by inspecting type annotations on constructors and methods — no configuration files, no decorators.

```python
# app/contracts/email.py
from abc import ABC, abstractmethod

class IEmailService(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool: ...


# app/services/email.py
from app.contracts.email import IEmailService

class EmailService(IEmailService):
    def send(self, to: str, subject: str, body: str) -> bool:
        # real SMTP logic
        return True
```

**Three service lifetimes:**

| Lifetime | Behaviour |
|---|---|
| `Singleton` | One instance per process, shared across all requests and commands |
| `Scoped` | One instance per HTTP request or CLI command execution |
| `Transient` | A fresh instance on every resolution |

The container is thread-safe with double-checked locking and is the single shared instance across HTTP, CLI, and scheduled task contexts.

---

## Service Providers

Providers are the configuration layer. They register bindings during `register()` and run async initialization in `boot()`. Orionis invokes both methods in the correct order during startup.

```bash
# Generate a new provider
python -B reactor make:provider payment_service_provider

# Generate a deferred provider (loaded only when its services are first requested)
python -B reactor make:provider analytics_service_provider --deferred
```

Deferred providers declare the types they offer via `provides()` and are loaded on-demand, reducing startup overhead for optional services.

---

## Reactor CLI

**Reactor** is the official command-line interface for Orionis — an extensible command bus that ships with built-in commands and allows you to add your own.

```bash
python -B reactor serve                  # Start the development server
python -B reactor make:provider name     # Scaffold a service provider
python -B reactor make:command name      # Scaffold a console command
python -B reactor schedule:work          # Run the task scheduler
python -B reactor test                   # Run the test suite
python -B reactor list                   # List all available commands
```

Custom commands register themselves in `routes/console.py` and are auto-discovered by the router. Each command can declare typed arguments, options, and descriptions.

---

## Task Scheduler

Schedule recurring commands with a fluent API — from simple intervals to full cron expressions — with built-in concurrency control and lifecycle event listeners.

```python
# app/console/scheduler.py
from orionis.console.base.scheduler import BaseScheduler
from orionis.console.contracts.schedule import ISchedule

class Scheduler(BaseScheduler):

    def tasks(self, schedule: ISchedule) -> None:

        schedule.command("reports:daily")\
            .purpose("Generate daily sales report")\
            .maxInstances(1)\
            .daily()

        schedule.command("cache:prune")\
            .purpose("Remove expired cache entries")\
            .maxInstances(1)\
            .everyFifteenMinutes()
```

```bash
python -B reactor schedule:work
```

---

## Integrated Testing Engine

Every test method executes inside the real application context — the container is live, configuration is loaded, and all providers have booted. No manual mocking of framework internals required.

```python
from orionis.test.cases.test_case import TestCase

class TestEmailService(TestCase):

    async def test_sends_email(self):
        service = self.make(IEmailService)
        result = await service.send("user@example.com", "Hello", "World")
        self.assertTrue(result)
```

**Engine features:**

- Async-native execution via a thread pool, keeping the event loop unblocked
- Configurable verbosity: `SILENT`, `MINIMAL`, or `DETAILED` (Rich-formatted panels)
- `fail_fast` mode for CI pipelines
- Optional JSON result caching with timestamps
- File and method glob patterns for targeted test runs

---

## Reflection System

A complete runtime introspection API used internally by the container, router, and validator — and available to your application code.

```python
from orionis.services.introspection.reflection import Reflection

rc = Reflection.concrete(MyService)       # Inspect a concrete class
ra = Reflection.abstract(MyContract)      # Inspect an ABC
ri = Reflection.instance(my_object)       # Inspect a live object
rf = Reflection.callable(my_function)     # Inspect a function signature
rm = Reflection.module("my.module")       # Discover classes and functions in a module

Reflection.isConcreteClass(MyService)     # True
Reflection.isAbstract(MyContract)         # True
Reflection.isCoroutineFunction(async_fn)  # True
```

---

## Support Services

### Environment

Typed `.env` management with automatic value casting — booleans, integers, lists, JSON, and more parsed from string values automatically.

```python
from orionis.services.environment.env import Env

db_port = Env.get("DB_PORT", 5432)   # returns int, not str
debug   = Env.get("DEBUG", False)    # returns bool
```

### Encryption

AES-128/256 in CBC or GCM mode via the `Crypt` facade. The application key is loaded from `APP_KEY`; if absent, a secure key is generated automatically at startup.

```python
from orionis.support.facades.crypt import Crypt

token     = Crypt.encrypt("sensitive-data")
plaintext = Crypt.decrypt(token)
```

### Logging

Multi-channel logger with per-channel rotation, retention policies, and runtime channel switching. Channel strategy is read from `LOG_CHANNEL` — no code changes between environments.

```python
from orionis.support.facades.logger import Log

Log.info("Request processed successfully")
Log.error("Payment gateway timeout")
Log.critical("Database connection pool exhausted")
```

### Stringable

Fluent, immutable string wrapper with chainable transformations.

```python
from orionis.support.strings.stringable import Stringable

result = Stringable("  hello world  ").trim().title().finish("!")
# "Hello World!"
```

---

## Architecture at a Glance

```
app/
  console/       # Scheduled tasks and custom CLI commands
  contracts/     # Interfaces and abstract types
  providers/     # Service providers
  services/      # Application services
bootstrap/       # Application bootstrap
config/          # Configuration files (app, cache, logging, database…)
routes/
  web.py         # HTTP routes
  api.py         # API routes
  console.py     # CLI command routes
tests/           # Test suite (auto-discovered by the engine)
orionis/         # Framework internals
```

---

## Requirements

- Python **3.14+**
- Install via pip:

```bash
pip install orionis
```

---

## Documentation

Full documentation is available at **[orionis-framework.com](https://orionis-framework.com)**.

---

## Community & Contributing

Orionis is open-source and welcomes contributions of all kinds.

- **Bug reports & feature requests** — [GitHub Issues](https://github.com/orionis-framework/framework/issues)
- **Discussions** — [GitHub Discussions](https://github.com/orgs/orionis-framework/discussions)
- **LinkedIn** — [Raul Mauricio Unate Castro](https://www.linkedin.com/in/raul-mauricio-unate-castro/)
- **Email** — [raulmauriciounate@gmail.com](mailto:raulmauriciounate@gmail.com)

[![Become a Sponsor](https://img.shields.io/badge/-Become%20a%20Sponsor-pink?style=for-the-badge&logo=github-sponsors)](https://github.com/sponsors/rmunate)

---

*Orionis — Build without limits.*
