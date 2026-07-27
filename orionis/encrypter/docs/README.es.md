# Encrypter de Orionis (`orionis.encrypter`)

> Servicio de cifrado simétrico autenticado basado en AES para el Orionis
> Framework, integrado en el contenedor de la aplicación como el contrato
> `IEncrypter` y la fachada `Crypt`.
>
> 🇬🇧 English version: [README.md](README.md)

`orionis.encrypter` provee un único servicio gestionado por el contenedor —
`Encrypter` — que cifra y descifra cadenas de texto usando AES en modo CBC
o GCM, controlado enteramente por los valores de configuración `app.key` /
`app.cipher` de la aplicación. Es la implementación concreta detrás de la
fachada `Crypt` del framework.

---

## Tabla de contenidos

1. [Requisitos](#requisitos)
2. [Qué problema resuelve](#qué-problema-resuelve)
3. [Referencia de API](#referencia-de-api)
   - [`IEncrypter`](#iencrypter)
   - [`Encrypter`](#encrypter)
   - [`EncrypterProvider`](#encrypterprovider)
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

- **Python:** 3.14 o superior.
- **Dependencias de terceros** (ya declaradas por el framework):
  - [`cryptography`](https://pypi.org/project/cryptography/) `~=48.0` —
    primitivas AES (`Cipher`, `algorithms`, `modes`, `AESGCM`).
  - [`msgspec`](https://pypi.org/project/msgspec/) `>=0.21.1` —
    codificación/decodificación JSON rápida y validada por esquema para la
    estructura interna del payload.
- **Configuración:** deben existir valores `app.key` y `app.cipher`
  accesibles a través de `IApplication.config(...)` (típicamente
  provenientes de `config/app.py`, que a su vez lee las variables de
  entorno `APP_KEY` / `APP_CIPHER`). Si `APP_KEY` no está definida, el
  framework genera una automáticamente al arrancar
  (`SecureKeyGenerator`, ver [orionis/environment](../../environment)) y la
  persiste de vuelta en el entorno.

## Qué problema resuelve

Las aplicaciones necesitan con frecuencia proteger valores sensibles en
reposo o en tránsito — datos de sesión, tokens firmados, secretos
almacenados — sin que cada parte del código tenga que reimplementar
correctamente la gestión de claves, la generación de IV, el relleno
(padding) y las etiquetas de autenticación. `orionis.encrypter` centraliza
esta responsabilidad:

- Una única clase, `Encrypter`, expone solo dos operaciones —
  `encrypt(plaintext)` y `decrypt(payload)` — respaldadas por AES en el
  modo configurado para la aplicación (`AES-128-CBC`, `AES-256-CBC`,
  `AES-128-GCM` o `AES-256-GCM`).
- La longitud de la clave, el soporte del cifrador y la integridad del
  payload (coincidencia de cifrador, tamaño de IV, etiqueta de
  autenticación para GCM) se validan internamente, por lo que quien llama
  no puede usar accidentalmente una combinación de clave/cifrador
  incompatible sin recibir un error explícito.
- El payload cifrado es autodescriptivo (incluye su propio nombre de
  cifrador e IV/etiqueta), pero aun así se niega a descifrar con un
  cifrador distinto al configurado actualmente.
- `EncrypterProvider` conecta `Encrypter` al contenedor de la aplicación
  como un singleton vinculado a `IEncrypter`, y lo expone en toda la
  aplicación mediante la fachada `Crypt` — sin necesidad de instanciarlo
  manualmente dentro del código de la aplicación.

## Referencia de API

### `IEncrypter`

```python
from orionis.encrypter.contracts.encrypter import IEncrypter
```

Clase base abstracta (`abc.ABC`) que describe el contrato de cifrado que
implementan `Encrypter` (y la fachada `Crypt`).

| Miembro | Firma | Descripción |
| --- | --- | --- |
| `encrypt` | `def encrypt(self, plaintext: str) -> str` | Método abstracto. Cifra `plaintext` y devuelve un payload codificado en base64. |
| `decrypt` | `def decrypt(self, payload: str) -> str` | Método abstracto. Descifra un payload previamente producido y devuelve el texto original. |

**Excepciones:** instanciar `IEncrypter` directamente lanza `TypeError`
(comportamiento estándar de `abc.ABC`), ya que ambos métodos son
abstractos.

---

### `Encrypter`

```python
from orionis.encrypter.encrypter import Encrypter
```

Implementación concreta de `IEncrypter`. Usa
`__slots__ = ("_aesgcm", "_is_gcm", "cipher", "key")` — no se permiten
atributos dinámicos en las instancias.

#### Constantes de clase

| Constante | Valor | Significado |
| --- | --- | --- |
| `AES_128_KEY_SIZE` | `16` | Longitud de clave requerida, en bytes, para los cifradores AES-128. |
| `AES_256_KEY_SIZE` | `32` | Longitud de clave requerida, en bytes, para los cifradores AES-256. |
| `CBC_IV_SIZE` | `16` | Longitud de IV requerida, en bytes, para el modo CBC. |
| `GCM_IV_SIZE` | `12` | Longitud de IV requerida, en bytes, para el modo GCM. |
| `GCM_TAG_SIZE` | `16` | Longitud de la etiqueta de autenticación, en bytes, requerida para el modo GCM. |
| `PKCS7_BLOCK_SIZE` | `16` | Tamaño de bloque, en bytes, usado para el relleno PKCS7 en modo CBC. |
| `SUPPORTED_CIPHERS` | `frozenset[str]` | Los cuatro identificadores de cifrador soportados: `"AES-128-CBC"`, `"AES-256-CBC"`, `"AES-128-GCM"`, `"AES-256-GCM"` (refleja `orionis.foundation.config.app.enums.ciphers.Cipher`). |

#### `Encrypter(app)`

Constructor.

| Parámetro | Tipo | Descripción |
| --- | --- | --- |
| `app` | `IApplication` | La instancia de la aplicación; se usa para leer `app.config("app.key")` y `app.config("app.cipher")`. |

**Comportamiento:**

- Lee `self.key` desde `app.config("app.key")` (se espera que sea
  `bytes`) y `self.cipher` desde `app.config("app.cipher")` (una cadena
  que identifica uno de los cifradores soportados).
- Valida que `self.cipher` sea uno de los `SUPPORTED_CIPHERS`.
- Valida que `len(self.key)` coincida con el tamaño requerido por la
  familia del cifrador (`16` bytes para `AES-128-*`, `32` bytes para
  `AES-256-*`).
- Precalcula si el cifrador es una variante GCM y, en ese caso, crea y
  almacena en caché una instancia `AESGCM` (`self._aesgcm`) para evitar
  recalcular el key schedule en cada llamada.

**Excepciones:** `ValueError` si el cifrador no es compatible o si la
longitud de la clave no coincide con el cifrador configurado.

#### `encrypter.encrypt(plaintext)`

```python
def encrypt(self, plaintext: str) -> str
```

Cifra `plaintext` usando el cifrador configurado y devuelve un payload
JSON codificado en base64 que contiene el IV, el texto cifrado, la
etiqueta de autenticación (solo GCM) y el identificador del cifrador.

| Parámetro | Tipo | Descripción |
| --- | --- | --- |
| `plaintext` | `str` | El texto a cifrar. Debe ser no vacío. |

**Devuelve:** `str` — un payload autodescriptivo codificado en base64,
apto para almacenamiento o transmisión, y para su uso posterior con
`decrypt`.

**Excepciones:**
- `TypeError` si `plaintext` no es un `str`.
- `ValueError` si `plaintext` está vacío, o si no puede codificarse como
  UTF-8.
- `RuntimeError` si la operación de cifrado subyacente falla por
  cualquier otro motivo (envuelve la excepción original mediante
  `raise ... from e`).

**Efectos secundarios:** genera un IV aleatorio nuevo mediante
`os.urandom` en cada llamada (no se conserva ningún estado entre llamadas
más allá de la clave en caché / la instancia `AESGCM`).

#### `encrypter.decrypt(payload)`

```python
def decrypt(self, payload: str) -> str
```

Descifra un payload previamente producido por `encrypt` (o por cualquier
productor compatible que siga el mismo formato de intercambio) y devuelve
el texto original.

| Parámetro | Tipo | Descripción |
| --- | --- | --- |
| `payload` | `str` | Cadena de payload codificada en base64, tal como la devuelve `encrypt`. Debe ser no vacía. |

**Devuelve:** `str` — el texto descifrado, decodificado como UTF-8.

**Excepciones:**
- `TypeError` si `payload` no es un `str`.
- `ValueError` si `payload` está vacío, no puede decodificarse como
  base64/JSON, su cifrador no coincide con el cifrador actualmente
  configurado, el tamaño de su IV es incorrecto para el modo configurado,
  o (en GCM) su etiqueta de autenticación falta o tiene un tamaño
  incorrecto.
- `RuntimeError` si el propio descifrado falla (por ejemplo, un fallo de
  autenticación en modo GCM, o un relleno PKCS7 corrupto o inválido en
  modo CBC) — envuelve la excepción original mediante `raise ... from e`.

> Internamente, `decrypt` delega en varios métodos auxiliares privados
> (con "name mangling") — `__decodePayload`, `__extractPayloadData`,
> `__validateCipherMatch`, `__validateIvSize`, `__performDecryption`,
> `__encryptCBC` / `__decryptCBC`, `__encryptGCM` / `__decryptGCM` —, que
> son detalles de implementación y no forman parte de la API pública.

---

### `EncrypterProvider`

```python
from orionis.encrypter.provider import EncrypterProvider
```

Proveedor de servicio que conecta `Encrypter` al contenedor de la
aplicación. Hereda de `ServiceProvider` y de `DeferrableProvider`.

| Miembro | Firma | Descripción |
| --- | --- | --- |
| `provides` | `@classmethod def provides(cls) -> list[type]` | Devuelve `[IEncrypter]` — declara qué tipos de servicio gestiona este proveedor, habilitando la carga diferida (bajo demanda). |
| `register` | `def register(self) -> None` | Vincula `IEncrypter` a `Encrypter` como un **singleton** en el contenedor de la aplicación (`self.app.singleton(IEncrypter, Encrypter)`). |
| `boot` | `async def boot(self) -> None` | Fija (pin) la fachada `Crypt` (`await CryptFacade.pin()`) para que `orionis.support.facades.encrypter.Crypt` resuelva al singleton `Encrypter` registrado. |

**Devuelve / Excepciones:** ninguna adicional más allá de las que lancen
los métodos subyacentes del contenedor (por ejemplo, si `IEncrypter` no
puede resolverse).

## Ejemplos de uso

### 1. Resolver el encrypter a través de la fachada `Crypt`

```python
from orionis.support.facades.encrypter import Crypt

def store_secret(raw_value: str) -> str:
    return Crypt.encrypt(raw_value)

def read_secret(stored_value: str) -> str:
    return Crypt.decrypt(stored_value)

token = store_secret("valor-super-secreto")
original = read_secret(token)
assert original == "valor-super-secreto"
```

### 2. Ciclo de cifrado y descifrado directamente con `Encrypter`

```python
from orionis.encrypter.encrypter import Encrypter

class _ConfigStub:
    """Sustituto mínimo de IApplication.config(...) usado aquí solo a modo ilustrativo."""

    def __init__(self, key: bytes, cipher: str) -> None:
        self._values = {"app.key": key, "app.cipher": cipher}

    def config(self, path: str) -> object:
        return self._values[path]

# Una aplicación real obtiene estos valores desde config/app.py (APP_KEY / APP_CIPHER).
key_32_bytes = b"\x9f" * 32
app = _ConfigStub(key_32_bytes, "AES-256-GCM")

encrypter = Encrypter(app)
payload = encrypter.encrypt("hola mundo")
plaintext = encrypter.decrypt(payload)
assert plaintext == "hola mundo"
```

### 3. Manejar entradas inválidas de forma explícita

```python
from orionis.encrypter.encrypter import Encrypter

def safe_decrypt(encrypter: Encrypter, payload: str) -> str | None:
    try:
        return encrypter.decrypt(payload)
    except (TypeError, ValueError) as exc:
        # Payload malformado, entrada vacía, cifrador incompatible o tamaño de IV/etiqueta incorrecto.
        print(f"Payload rechazado: {exc}")
        return None
    except RuntimeError as exc:
        # Fallo de autenticación (GCM) o relleno corrupto (CBC).
        print(f"Fallo al descifrar: {exc}")
        return None
```

### 4. Registrar el proveedor manualmente (escenarios avanzados / de pruebas)

```python
from orionis.encrypter.provider import EncrypterProvider
from orionis.encrypter.contracts.encrypter import IEncrypter

# `app` es una instancia de Application/contenedor de Orionis.
provider = EncrypterProvider(app)
provider.register()      # vincula IEncrypter -> Encrypter como singleton
await provider.boot()     # fija la fachada Crypt

encrypter = app.make(IEncrypter)
token = encrypter.encrypt("valor a proteger")
```

## Notas de diseño

Las siguientes notas describen decisiones de diseño **ya existentes** con
fines exclusivamente informativos — no son propuestas de cambio.

- **`__slots__` por eficiencia de memoria.** `Encrypter` declara
  `__slots__ = ("_aesgcm", "_is_gcm", "cipher", "key")`, lo que impide la
  creación dinámica de atributos y evita un `__dict__` por instancia —
  apropiado para un servicio que típicamente se instancia una sola vez
  (como singleton del contenedor).
- **Indicador de modo precalculado y `AESGCM` en caché.** `_is_gcm` se
  calcula una sola vez en el constructor (`"GCM" in self.cipher`) en lugar
  de volver a comprobarse en cada llamada a `encrypt`/`decrypt`, y la
  instancia `AESGCM` (que realiza la configuración del key schedule) se
  crea una vez y se reutiliza, evitando el costo repetido en cada llamada.
- **Payload autodescriptivo mediante `msgspec.Struct`.** La estructura
  interna `_Payload` (`msgspec.Struct, gc=False`) modela el formato de
  intercambio — `iv`, `value`, `tag`, `cipher`, todos cadenas codificadas
  en base64 — y se codifica/decodifica con `msgspec.json`, que valida
  estrictamente la forma del payload al decodificar (campos
  inesperados/faltantes lanzan `msgspec.DecodeError`, traducido a un
  `ValueError` por `decrypt`). `_Payload` es un detalle de implementación
  privado del módulo, no forma parte de la superficie de la API pública.
- **Defensa en profundidad al descifrar.** `decrypt` revalida
  explícitamente que el `cipher` del payload coincida con el cifrador
  configurado de la instancia y que la longitud del IV coincida con el
  tamaño esperado para el modo, además de apoyarse en la etiqueta de
  autenticación integrada de AES-GCM — de modo que un payload producido
  bajo una configuración distinta de cifrador/clave se rechaza antes de
  intentar cualquier operación criptográfica real.
- **Relleno PKCS7 implementado manualmente para CBC.** Dado que AES-CBC (a
  diferencia de GCM) no está autenticado y no gestiona el relleno por sí
  mismo, `Encrypter` aplica/elimina el relleno PKCS7 a mano
  (`PKCS7_BLOCK_SIZE = 16`) alrededor del objeto de cifrado CBC crudo de
  la librería `cryptography`.
- **Impulsado por configuración, no por parámetros.** El cifrador y la
  clave se resuelven una sola vez, en el momento de la construcción, desde
  `app.config("app.cipher")` / `app.config("app.key")` — no existe forma
  de pasar una clave o cifrador distinto a una llamada individual de
  `encrypt`/`decrypt`; se necesitaría una nueva instancia de `Encrypter`
  (o una aplicación configurada de otra manera) para eso.

## Consideraciones de rendimiento y concurrencia

Estas son notas informativas sobre el comportamiento existente, no
recomendaciones de optimización:

- `Encrypter` se registra como **singleton** por parte de
  `EncrypterProvider`, por lo que la configuración del key schedule para
  GCM (`AESGCM(self.key)`), relativamente económica, ocurre una sola vez
  por proceso de la aplicación, no una vez por solicitud.
- Tanto `encrypt` como `decrypt` son operaciones **totalmente síncronas y
  ligadas a CPU** (sin `await`, sin E/S). Cuando se llaman desde
  manejadores de solicitudes `async def`, se ejecutan en el hilo del bucle
  de eventos; para payloads muy grandes o tasas de solicitudes muy altas,
  esto ocupa el bucle igual que cualquier otro trabajo síncrono ligado a
  CPU. El framework no delega estas llamadas automáticamente a un pool de
  hilos — hágalo explícitamente (por ejemplo, mediante
  `orionis.aio.Loop.execute`) si el perfilado muestra que es necesario
  para su carga de trabajo.
- Las instancias de `Encrypter` no están documentadas como thread-safe
  frente a mutación concurrente (no la hay — todo el estado mutable se
  establece una vez en `__init__`), por lo que múltiples hilos que llamen
  a `encrypt`/`decrypt` concurrentemente sobre la misma instancia
  singleton solo comparten estado de solo lectura (`self.key`,
  `self.cipher`, `self._aesgcm`), lo cual la librería `cryptography`
  subyacente está diseñada para soportar en operaciones concurrentes e
  independientes.
- Se genera un IV nuevo y criptográficamente aleatorio (`os.urandom`) en
  **cada** llamada a `encrypt` — cifrar repetidamente el mismo texto plano
  no producirá el mismo texto cifrado, lo cual es esperado y necesario
  para las garantías de seguridad de AES-CBC/AES-GCM, pero también implica
  que la longitud del texto cifrado y el tamaño del payload crecen con el
  overhead del IV/etiqueta/JSON envuelto, además del propio texto plano.

## Notas de compatibilidad

- **Versión mínima de Python:** 3.14.
- **Dependencias:**
  - `cryptography ~= 48.0` — provee `Cipher`, `algorithms`, `modes` y
    `AESGCM`.
  - `msgspec >= 0.21.1` — provee `msgspec.Struct` y `msgspec.json`, usados
    para codificar/decodificar el formato interno del payload.
  - Librería estándar: `base64`, `os`, `typing`.
- **Integración con el framework:** `Encrypter` requiere una instancia de
  `IApplication` que exponga un método `config(path: str)` capaz de
  resolver `"app.key"` (bytes) y `"app.cipher"` (una cadena que coincida
  con uno de los `SUPPORTED_CIPHERS`). En una aplicación Orionis completa,
  estos valores provienen de `config/app.py` (variables de entorno
  `APP_KEY` / `APP_CIPHER`), generándose `APP_KEY` automáticamente en el
  primer arranque si no está definida.
