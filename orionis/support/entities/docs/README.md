# Orionis Entities (`orionis.support.entities`)

> `BaseEntity` — a shared dataclass mixin used across the whole framework to give every entity `toDict()` serialization and `getFields()` introspection for free.
>
> 🇪🇸 Versión en español: [README.es.md](README.es.md)

`orionis.support.entities` provides a single class, `BaseEntity`, meant
to be combined with the standard library's `@dataclass` decorator. It is
the common ancestor of nearly every "entity" dataclass across the
framework (configuration entities under `orionis.foundation.config`,
`Argument`/`Signature` in `orionis.introspection`, `TestResult` in
`orionis.test`, `ValidationFailure` in `orionis.schemas`, and many more),
giving all of them a consistent way to serialize to a plain `dict` and
to introspect their own field definitions.

---

## Table of contents

1. [Requirements](#requirements)
2. [Module overview](#module-overview)
3. [API reference](#api-reference)
   - [`BaseEntity`](#baseentity-orionissupportentitiesbasebaseentity)
4. [Usage examples](#usage-examples)
5. [Performance and concurrency considerations](#performance-and-concurrency-considerations)
6. [Design notes](#design-notes)
7. [Compatibility notes](#compatibility-notes)

---

## Requirements

No extra installation is required beyond the framework itself:

```bash
pip install orionis
```

- **Python:** 3.14 or newer (the same minimum as the rest of the framework).
- **Dependencies:** none beyond the Python standard library
  (`dataclasses`, `enum`).
- **Usage requirement:** `BaseEntity` is **not** itself a `@dataclass`.
  Subclasses must be decorated with `@dataclass` (optionally
  `frozen=True`, `kw_only=True`, etc.) for `toDict()` and `getFields()`
  to work — they call `dataclasses.asdict()` / `dataclasses.fields()`
  internally, which require the instance/class to actually be a
  dataclass.

## Module overview

| Type | File | Purpose |
|---|---|---|
| `BaseEntity` | [base.py](../base.py) | Mixin providing `toDict()`, `getFields()`, a cached `_cachedDataclassFields()` classmethod, and an overridable no-op `__post_init__()` hook for dataclass-based entities. |

```python
from orionis.support.entities import BaseEntity
```

---

## API reference

### `BaseEntity` (`orionis.support.entities.base.BaseEntity`)

```python
from dataclasses import dataclass
from orionis.support.entities import BaseEntity

@dataclass
class MyEntity(BaseEntity):
    name: str = "default"
```

`BaseEntity` itself declares no fields — it is meant to be mixed into a
class that is *also* decorated with `@dataclass`. It relies on the
standard `__post_init__` dataclass hook and on the `dataclasses` module
functions (`asdict`, `fields`) operating on the concrete subclass.

| Method | Signature | Description |
|---|---|---|
| `__post_init__` | `__post_init__(self) -> None` | No-op hook automatically invoked by the dataclass machinery right after all generated `__init__` field assignments. Override it in a subclass to add validation or derived-field logic — the base implementation does nothing and returns `None`. |
| `toDict` | `toDict(self) -> dict` | Returns a `dict` representation of the instance via `dataclasses.asdict()`, using a custom `dict_factory` that converts any `Enum` field value to `.value` (recursively, for nested dataclasses as well, per `asdict()`'s own recursive behavior). |
| `getFields` | `getFields(self) -> list[dict]` | Returns one dict per declared field with keys `"name"` (`str`), `"types"` (`list[str]`), `"default"` (`Any`), and `"metadata"` (`dict`) — see below for how `default`/`types` are resolved. |
| `_cachedDataclassFields` | `_cachedDataclassFields(cls) -> tuple` *(classmethod)* | Returns the tuple of `dataclasses.Field` objects for `cls`, computed once via `dataclasses.fields(cls)` and cached in a module-level `dict[type, tuple]` keyed by class — used internally by `getFields()`. |

**How `getFields()` resolves each field's `"types"` entry:**
attempts `field.type.__name__` first; if that fails (unions, generics,
string-based/forward-reference annotations), falls back to splitting
the string form of the type on `"|"` and stripping each part, always
normalizing the result to a `list[str]`.

**How `getFields()` resolves each field's `"default"` entry**, in
priority order:

1. If the field has a static `default` (not `dataclasses.MISSING`), use
   it — calling it first if it is itself callable, then converting it
   via `dataclasses.asdict()` if it is a dataclass instance, or via
   `.value` if it is an `Enum` member.
2. Otherwise, if the field has a `default_factory` (not
   `dataclasses.MISSING`), call it (or use it as-is if not callable) and
   apply the same dataclass/`Enum` normalization.
3. Otherwise, fall back to `field.metadata.get("default", None)`.

`field.metadata` itself is also normalized: if it contains a `"default"`
key, that value goes through the same callable/dataclass/`Enum`
resolution before being placed back into the returned `"metadata"` dict.

---

## Usage examples

### A minimal entity

```python
from dataclasses import dataclass
from orionis.support.entities import BaseEntity

@dataclass
class User(BaseEntity):
    name: str = "anonymous"
    age: int = 0
    active: bool = True

user = User(name="Ada", age=34)
print(user.toDict())
# {'name': 'Ada', 'age': 34, 'active': True}
```

### An entity with an `Enum` field

```python
from dataclasses import dataclass
from enum import Enum
from orionis.support.entities import BaseEntity

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

@dataclass
class Account(BaseEntity):
    status: Status = Status.ACTIVE

account = Account()
print(account.toDict())
# {'status': 'active'}  -- the Enum is serialized to its `.value`
```

### Inspecting field metadata with `getFields()`

```python
from dataclasses import dataclass, field
from orionis.support.entities import BaseEntity

@dataclass
class Product(BaseEntity):
    score: int = field(default=0, metadata={"label": "Score", "default": 42})

for info in Product().getFields():
    print(info["name"], info["types"], info["default"], info["metadata"])
# score ['int'] 0 {'label': 'Score', 'default': 42}
```

### Adding validation with `__post_init__`

```python
from dataclasses import dataclass
from orionis.support.entities import BaseEntity

@dataclass
class Range(BaseEntity):
    low: int
    high: int

    def __post_init__(self) -> None:
        if self.low > self.high:
            error_msg = "`low` must not be greater than `high`"
            raise ValueError(error_msg)

Range(low=1, high=10)   # OK
Range(low=10, high=1)   # raises ValueError
```

---

## Performance and concurrency considerations

- `dataclasses.fields(cls)` builds a new tuple on every call; `getFields()`
  avoids paying that cost repeatedly by going through
  `_cachedDataclassFields()`, which memoizes the result in a **module-level**
  `dict[type, tuple]` (`_FIELDS_CACHE`), keyed by the concrete class —
  the cost is paid once per class, not once per instance or per call.
- `toDict()` uses a module-level `_dictFactory`/`_enumSerializer` pair
  instead of building a closure on every call, avoiding two extra
  function-object allocations per `toDict()` invocation.
- `dataclasses.asdict()` (used by `toDict()`) recursively **deep-copies**
  non-dataclass field values (lists, dicts, etc.) as part of its
  standard-library behavior — for entities holding large nested mutable
  structures, this is an inherent cost of `asdict()` itself, not
  something `BaseEntity` adds on top.
- `_FIELDS_CACHE` is a plain module-level `dict` with no lock around
  writes. If two threads call `getFields()`/`_cachedDataclassFields()`
  for the *same* class for the first time concurrently, both may compute
  `dataclasses.fields(cls)` once and write an equal tuple to the cache —
  a harmless redundant computation, not a correctness issue, since the
  computed value is always the same for a given class.
- All operations are synchronous, CPU-bound, and perform no I/O.

## Design notes

- **Mixin, not a dataclass itself**: `BaseEntity` deliberately has no
  fields of its own and is not decorated with `@dataclass` — every
  concrete entity in the framework applies `@dataclass` (often with
  `frozen=True, kw_only=True`) to its own subclass, keeping
  `BaseEntity`'s behavior (serialization, introspection) orthogonal to
  each entity's specific field layout and (im)mutability choice.
  Configuration entities in `orionis.foundation.config` and reflection
  entities like `Argument`/`Signature` in `orionis.introspection` follow
  this pattern (`@dataclass(frozen=True, kw_only=True)` combined with
  `BaseEntity`).
- **`Enum` normalization on serialization**: both `toDict()` and
  `getFields()` convert `Enum` members to their `.value`, so consumers
  of the serialized form (JSON, logs, HTTP payloads) never see raw
  `Enum` objects.
- **Per-class field cache**: caching `dataclasses.fields(cls)` at the
  class level (not per instance) reflects the fact that field
  definitions are identical for every instance of the same dataclass.
- **Overridable `__post_init__` hook**: `BaseEntity.__post_init__` is
  intentionally a no-op so subclasses can add validation/derived-field
  logic simply by overriding it — the standard dataclass-generated
  `__init__` already calls `__post_init__` automatically after setting
  all fields.

## Compatibility notes

- Requires **Python 3.14+**, consistent with the rest of the `orionis`
  framework (`requires-python = ">=3.14"` in `pyproject.toml`).
- No third-party dependencies; only uses `dataclasses` and `enum` from
  the standard library.
- No platform-specific behavior.
- Subclasses **must** be decorated with `@dataclass` (directly or via
  another dataclass in the MRO) for `toDict()`/`getFields()` to work,
  since both rely on `dataclasses.asdict()`/`dataclasses.fields()`
  recognizing the instance/class as a dataclass.
