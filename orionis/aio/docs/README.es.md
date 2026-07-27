# Gestor de Bucle Asíncrono de Orionis (`orionis.aio`)

> Gestor de bucle de eventos de `asyncio` thread-safe y consciente de la
> plataforma, para el Orionis Framework.
>
> 🇬🇧 English version: [README.md](README.md)

`orionis.aio` centraliza todo lo relacionado con el ciclo de vida del bucle
de eventos que una aplicación construida sobre Orionis necesita: elegir la
implementación de bucle más rápida disponible en la plataforma actual,
almacenar en caché un bucle por hilo, permitir el puente entre código
síncrono y asíncrono sin bloqueos mutuos (deadlocks), y limpiar las tareas
pendientes al finalizar. Todo el módulo se expone a través de una única
clase, `Loop`, que se usa exclusivamente mediante métodos de clase/estáticos
— nunca se crea una instancia.

---

## Tabla de contenidos

1. [Requisitos](#requisitos)
2. [Qué problema resuelve](#qué-problema-resuelve)
3. [Referencia de API](#referencia-de-api)
   - [`Loop.getEventLoop()`](#loopgeteventloop)
   - [`Loop.run(coro)`](#loopruncoro)
   - [`Loop.runSync(coro)`](#looprunsynccoro)
   - [`Loop.execute(func, *args, **kwargs)`](#loopexecutefunc-args-kwargs)
   - [`Loop.createTask(coro, *, name=None)`](#loopcreatetaskcoro-name-none)
   - [`Loop.eventLoopContext()`](#loopeventloopcontext)
   - [`Loop.isLoopRunning()`](#loopisrunning)
4. [Ejemplos de uso](#ejemplos-de-uso)
5. [Notas de diseño](#notas-de-diseño)
6. [Consideraciones de rendimiento y concurrencia](#consideraciones-de-rendimiento-y-concurrencia)
7. [Notas de compatibilidad](#notas-de-compatibilidad)

---

## Requisitos

No se necesita ningún paso de instalación adicional además del propio
framework:

```bash
pip install orionis
```

- **Python:** 3.14 o superior (el módulo usa la sintaxis genérica de PEP 695,
  por ejemplo `def run[T](...)`).
- **Acelerador opcional:** [`uvloop`](https://pypi.org/project/uvloop/) es
  una dependencia normal del framework en plataformas distintas de Windows
  (`uvloop>=0.22.1 ; sys_platform != 'win32'`) y se detecta y usa
  automáticamente cuando está presente — no requiere configuración manual.
- En Windows se selecciona automáticamente `asyncio.ProactorEventLoop`
  (con retorno al bucle por defecto de asyncio si no está disponible).

## Qué problema resuelve

Combinar código síncrono y asíncrono de forma segura en una aplicación
multihilo y multiplataforma es propenso a errores: cada plataforma favorece
una implementación de bucle distinta, crear un bucle nuevo en cada llamada
es costoso, y llamar a `asyncio.run()` desde dentro de un bucle que ya está
corriendo lanza un `RuntimeError`. `Loop` resuelve todo esto detrás de una
API estática y compacta:

- Selecciona la fábrica de bucle óptima una sola vez (`uvloop` →
  `ProactorEventLoop` → valor por defecto de la librería estándar) y
  almacena en caché la decisión.
- Mantiene un **bucle independiente por hilo**, de modo que los bucles nunca
  se comparten entre hilos.
- Permite que código síncrono invoque código asíncrono (`runSync`) y que
  código asíncrono invoque código síncrono (`execute`) sin producir
  bloqueos mutuos.
- Cancela y drena las tareas pendientes cuando un contexto gestionado
  finaliza.

## Referencia de API

Todos los miembros descritos a continuación están declarados como
`@staticmethod` o `@classmethod`. Se invocan directamente sobre la clase,
por ejemplo `Loop.run(main())` — no se debe instanciar `Loop`.

### `Loop.getEventLoop()`

```python
@classmethod
def getEventLoop(cls) -> asyncio.AbstractEventLoop
```

Devuelve el bucle de eventos del hilo actual, creando uno si es necesario.

- Si ya hay un bucle corriendo en el hilo que llama, se devuelve ese mismo
  bucle de inmediato.
- En caso contrario, se devuelve el bucle almacenado en caché para el hilo
  actual, si aún existe y no está cerrado.
- Si no existe un bucle utilizable, se crea uno nuevo con la fábrica óptima
  para la plataforma (`uvloop` / `ProactorEventLoop` / valor por defecto),
  se registra mediante `asyncio.set_event_loop`, se guarda en caché para el
  hilo y se devuelve.

**Parámetros:** ninguno.

**Devuelve:** `asyncio.AbstractEventLoop`.

**Excepciones:** ninguna.

---

### `Loop.run(coro)`

```python
@staticmethod
def run[T](coro: Coroutine[Any, Any, T]) -> T
```

Ejecuta una corrutina como **punto de entrada de la aplicación**. Está
pensado para invocarse desde un contexto en el que **no** hay ningún bucle
de eventos corriendo (por ejemplo, un bloque `if __name__ == "__main__":`
de una CLI).

- Usa `asyncio.Runner(loop_factory=...)` cuando existe una fábrica óptima
  (`uvloop` o `ProactorEventLoop`); en caso contrario recurre a
  `asyncio.run(coro)`.
- `KeyboardInterrupt` se captura internamente y se convierte en un valor de
  retorno `0`, de modo que `Ctrl+C` no se propaga como una excepción sin
  gestionar.

**Parámetros:**

| Nombre | Tipo | Descripción |
| --- | --- | --- |
| `coro` | `Coroutine[Any, Any, T]` | El objeto corrutina a ejecutar. |

**Devuelve:** el valor producido por `coro`, o `0` si se interrumpe con
`Ctrl+C`.

**Excepciones:** `TypeError` si `coro` no es un objeto corrutina.

> ⚠️ Llamar a `Loop.run()` desde dentro de un bucle de eventos que ya está
> corriendo lanzará una excepción, igual que haría `asyncio.run()` — en ese
> caso use `Loop.runSync()`.

---

### `Loop.runSync(coro)`

```python
@classmethod
def runSync[T](cls, coro: Coroutine[Any, Any, T]) -> T
```

Ejecuta una corrutina hasta su finalización de forma **síncrona**,
independientemente de si ya hay un bucle corriendo en el hilo que llama.

- Si no hay ningún bucle corriendo, delega directamente en `Loop.run(coro)`.
- Si **sí** hay un bucle corriendo (por ejemplo, el llamador está dentro de
  un manejador ASGI/RSGI u otro framework asíncrono), la corrutina se
  despacha a un pool de hilos compartido de un solo trabajador, donde se
  ejecuta con su propio bucle de eventos mediante `Loop.run`, y el
  resultado se espera de forma síncrona con `.result()`.

**Parámetros:**

| Nombre | Tipo | Descripción |
| --- | --- | --- |
| `coro` | `Coroutine[Any, Any, T]` | La corrutina a ejecutar. |

**Devuelve:** el valor producido por `coro`.

**Excepciones:** propaga cualquier excepción lanzada dentro de `coro`
(expuesta a través de `concurrent.futures.Future.result()` cuando se
despacha al hilo en segundo plano), además del mismo `TypeError` que
`Loop.run()` cuando `coro` no es válida.

> Este método **bloquea el hilo que lo invoca** hasta que la corrutina
> finaliza. No lo llame desde dentro del mismo bucle que está intentando
> puentear, o podría terminar serializando trabajo que de otro modo sería
> concurrente en ese único hilo trabajador.

---

### `Loop.execute(func, *args, **kwargs)`

```python
@staticmethod
async def execute(func: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any
```

Ejecuta de forma transparente un invocable **síncrono o asíncrono** desde
dentro de una función `async def`, para que el código que llama no tenga
que distinguir entre ambos casos.

- Si `func` es una función corrutina (`inspect.iscoroutinefunction`), se
  espera (`await`) directamente.
- En caso contrario, `func` se delega al executor por defecto del bucle
  mediante `loop.run_in_executor`, de modo que no bloquea el hilo del
  bucle de eventos.
- Si la llamada síncrona devuelve inesperadamente un objeto esperable
  (tiene `__await__`), ese objeto también se espera antes de devolver el
  resultado.

**Parámetros:**

| Nombre | Tipo | Descripción |
| --- | --- | --- |
| `func` | `Callable[..., Any]` | La función o función corrutina a invocar. Solo posicional. |
| `*args` | `Any` | Argumentos posicionales reenviados a `func`. |
| `**kwargs` | `Any` | Argumentos con nombre reenviados a `func`. |

**Devuelve:** lo que produzca `func` (o el resultado esperado, si aplica).

**Excepciones:** `TypeError` si `func` no es invocable. Debe llamarse desde
dentro de un bucle de eventos en ejecución (internamente llama a
`asyncio.get_running_loop()`).

---

### `Loop.createTask(coro, *, name=None)`

```python
@staticmethod
async def createTask[T](coro: Coroutine[Any, Any, T], *, name: str | None = None) -> asyncio.Task[T]
```

Crea y programa una nueva `asyncio.Task` para `coro` en el bucle
actualmente en ejecución.

**Parámetros:**

| Nombre | Tipo | Descripción |
| --- | --- | --- |
| `coro` | `Coroutine[Any, Any, T]` | La corrutina a programar. |
| `name` | `str \| None` | Nombre descriptivo opcional para la tarea (solo por palabra clave). |

**Devuelve:** `asyncio.Task[T]`.

**Excepciones:** propaga el `RuntimeError` de `asyncio.get_running_loop()`
si se llama sin ningún bucle en ejecución.

---

### `Loop.eventLoopContext()`

```python
@staticmethod
@contextmanager
def eventLoopContext() -> Generator[asyncio.AbstractEventLoop]
```

Gestor de contexto que entrega el bucle devuelto por
`Loop.getEventLoop()` y realiza una limpieza cooperativa al salir:

- Si el bucle **no** está en ejecución y todavía tiene tareas pendientes
  cuando el bloque `with` finaliza, todas esas tareas se cancelan y luego
  se esperan en conjunto mediante
  `asyncio.gather(*pending, return_exceptions=True)`, de modo que ninguna
  excepción de cancelación escapa del bloque `finally`.
- `RuntimeError` y `asyncio.CancelledError` producidas durante la limpieza
  se suprimen.

**Parámetros:** ninguno.

**Entrega (yield):** `asyncio.AbstractEventLoop`.

**Excepciones:** ninguna (los errores de limpieza se descartan de forma
intencional).

---

### `Loop.isLoopRunning()`

```python
@staticmethod
def isLoopRunning() -> bool
```

Devuelve `True` si hay un bucle de eventos corriendo actualmente en el hilo
que llama.

**Parámetros:** ninguno.

**Devuelve:** `bool`.

**Excepciones:** ninguna.

## Ejemplos de uso

### 1. Punto de entrada de la aplicación

```python
import asyncio
from orionis.aio import Loop

async def main() -> int:
    print("Aplicación iniciada")
    await asyncio.sleep(0.1)
    return 0

if __name__ == "__main__":
    exit_code = Loop.run(main())
    raise SystemExit(exit_code)
```

### 2. Invocar código asíncrono desde código síncrono (por ejemplo, un comando de CLI o un manejador de señales)

```python
from orionis.aio import Loop

async def fetch_greeting() -> str:
    return "Hola desde una tarea asíncrona"

def sync_entrypoint() -> None:
    # Funciona tanto si ya hay un bucle en ejecución como si no.
    message = Loop.runSync(fetch_greeting())
    print(message)
```

### 3. Invocar una función bloqueante desde código asíncrono sin detener el bucle

```python
import time
from orionis.aio import Loop

def slow_blocking_call(seconds: float) -> str:
    time.sleep(seconds)  # simula E/S bloqueante
    return "listo"

async def handler() -> None:
    result = await Loop.execute(slow_blocking_call, 0.5)
    print(result)
```

### 4. Programar una tarea en segundo plano e inspeccionar el estado del bucle

```python
import asyncio
from orionis.aio import Loop

async def background_job() -> None:
    await asyncio.sleep(1)
    print("tarea en segundo plano finalizada")

async def controller() -> None:
    print("bucle en ejecución:", Loop.isLoopRunning())  # True
    task = await Loop.createTask(background_job(), name="warmup")
    await task
```

### 5. Gestionar explícitamente el ciclo de vida de un bucle con limpieza

```python
from orionis.aio import Loop

def run_batch(coro) -> None:
    with Loop.eventLoopContext() as loop:
        loop.run_until_complete(coro)
        # Cualquier tarea que aún quede pendiente aquí se cancela y se
        # drena automáticamente al salir del bloque `with`.
```

## Notas de diseño

Las siguientes notas describen decisiones de diseño **ya existentes** con
fines exclusivamente informativos — no son propuestas de cambio.

- **Sin instancias, solo estado de clase.** `Loop` almacena todo su estado
  como atributos `ClassVar` (`_loop_local`, `_uvloop_factory`,
  `_sync_executor`, etc.) y expone únicamente miembros
  `@staticmethod`/`@classmethod`. Esto refleja un patrón de tipo
  singleton/namespace: la propia clase actúa como el gestor compartido.
- **Caché de bucle por hilo.** `_loop_local` es una instancia de
  `threading.local()`, de modo que `getEventLoop()` nunca filtra un bucle
  creado en un hilo hacia otro hilo distinto.
- **Bloqueo de doble verificación (double-checked locking).** Tanto
  `_detectUvloop()` (detección de uvloop) como `_getSyncExecutor()`
  (creación del executor compartido) usan una comprobación booleana fuera
  de un lock y la vuelven a comprobar dentro de él, de modo que la
  operación costosa (importación del módulo / creación del pool de hilos)
  se ejecuta como máximo una vez, incluso ante llamadas concurrentes en la
  primera invocación.
- **Orden de resolución de la fábrica de bucle.** `_getLoopFactory()`
  prefiere `uvloop` (fuera de Windows) primero, luego
  `asyncio.ProactorEventLoop` (Windows), y finalmente recurre a `None`, lo
  que significa "dejar que asyncio decida" mediante
  `asyncio.new_event_loop()`.
- **Pool de un solo trabajador para el puente síncrono/asíncrono.**
  `runSync()` se apoya en un
  `concurrent.futures.ThreadPoolExecutor(max_workers=1)` para ejecutar una
  corrutina en su propio bucle cuando se invoca desde dentro de un bucle ya
  en ejecución, evitando el clásico bloqueo mutuo de "no se puede ejecutar
  un bucle mientras otro bucle está en ejecución".
- **Apagado cooperativo.** `eventLoopContext()` cancela las tareas
  pendientes y las espera con `return_exceptions=True`, de modo que la
  limpieza nunca lanza una excepción ni oculta la excepción original del
  bloque `with`, si la hubiera.

## Consideraciones de rendimiento y concurrencia

Estas son notas informativas sobre el comportamiento existente, no
recomendaciones de optimización:

- La ruta rápida de `getEventLoop()` (`asyncio.get_running_loop()` dentro
  de un `try/except`) tiene un coste despreciable cuando ya hay un bucle en
  ejecución, que es el caso habitual dentro de los manejadores de
  solicitudes.
- La detección de `uvloop` y la resolución de la fábrica de bucle ocurren
  **como máximo una vez por proceso** (los resultados se almacenan en
  atributos de clase), por lo que llamadas repetidas a `getEventLoop()` o
  `run()` no vuelven a ejecutar la detección de plataforma.
- `runSync()` **bloquea el hilo que lo invoca** hasta que la corrutina
  finaliza. Dado que el executor de puente tiene exactamente **un**
  trabajador, las llamadas concurrentes a `runSync()` realizadas mientras
  ya hay un bucle en ejecución se serializan en ese único hilo trabajador
  — no se ejecutan en paralelo entre sí.
- `execute()` delega los invocables síncronos al executor **por defecto**
  del bucle (no al pool dedicado de un solo trabajador que usa
  `runSync()`), por lo que su nivel de concurrencia está determinado por
  el tamaño por defecto del executor de `asyncio`.
- `eventLoopContext()` solo cancela y drena las tareas pendientes cuando el
  bucle **no** está en ejecución en el momento de salir; si el bucle sigue
  en ejecución, la limpieza se omite en esa invocación.
- En plataformas distintas de Windows con `uvloop` instalado, tanto
  `getEventLoop()` como `run()` usan la implementación de bucle de
  `uvloop`, que habitualmente ofrece menor latencia de E/S que la
  implementación por defecto de la librería estándar; en Windows se usa en
  su lugar `ProactorEventLoop`, que admite operaciones de subprocesos y
  named pipes que el bucle selector por defecto no admite.

## Notas de compatibilidad

- **Versión mínima de Python:** 3.14 (el módulo depende de la sintaxis
  genérica de PEP 695: `def run[T](...)`, `def createTask[T](...)`,
  `def runSync[T](...)`).
- **Dependencias:**
  - Solo librería estándar: `asyncio`, `concurrent.futures`, `functools`,
    `inspect`, `sys`, `threading`, `types`, `contextlib`, `typing`.
  - `uvloop` — opcional a nivel de Python, pero declarada como dependencia
    normal del proyecto para plataformas distintas de Windows; se usa
    automáticamente cuando es importable, y se ignora silenciosamente en
    caso contrario (se captura el `ImportError`).
- **El comportamiento por plataforma difiere de forma intencional:** la
  implementación de bucle seleccionada en Windows (`ProactorEventLoop`)
  difiere de la seleccionada en Linux/macOS (`uvloop` o valor por defecto
  de la librería estándar) — esto es intencional y está documentado, no es
  un defecto.
