# Orionis Entities (`orionis.support.entities`)

> `BaseEntity` — un mixin de dataclass compartido, usado en todo el framework para dar a cada entidad serialización `toDict()` e introspección `getFields()` sin esfuerzo adicional.
>
> 🇬🇧 English version: [README.md](README.md)

`orionis.support.entities` provee una única clase, `BaseEntity`,
pensada para combinarse con el decorador `@dataclass` de la librería
estándar. Es el ancestro común de casi todas las dataclasses de
"entidad" en el framework (entidades de configuración bajo
`orionis.foundation.config`, `Argument`/`Signature` en
`orionis.introspection`, `TestResult` en `orionis.test`,
`ValidationFailure` en `orionis.schemas`, y muchas más), dándoles a todas
una forma consistente de serializarse a un `dict` plano y de
introspeccionar sus propias definiciones de campos.

---

## Tabla de contenidos

1. [Requisitos](#requisitos)
2. [Descripción funcional del módulo](#descripción-funcional-del-módulo)
3. [Referencia de API](#referencia-de-api)
   - [`BaseEntity`](#baseentity-orionissupportentitiesbasebaseentity)
4. [Ejemplos de uso](#ejemplos-de-uso)
5. [Consideraciones de rendimiento y concurrencia](#consideraciones-de-rendimiento-y-concurrencia)
6. [Notas de diseño](#notas-de-diseño)
7. [Notas de compatibilidad](#notas-de-compatibilidad)

---

## Requisitos

No se necesita instalación adicional además del propio framework:

```bash
pip install orionis
```

- **Python:** 3.14 o superior (el mismo mínimo que el resto del framework).
- **Dependencias:** ninguna más allá de la librería estándar de Python
  (`dataclasses`, `enum`).
- **Requisito de uso:** `BaseEntity` **no** es en sí misma una
  `@dataclass`. Las subclases deben decorarse con `@dataclass`
  (opcionalmente `frozen=True`, `kw_only=True`, etc.) para que
  `toDict()` y `getFields()` funcionen — internamente llaman a
  `dataclasses.asdict()` / `dataclasses.fields()`, que requieren que la
  instancia/clase sea realmente una dataclass.

## Descripción funcional del módulo

| Tipo | Archivo | Propósito |
|---|---|---|
| `BaseEntity` | [base.py](../base.py) | Mixin que provee `toDict()`, `getFields()`, un classmethod `_cachedDataclassFields()` cacheado, y un hook `__post_init__()` sobrescribible (no-op por defecto) para entidades basadas en dataclass. |

```python
from orionis.support.entities import BaseEntity
```

---

## Referencia de API

### `BaseEntity` (`orionis.support.entities.base.BaseEntity`)

```python
from dataclasses import dataclass
from orionis.support.entities import BaseEntity

@dataclass
class MyEntity(BaseEntity):
    name: str = "default"
```

`BaseEntity` en sí misma no declara ningún campo — está pensada para
mezclarse en una clase que *también* esté decorada con `@dataclass`. Se
apoya en el hook estándar `__post_init__` de las dataclasses y en las
funciones del módulo `dataclasses` (`asdict`, `fields`) operando sobre
la subclase concreta.

| Método | Firma | Descripción |
|---|---|---|
| `__post_init__` | `__post_init__(self) -> None` | Hook no-op invocado automáticamente por la maquinaria de dataclasses justo después de todas las asignaciones de campos del `__init__` generado. Sobrescribirlo en una subclase para agregar lógica de validación o de campos derivados — la implementación base no hace nada y devuelve `None`. |
| `toDict` | `toDict(self) -> dict` | Devuelve una representación `dict` de la instancia vía `dataclasses.asdict()`, usando un `dict_factory` personalizado que convierte cualquier valor de campo `Enum` a `.value` (recursivamente, también para dataclasses anidadas, según el propio comportamiento recursivo de `asdict()`). |
| `getFields` | `getFields(self) -> list[dict]` | Devuelve un dict por cada campo declarado con las claves `"name"` (`str`), `"types"` (`list[str]`), `"default"` (`Any`) y `"metadata"` (`dict`) — ver abajo cómo se resuelven `default`/`types`. |
| `_cachedDataclassFields` | `_cachedDataclassFields(cls) -> tuple` *(classmethod)* | Devuelve la tupla de objetos `dataclasses.Field` para `cls`, calculada una vez vía `dataclasses.fields(cls)` y cacheada en un `dict[type, tuple]` a nivel de módulo indexado por clase — usado internamente por `getFields()`. |

**Cómo `getFields()` resuelve la entrada `"types"` de cada campo:**
intenta primero `field.type.__name__`; si eso falla (uniones, genéricos,
anotaciones basadas en cadenas/forward-references), recurre a dividir la
forma en cadena del tipo por `"|"` y recortar cada parte, normalizando
siempre el resultado a una `list[str]`.

**Cómo `getFields()` resuelve la entrada `"default"` de cada campo**, en
orden de prioridad:

1. Si el campo tiene un `default` estático (no `dataclasses.MISSING`),
   se usa — llamándolo primero si es a su vez invocable, y luego
   convirtiéndolo vía `dataclasses.asdict()` si es una instancia de
   dataclass, o vía `.value` si es un miembro de `Enum`.
2. Si no, si el campo tiene un `default_factory` (no
   `dataclasses.MISSING`), se llama (o se usa tal cual si no es
   invocable) y se aplica la misma normalización de dataclass/`Enum`.
3. Si no, se recurre a `field.metadata.get("default", None)`.

El propio `field.metadata` también se normaliza: si contiene una clave
`"default"`, ese valor pasa por la misma resolución
invocable/dataclass/`Enum` antes de volver a colocarse en el `dict`
`"metadata"` devuelto.

---

## Ejemplos de uso

### Una entidad mínima

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

### Una entidad con un campo `Enum`

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
# {'status': 'active'}  -- el Enum se serializa a su `.value`
```

### Inspeccionar metadatos de campo con `getFields()`

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

### Agregar validación con `__post_init__`

```python
from dataclasses import dataclass
from orionis.support.entities import BaseEntity

@dataclass
class Range(BaseEntity):
    low: int
    high: int

    def __post_init__(self) -> None:
        if self.low > self.high:
            error_msg = "`low` no debe ser mayor que `high`"
            raise ValueError(error_msg)

Range(low=1, high=10)   # OK
Range(low=10, high=1)   # lanza ValueError
```

---

## Consideraciones de rendimiento y concurrencia

- `dataclasses.fields(cls)` construye una nueva tupla en cada llamada;
  `getFields()` evita pagar ese costo repetidamente pasando por
  `_cachedDataclassFields()`, que memoiza el resultado en un `dict[type,
  tuple]` a **nivel de módulo** (`_FIELDS_CACHE`), indexado por la clase
  concreta — el costo se paga una vez por clase, no una vez por
  instancia ni por llamada.
- `toDict()` usa un par `_dictFactory`/`_enumSerializer` a nivel de
  módulo en lugar de construir un closure en cada llamada, evitando dos
  asignaciones de objetos función adicionales por invocación de
  `toDict()`.
- `dataclasses.asdict()` (usado por `toDict()`) hace **copias profundas**
  recursivas de los valores de campo que no son dataclass (listas,
  diccionarios, etc.) como parte de su comportamiento estándar de
  librería — para entidades con estructuras mutables anidadas grandes,
  este es un costo inherente al propio `asdict()`, no algo que
  `BaseEntity` añada por encima.
- `_FIELDS_CACHE` es un `dict` plano a nivel de módulo sin lock alrededor
  de las escrituras. Si dos hilos llaman a
  `getFields()`/`_cachedDataclassFields()` para la *misma* clase por
  primera vez de forma concurrente, ambos pueden calcular
  `dataclasses.fields(cls)` una vez y escribir una tupla igual en la
  caché — un cómputo redundante inofensivo, no un problema de
  corrección, ya que el valor calculado siempre es el mismo para una
  clase dada.
- Todas las operaciones son síncronas, limitadas por CPU, y no realizan
  E/S.

## Notas de diseño

- **Mixin, no una dataclass en sí misma**: `BaseEntity` deliberadamente
  no tiene campos propios y no está decorada con `@dataclass` — cada
  entidad concreta del framework aplica `@dataclass` (a menudo con
  `frozen=True, kw_only=True`) a su propia subclase, manteniendo el
  comportamiento de `BaseEntity` (serialización, introspección)
  ortogonal a la disposición de campos específica de cada entidad y a su
  elección de (in)mutabilidad. Las entidades de configuración en
  `orionis.foundation.config` y entidades de reflexión como
  `Argument`/`Signature` en `orionis.introspection` siguen este patrón
  (`@dataclass(frozen=True, kw_only=True)` combinado con `BaseEntity`).
- **Normalización de `Enum` en la serialización**: tanto `toDict()` como
  `getFields()` convierten los miembros `Enum` a su `.value`, de modo
  que quienes consumen la forma serializada (JSON, logs, payloads HTTP)
  nunca ven objetos `Enum` crudos.
- **Caché de campos por clase**: cachear `dataclasses.fields(cls)` a
  nivel de clase (no por instancia) refleja el hecho de que las
  definiciones de campos son idénticas para toda instancia de la misma
  dataclass.
- **Hook `__post_init__` sobrescribible**: `BaseEntity.__post_init__` es
  intencionalmente un no-op para que las subclases puedan agregar lógica
  de validación/campos derivados simplemente sobrescribiéndolo — el
  `__init__` generado estándar de la dataclass ya llama a
  `__post_init__` automáticamente después de asignar todos los campos.

## Notas de compatibilidad

- Requiere **Python 3.14+**, en línea con el resto del framework
  `orionis` (`requires-python = ">=3.14"` en `pyproject.toml`).
- Sin dependencias de terceros; solo usa `dataclasses` y `enum` de la
  librería estándar.
- Sin comportamiento específico de plataforma.
- Las subclases **deben** estar decoradas con `@dataclass` (directamente
  o vía otra dataclass en el MRO) para que `toDict()`/`getFields()`
  funcionen, ya que ambos dependen de que
  `dataclasses.asdict()`/`dataclasses.fields()` reconozcan la
  instancia/clase como una dataclass.
