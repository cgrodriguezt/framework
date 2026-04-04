<h1 align="center">Orionis Framework</h1>

<h3 align="center">The async-first framework Python never had.</h3>

<p align="center"><em>One framework. Zero compromises.</em></p>

<p align="center">
  <img src="https://docs.orionis-framework.com/prologue/logo.png" alt="Orionis Framework" width="300" />
</p>

<p align="center">
  <a href="https://pypi.org/project/orionis/"><img src="https://img.shields.io/pypi/v/orionis?color=blue&style=flat-square" alt="PyPI version"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.14%2B-blue?style=flat-square" alt="Python"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License: MIT"></a>
  <a href="https://github.com/orgs/orionis-framework/discussions"><img src="https://img.shields.io/badge/discussions-GitHub-black?style=flat-square&logo=github" alt="GitHub Discussions"></a>
  <a href="https://github.com/sponsors/rmunate"><img src="https://img.shields.io/badge/sponsor-GitHub-pink?style=flat-square&logo=github-sponsors" alt="Sponsor"></a>
</p>

---

> **Async-first. Rust-powered. Built for production.**
>
> Orionis is a complete framework for building **APIs, web apps, sockets, queues, jobs, scheduled tasks, and CLI commands** — with the architecture and developer experience that Python has been missing.

> **Not just another framework**
>
> Orionis is not a router, not a microframework, not a toolkit. It's a **full-stack async-first framework**, designed to replace the need to assemble multiple tools in Python.

---

## The Problem Isn't Python. It's the Tooling.

Most Python frameworks give you a router and leave the rest to you. You end up stitching together dozens of libraries, writing boilerplate, and fighting decisions that should have been made for you.

**The result?** Inconsistent project structures. No clear conventions. Dependency management as an afterthought. Testing that feels like a chore.

Orionis takes a different approach.

> **A framework, not a toolkit**
>
> Orionis ships with everything you need — dependency injection, service providers, middleware, facades, a CLI, and a testing engine — all designed to work together from day one. One framework. Zero glue code.

---

## Why Orionis

### Rust-Powered HTTP Core

Built on [Granian](https://github.com/emmett-framework/granian), the fastest HTTP server in the Python ecosystem. ASGI and RSGI support out of the box. **10x faster** than traditional Python servers.

### Async-First Architecture

Designed from the ground up for `async/await`. Not bolted on. Not optional. Every layer — from routing to middleware to DI — is natively asynchronous.

### Reactor CLI

A powerful command-line interface for scaffolding, task scheduling, and job processing. Run `python -B reactor schedule:work` and ship.

### Built-In Testing Engine

First-class testing with expressive assertions, async support, and parallel execution. No external test runners required.

### Clean Architecture That Scales

Service providers, middleware pipelines, dependency injection, and facades. Patterns that keep your codebase clean at 100 routes or 10,000.

### Secure by Default

OWASP-aligned security, built-in middleware protection, and authentication primitives. Security is not a plugin — it's the foundation.

---

## Performance That Speaks for Itself

> **Benchmarked. Not Estimated.**
>
> Orionis runs on **Granian** — an HTTP server written in Rust. This isn't theoretical performance. These are real numbers on real hardware.

### Choose Your Interface

| Interface | Description |
|---|---|
| **RSGI** *(Rust Server Gateway Interface)* | Granian's native Rust interface — unlocking maximum throughput and the lowest possible latency. When every microsecond matters. |
| **ASGI** *(Asynchronous Server Gateway Interface)* | Compatible with the entire Python async ecosystem. Full interoperability with Uvicorn, Hypercorn, and Daphne. |

### Real-World Benchmarks

| Metric | Value |
|---|---|
| **Requests/sec** | **455k+** — Projected with Granian RSGI. Based on TechEmpower Framework Benchmarks Round 22. |
| **Avg Latency** | **< 2ms** — Granian internal benchmarks. Sub-millisecond response times under real production conditions. |
| **vs FastAPI** | **2.6x faster** — JSON serialization throughput. Orionis (~455k req/s) vs FastAPI (~177k req/s). |
| **vs Django** | **6.6x faster** — JSON serialization throughput. Orionis (~455k req/s) vs Django (~69k req/s). |

<sub><em>Estimated: Granian RSGI scored 652k raw (TechEmpower R22). Orionis adds framework overhead, projected ~455k req/s.</em></sub>

---

## Get Started in Minutes

Explore the official documentation to get up and running quickly:

| Resource | Description |
|---|---|
| [**Installation**](https://docs.orionis-framework.com/es/getting-started/installation/) | From zero to running in under 5 minutes. |
| [**Project Structure**](https://docs.orionis-framework.com/es/getting-started/project-structure/) | Understand how Orionis organizes your application. |
| [**Configuration**](https://docs.orionis-framework.com/es/getting-started/configuration/) | Fine-tune every aspect of the framework. |
| [**Request Lifecycle**](https://docs.orionis-framework.com/es/architecture/request-lifecycle/) | Trace the full journey of an HTTP request. |

---

## Quick Tour

### Routing

```python
# routes/api.py
from app.http.controllers.home_controller import HomeController
from orionis.support.facades.router import Route

Route.prefix("/home").group(
    Route.get("/{slug:str}/{id:int}", [HomeController, "index"]),
    Route.post("/", [HomeController, "store"]),
    Route.put("/{id:int}", [HomeController, "update"]),
    Route.delete("/{id:int}", [HomeController, "destroy"]),
)
```

### Dependency Injection

```python
# Define a contract
class IMailer(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, body: str) -> bool: ...

# Register in a service provider
class MailServiceProvider(ServiceProvider):
    def register(self) -> None:
        self.app.singleton(IMailer, SmtpMailer)

# Consume via automatic injection — no manual resolution
class ContactController:
    async def send(self, mailer: IMailer) -> dict:
        sent = await mailer.send("user@example.com", "Welcome", "Thanks!")
        return {"sent": sent}
```

Three service lifetimes: **Singleton** (one per process), **Scoped** (one per request), **Transient** (fresh every time).

### Reactor CLI

```bash
python -B reactor serve                  # Start the development server
python -B reactor make:provider name     # Scaffold a service provider
python -B reactor make:command name      # Scaffold a console command
python -B reactor schedule:work          # Run the task scheduler
python -B reactor test                   # Run the test suite
python -B reactor list                   # List all available commands
```

### Testing

```python
from orionis.test import TestCase
from app.contracts.mailer import IMailer

class TestMailer(TestCase):

    async def testWelcomeEmailIsSent(self, mailer: IMailer):
        sent = await mailer.send("jane@example.com", "Welcome", "Thanks!")
        self.assertTrue(sent)
```

```bash
python -B reactor test
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

---

## Documentation

Full documentation — including installation, guides, and API reference — is available at **[docs.orionis-framework.com](https://docs.orionis-framework.com)**.

---

**Stop assembling. Start building for real.**

Orionis gives you the architecture, performance, and developer experience to ship Python applications at scale.

*Built for developers who refuse to compromise — on performance, architecture, or experience.*

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
