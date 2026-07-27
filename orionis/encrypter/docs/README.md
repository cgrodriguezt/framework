# Orionis Encrypter (`orionis.encrypter`)

> Authenticated, AES-based symmetric encryption service for the Orionis
> Framework, wired into the application container as the `IEncrypter`
> contract and the `Crypt` facade.
>
> 🇪🇸 Versión en español: [README.es.md](README.es.md)

`orionis.encrypter` provides a single, container-managed service —
`Encrypter` — that encrypts and decrypts strings using AES in either CBC or
GCM mode, driven entirely by the application's `app.key` / `app.cipher`
configuration values. It is the concrete implementation behind the
framework's `Crypt` facade.

---

## Table of contents

1. [Requirements](#requirements)
2. [What problem it solves](#what-problem-it-solves)
3. [API reference](#api-reference)
   - [`IEncrypter`](#iencrypter)
   - [`Encrypter`](#encrypter)
   - [`EncrypterProvider`](#encrypterprovider)
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

- **Python:** 3.14 or newer.
- **Third-party dependencies** (already declared by the framework):
  - [`cryptography`](https://pypi.org/project/cryptography/) `~=48.0` — AES
    primitives (`Cipher`, `algorithms`, `modes`, `AESGCM`).
  - [`msgspec`](https://pypi.org/project/msgspec/) `>=0.21.1` — fast,
    schema-validated JSON encoding/decoding of the internal payload
    structure.
- **Configuration:** an `app.key` and an `app.cipher` value must be
  available through `IApplication.config(...)` (typically populated from
  `config/app.py`, which in turn reads the `APP_KEY` / `APP_CIPHER`
  environment variables). If `APP_KEY` is unset, the framework generates
  one automatically at boot (`SecureKeyGenerator`, see
  [orionis/environment](../../environment)) and persists it back into the
  environment.

## What problem it solves

Applications routinely need to protect sensitive values at rest or in
transit — session payloads, signed tokens, stored secrets — without every
part of the codebase re-implementing key management, IV generation, padding
and authentication tags correctly. `orionis.encrypter` centralises this
concern:

- A single class, `Encrypter`, exposes just two operations —
  `encrypt(plaintext)` and `decrypt(payload)` — backed by AES in the mode
  configured for the application (`AES-128-CBC`, `AES-256-CBC`,
  `AES-128-GCM`, or `AES-256-GCM`).
- Key length, cipher support, and payload integrity (cipher match, IV size,
  authentication tag for GCM) are all validated internally, so callers
  cannot accidentally use a mismatched key/cipher combination without an
  explicit error.
- The encrypted payload is self-describing (it carries its own cipher name
  and IV/tag), while still refusing to decrypt with a different cipher than
  the one currently configured.
- `EncrypterProvider` wires `Encrypter` into the application container as a
  singleton bound to `IEncrypter`, and exposes it application-wide through
  the `Crypt` facade — no manual instantiation needed inside application
  code.

## API reference

### `IEncrypter`

```python
from orionis.encrypter.contracts.encrypter import IEncrypter
```

Abstract base class (`abc.ABC`) describing the encryption contract that
`Encrypter` (and the `Crypt` facade) implement.

| Member | Signature | Description |
| --- | --- | --- |
| `encrypt` | `def encrypt(self, plaintext: str) -> str` | Abstract method. Encrypts `plaintext` and returns a base64-encoded payload string. |
| `decrypt` | `def decrypt(self, payload: str) -> str` | Abstract method. Decrypts a previously produced payload back into the original plaintext string. |

**Raises:** instantiating `IEncrypter` directly raises `TypeError` (standard
`abc.ABC` behaviour), since both methods are abstract.

---

### `Encrypter`

```python
from orionis.encrypter.encrypter import Encrypter
```

Concrete implementation of `IEncrypter`. Uses `__slots__ = ("_aesgcm",
"_is_gcm", "cipher", "key")` — no dynamic attributes are allowed on
instances.

#### Class constants

| Constant | Value | Meaning |
| --- | --- | --- |
| `AES_128_KEY_SIZE` | `16` | Required key length, in bytes, for AES-128 ciphers. |
| `AES_256_KEY_SIZE` | `32` | Required key length, in bytes, for AES-256 ciphers. |
| `CBC_IV_SIZE` | `16` | Required IV length, in bytes, for CBC mode. |
| `GCM_IV_SIZE` | `12` | Required IV length, in bytes, for GCM mode. |
| `GCM_TAG_SIZE` | `16` | Required authentication tag length, in bytes, for GCM mode. |
| `PKCS7_BLOCK_SIZE` | `16` | Block size, in bytes, used for PKCS7 padding in CBC mode. |
| `SUPPORTED_CIPHERS` | `frozenset[str]` | The four supported cipher identifiers: `"AES-128-CBC"`, `"AES-256-CBC"`, `"AES-128-GCM"`, `"AES-256-GCM"` (mirrors `orionis.foundation.config.app.enums.ciphers.Cipher`). |

#### `Encrypter(app)`

Constructor.

| Parameter | Type | Description |
| --- | --- | --- |
| `app` | `IApplication` | The application instance; used to read `app.config("app.key")` and `app.config("app.cipher")`. |

**Behaviour:**

- Reads `self.key` from `app.config("app.key")` (expected to be `bytes`)
  and `self.cipher` from `app.config("app.cipher")` (a string identifying
  one of the supported ciphers).
- Validates that `self.cipher` is one of `SUPPORTED_CIPHERS`.
- Validates that `len(self.key)` matches the size required by the cipher
  family (`16` bytes for `AES-128-*`, `32` bytes for `AES-256-*`).
- Precomputes whether the cipher is a GCM variant and, if so, creates and
  caches an `AESGCM` instance (`self._aesgcm`) to avoid re-deriving the key
  schedule on every call.

**Raises:** `ValueError` if the cipher is unsupported or the key length
does not match the configured cipher.

#### `encrypter.encrypt(plaintext)`

```python
def encrypt(self, plaintext: str) -> str
```

Encrypts `plaintext` using the configured cipher and returns a
base64-encoded JSON payload containing the IV, ciphertext, authentication
tag (GCM only), and cipher identifier.

| Parameter | Type | Description |
| --- | --- | --- |
| `plaintext` | `str` | The text to encrypt. Must be non-empty. |

**Returns:** `str` — a base64-encoded, self-describing payload suitable for
storage or transmission, and for later use with `decrypt`.

**Raises:**
- `TypeError` if `plaintext` is not a `str`.
- `ValueError` if `plaintext` is empty, or if it cannot be encoded as UTF-8.
- `RuntimeError` if the underlying encryption operation fails for any other
  reason (wraps the original exception via `raise ... from e`).

**Side effects:** generates a fresh random IV via `os.urandom` on every
call (no state is retained between calls other than the cached key /
`AESGCM` instance).

#### `encrypter.decrypt(payload)`

```python
def decrypt(self, payload: str) -> str
```

Decrypts a payload previously produced by `encrypt` (or by any compatible
producer following the same wire format) and returns the original
plaintext.

| Parameter | Type | Description |
| --- | --- | --- |
| `payload` | `str` | Base64-encoded payload string, as returned by `encrypt`. Must be non-empty. |

**Returns:** `str` — the decrypted plaintext, decoded as UTF-8.

**Raises:**
- `TypeError` if `payload` is not a `str`.
- `ValueError` if `payload` is empty, cannot be base64/JSON-decoded, its
  cipher does not match the currently configured cipher, its IV size is
  wrong for the configured mode, or (for GCM) its authentication tag is
  missing or has the wrong size.
- `RuntimeError` if decryption itself fails (e.g. authentication failure in
  GCM mode, or a corrupted/invalid PKCS7 padding in CBC mode) — wraps the
  original exception via `raise ... from e`.

> Internally, `decrypt` delegates to several private (name-mangled) helper
> methods — `__decodePayload`, `__extractPayloadData`,
> `__validateCipherMatch`, `__validateIvSize`, `__performDecryption`,
> `__encryptCBC` / `__decryptCBC`, `__encryptGCM` / `__decryptGCM` — which
> are implementation details, not part of the public API.

---

### `EncrypterProvider`

```python
from orionis.encrypter.provider import EncrypterProvider
```

Service provider that wires `Encrypter` into the application container.
Inherits from both `ServiceProvider` and `DeferrableProvider`.

| Member | Signature | Description |
| --- | --- | --- |
| `provides` | `@classmethod def provides(cls) -> list[type]` | Returns `[IEncrypter]` — declares which service types this provider is responsible for, enabling deferred (on-demand) loading. |
| `register` | `def register(self) -> None` | Binds `IEncrypter` to `Encrypter` as a **singleton** in the application container (`self.app.singleton(IEncrypter, Encrypter)`). |
| `boot` | `async def boot(self) -> None` | Pins the `Crypt` facade (`await CryptFacade.pin()`) so `orionis.support.facades.encrypter.Crypt` resolves to the registered `Encrypter` singleton. |

**Returns / Raises:** none beyond what the underlying container methods
raise (e.g. if `IEncrypter` cannot be resolved).

## Usage examples

### 1. Resolving the encrypter through the `Crypt` facade

```python
from orionis.support.facades.encrypter import Crypt

def store_secret(raw_value: str) -> str:
    return Crypt.encrypt(raw_value)

def read_secret(stored_value: str) -> str:
    return Crypt.decrypt(stored_value)

token = store_secret("super-secret-value")
original = read_secret(token)
assert original == "super-secret-value"
```

### 2. Encrypting and decrypting a round trip directly with `Encrypter`

```python
from orionis.encrypter.encrypter import Encrypter

class _ConfigStub:
    """Minimal stand-in for IApplication.config(...) used here for illustration."""

    def __init__(self, key: bytes, cipher: str) -> None:
        self._values = {"app.key": key, "app.cipher": cipher}

    def config(self, path: str) -> object:
        return self._values[path]

# A real application supplies these from config/app.py (APP_KEY / APP_CIPHER).
key_32_bytes = b"\x9f" * 32
app = _ConfigStub(key_32_bytes, "AES-256-GCM")

encrypter = Encrypter(app)
payload = encrypter.encrypt("hello world")
plaintext = encrypter.decrypt(payload)
assert plaintext == "hello world"
```

### 3. Handling invalid input explicitly

```python
from orionis.encrypter.encrypter import Encrypter

def safe_decrypt(encrypter: Encrypter, payload: str) -> str | None:
    try:
        return encrypter.decrypt(payload)
    except (TypeError, ValueError) as exc:
        # Malformed payload, empty input, cipher mismatch, or bad IV/tag size.
        print(f"Rejected payload: {exc}")
        return None
    except RuntimeError as exc:
        # Authentication failure (GCM) or corrupted padding (CBC).
        print(f"Decryption failed: {exc}")
        return None
```

### 4. Registering the provider manually (advanced / testing scenarios)

```python
from orionis.encrypter.provider import EncrypterProvider
from orionis.encrypter.contracts.encrypter import IEncrypter

# `app` is an Orionis Application/container instance.
provider = EncrypterProvider(app)
provider.register()      # binds IEncrypter -> Encrypter as a singleton
await provider.boot()     # pins the Crypt facade

encrypter = app.make(IEncrypter)
token = encrypter.encrypt("value to protect")
```

## Design notes

The following notes describe **existing** design decisions for
informational purposes only — they are not suggestions for change.

- **`__slots__` for memory efficiency.** `Encrypter` declares
  `__slots__ = ("_aesgcm", "_is_gcm", "cipher", "key")`, preventing dynamic
  attribute creation and avoiding a per-instance `__dict__` — appropriate
  for a service that is typically instantiated once (as a container
  singleton).
- **Precomputed mode flag and cached `AESGCM`.** `_is_gcm` is computed once
  in the constructor (`"GCM" in self.cipher`) rather than re-checked on
  every `encrypt`/`decrypt` call, and the `AESGCM` instance (which performs
  key-schedule setup) is created once and reused, avoiding repeated
  per-call overhead.
- **Self-describing payload via `msgspec.Struct`.** The internal
  `_Payload` struct (`msgspec.Struct, gc=False`) models the wire format —
  `iv`, `value`, `tag`, `cipher`, all base64-encoded strings — and is
  encoded/decoded with `msgspec.json`, which validates the payload shape
  strictly while decoding (unexpected/missing fields raise
  `msgspec.DecodeError`, translated into a `ValueError` by `decrypt`).
  `_Payload` is a module-private implementation detail, not part of the
  public API surface.
- **Defence in depth on decrypt.** `decrypt` explicitly re-validates that
  the payload's `cipher` matches the instance's configured cipher and that
  the IV length matches the expected size for the mode, in addition to
  relying on AES-GCM's built-in authentication tag — so a payload produced
  under a different cipher/key configuration is rejected before any actual
  cryptographic operation is attempted.
- **PKCS7 padding implemented manually for CBC.** Since AES-CBC (unlike
  GCM) is not authenticated and does not handle padding on its own, `
  Encrypter` applies/removes PKCS7 padding by hand
  (`PKCS7_BLOCK_SIZE = 16`) around the `cryptography` library's raw CBC
  cipher object.
- **Configuration-driven, not parameter-driven.** The cipher and key are
  resolved once, at construction time, from `app.config("app.cipher")` /
  `app.config("app.key")` — there is no way to pass a different key or
  cipher to an individual `encrypt`/`decrypt` call; a new `Encrypter`
  instance (or a differently configured application) would be required for
  that.

## Performance and concurrency considerations

These are informative notes about existing behaviour, not tuning advice:

- `Encrypter` is registered as a **singleton** by `EncrypterProvider`, so
  the (relatively cheap) key-schedule setup for GCM (`AESGCM(self.key)`)
  happens once per application process, not once per request.
- Both `encrypt` and `decrypt` are **fully synchronous, CPU-bound**
  operations (no `await`, no I/O). When called from within `async def`
  request handlers, they will run on the event loop thread; for very large
  payloads or very high request rates, this occupies the loop the same way
  any other synchronous CPU work does. The framework does not offload
  these calls to a thread pool automatically — do that explicitly (e.g.
  via `orionis.aio.Loop.execute`) if profiling shows it is needed for your
  workload.
- `Encrypter` instances are **not** documented as thread-safe for
  concurrent mutation (there is none — all mutable state is set once in
  `__init__`), so multiple threads calling `encrypt`/`decrypt`
  concurrently on the same singleton instance only share read-only state
  (`self.key`, `self.cipher`, `self._aesgcm`), which the underlying
  `cryptography` library is designed to support for concurrent, independent
  operations.
- A fresh, cryptographically random IV (`os.urandom`) is generated on
  **every** `encrypt` call — repeated encryption of the same plaintext
  will not produce the same ciphertext, which is expected and required for
  AES-CBC/AES-GCM security guarantees, but also means ciphertext length and
  payload size scale with the size of the wrapped IV/tag/JSON overhead in
  addition to the plaintext itself.

## Compatibility notes

- **Minimum Python version:** 3.14.
- **Dependencies:**
  - `cryptography ~= 48.0` — provides `Cipher`, `algorithms`, `modes`, and
    `AESGCM`.
  - `msgspec >= 0.21.1` — provides `msgspec.Struct` and `msgspec.json` used
    to encode/decode the internal payload format.
  - Standard library: `base64`, `os`, `typing`.
- **Framework integration:** `Encrypter` requires an `IApplication`
  instance exposing a `config(path: str)` method that resolves
  `"app.key"` (bytes) and `"app.cipher"` (a string matching one of
  `SUPPORTED_CIPHERS`). In a full Orionis application these values
  originate from `config/app.py` (`APP_KEY` / `APP_CIPHER` environment
  variables), with `APP_KEY` auto-generated on first boot if unset.
