import base64
import json
from orionis.services.encrypter.encrypter import Encrypter
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Minimal IApplication stub — provides config("app.key") and config("app.cipher")
# without requiring the full Orionis application bootstrap.
# ---------------------------------------------------------------------------

_KEY_16 = b"a" * 16   # 128-bit key
_KEY_32 = b"b" * 32   # 256-bit key

class _AppStub:
    """Lightweight stand-in for IApplication used exclusively in these tests."""

    def __init__(self, key: bytes, cipher: str) -> None:
        self._data = {"app.key": key, "app.cipher": cipher}

    def config(self, key_path: str):  # noqa: ANN201
        return self._data[key_path]

def _make(cipher: str, key: bytes | None = None) -> Encrypter:
    """Convenience factory that returns a configured Encrypter."""
    if key is None:
        key = _KEY_16 if "128" in cipher else _KEY_32
    return Encrypter(_AppStub(key, cipher))

# ===========================================================================
# TestEncrypterInit
# ===========================================================================

class TestEncrypterInit(TestCase):

    def testInitAes128CbcSucceeds(self) -> None:
        """
        Test that Encrypter can be initialised with AES-128-CBC.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        self.assertIsInstance(enc, Encrypter)

    def testInitAes256CbcSucceeds(self) -> None:
        """
        Test that Encrypter can be initialised with AES-256-CBC.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        self.assertIsInstance(enc, Encrypter)

    def testInitAes128GcmSucceeds(self) -> None:
        """
        Test that Encrypter can be initialised with AES-128-GCM.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        self.assertIsInstance(enc, Encrypter)

    def testInitAes256GcmSucceeds(self) -> None:
        """
        Test that Encrypter can be initialised with AES-256-GCM.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        self.assertIsInstance(enc, Encrypter)

    def testInitUnsupportedCipherRaisesValueError(self) -> None:
        """
        Test that an unsupported cipher string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Encrypter(_AppStub(_KEY_16, "DES-128-CBC"))

    def testInitAes128WithWrongKeyLengthRaisesValueError(self) -> None:
        """
        Test that a 32-byte key with AES-128 raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Encrypter(_AppStub(_KEY_32, "AES-128-CBC"))

    def testInitAes256WithWrongKeyLengthRaisesValueError(self) -> None:
        """
        Test that a 16-byte key with AES-256 raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Encrypter(_AppStub(_KEY_16, "AES-256-CBC"))

    def testInitAes128GcmWithWrongKeyRaisesValueError(self) -> None:
        """
        Test that a 32-byte key with AES-128-GCM raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Encrypter(_AppStub(_KEY_32, "AES-128-GCM"))

    def testInitAes256GcmWithWrongKeyRaisesValueError(self) -> None:
        """
        Test that a 16-byte key with AES-256-GCM raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Encrypter(_AppStub(_KEY_16, "AES-256-GCM"))

    def testInitStoresKeyAttributeCorrectly(self) -> None:
        """
        Test that the key attribute is stored as the value provided by the app.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC", _KEY_16)
        self.assertEqual(enc.key, _KEY_16)

    def testInitStoresCipherAttributeCorrectly(self) -> None:
        """
        Test that the cipher attribute reflects the configured cipher string.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM", _KEY_32)
        self.assertEqual(enc.cipher, "AES-256-GCM")

    def testSupportedCiphersListIsNotEmpty(self) -> None:
        """
        Test that SUPPORTED_CIPHERS class variable contains at least one value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(Encrypter.SUPPORTED_CIPHERS), 0)

    def testSupportedCiphersContainsAllFourModes(self) -> None:
        """
        Test that SUPPORTED_CIPHERS includes all four expected AES cipher modes.

        Returns
        -------
        None
            This method does not return a value.
        """
        for expected in ("AES-128-CBC", "AES-256-CBC", "AES-128-GCM", "AES-256-GCM"):
            self.assertIn(expected, Encrypter.SUPPORTED_CIPHERS)

# ===========================================================================
# TestEncrypterEncryptErrors
# ===========================================================================

class TestEncrypterEncryptErrors(TestCase):

    def testEncryptNonStringRaisesTypeError(self) -> None:
        """
        Test that passing a non-string to encrypt() raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        with self.assertRaises(TypeError):
            enc.encrypt(42)  # type: ignore[arg-type]

    def testEncryptNoneRaisesTypeError(self) -> None:
        """
        Test that passing None to encrypt() raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        with self.assertRaises(TypeError):
            enc.encrypt(None)  # type: ignore[arg-type]

    def testEncryptEmptyStringRaisesValueError(self) -> None:
        """
        Test that passing an empty string to encrypt() raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        with self.assertRaises(ValueError):
            enc.encrypt("")

    def testEncryptListRaisesTypeError(self) -> None:
        """
        Test that passing a list to encrypt() raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        with self.assertRaises(TypeError):
            enc.encrypt(["a", "b"])  # type: ignore[arg-type]

    def testEncryptIntZeroRaisesTypeError(self) -> None:
        """
        Test that passing the integer 0 to encrypt() raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        with self.assertRaises(TypeError):
            enc.encrypt(0)  # type: ignore[arg-type]

# ===========================================================================
# TestEncrypterDecryptErrors
# ===========================================================================

class TestEncrypterDecryptErrors(TestCase):

    def testDecryptNonStringRaisesTypeError(self) -> None:
        """
        Test that passing a non-string to decrypt() raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        with self.assertRaises(TypeError):
            enc.decrypt(123)  # type: ignore[arg-type]

    def testDecryptEmptyStringRaisesValueError(self) -> None:
        """
        Test that passing an empty string to decrypt() raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        with self.assertRaises(ValueError):
            enc.decrypt("")

    def testDecryptNoneRaisesTypeError(self) -> None:
        """
        Test that passing None to decrypt() raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        with self.assertRaises(TypeError):
            enc.decrypt(None)  # type: ignore[arg-type]

    def testDecryptInvalidBase64RaisesValueError(self) -> None:
        """
        Test that a non-base64 string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        with self.assertRaises((ValueError, RuntimeError)):
            enc.decrypt("!!!not_base64!!!")

    def testDecryptPayloadMissingIvFieldRaisesValueError(self) -> None:
        """
        Test that a payload missing the 'iv' field raises ValueError or RuntimeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        bad_payload = base64.b64encode(
            json.dumps({"value": "abc", "cipher": "AES-128-GCM"}).encode()
        ).decode()
        with self.assertRaises((ValueError, RuntimeError)):
            enc.decrypt(bad_payload)

    def testDecryptPayloadMissingValueFieldRaisesValueError(self) -> None:
        """
        Test that a payload missing the 'value' field raises ValueError or RuntimeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        bad_payload = base64.b64encode(
            json.dumps({"iv": "abc", "cipher": "AES-128-CBC"}).encode()
        ).decode()
        with self.assertRaises((ValueError, RuntimeError)):
            enc.decrypt(bad_payload)

    def testDecryptCipherMismatchRaisesValueError(self) -> None:
        """
        Test that a payload with a different cipher than configured raises an error.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        # Build a minimally valid-looking payload but with a different cipher name
        dummy_iv = base64.b64encode(b"\x00" * 16).decode()
        dummy_val = base64.b64encode(b"\x00" * 16).decode()
        bad_payload = base64.b64encode(
            json.dumps({
                "iv": dummy_iv,
                "value": dummy_val,
                "cipher": "AES-256-CBC",
            }).encode()
        ).decode()
        with self.assertRaises((ValueError, RuntimeError)):
            enc.decrypt(bad_payload)


# ===========================================================================
# TestEncrypterRoundtripCBC
# ===========================================================================

class TestEncrypterRoundtripCBC(TestCase):

    def testRoundtripAes128Cbc(self) -> None:
        """
        Test that AES-128-CBC encrypt then decrypt yields the original plaintext.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        original = "Hello, AES-128-CBC!"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundtripAes256Cbc(self) -> None:
        """
        Test that AES-256-CBC encrypt then decrypt yields the original plaintext.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        original = "Hello, AES-256-CBC!"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testCbcEncryptReturnsDifferentPayloadOnEachCall(self) -> None:
        """
        Test that two encryptions of the same plaintext produce different ciphertexts
        (due to random IV generation in CBC mode).

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        ct1 = enc.encrypt("same text")
        ct2 = enc.encrypt("same text")
        self.assertNotEqual(ct1, ct2)

    def testCbcEncryptedPayloadIsValidBase64(self) -> None:
        """
        Test that the encrypted payload returned by CBC mode is valid base64.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        payload = enc.encrypt("test payload")
        decoded = base64.b64decode(payload)  # Must not raise
        self.assertIsInstance(decoded, bytes)

    def testCbcEncryptedPayloadContainsCipherField(self) -> None:
        """
        Test that the decoded CBC payload JSON includes a 'cipher' field.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        payload = enc.encrypt("check cipher field")
        data = json.loads(base64.b64decode(payload).decode())
        self.assertIn("cipher", data)
        self.assertEqual(data["cipher"], "AES-128-CBC")

    def testCbcRoundtripWithLongText(self) -> None:
        """
        Test CBC roundtrip with a long plaintext (> one AES block).

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        original = "x" * 500
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testCbcRoundtripWithSingleCharacter(self) -> None:
        """
        Test CBC roundtrip with a single character as plaintext.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        self.assertEqual(enc.decrypt(enc.encrypt("A")), "A")

    def testCbcRoundtripWithSpecialCharacters(self) -> None:
        """
        Test CBC roundtrip with special characters and unicode.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        original = "!@#$%^&*() áéíóú ñ 中文 🔒"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testCbcEncryptedPayloadHasIvValueCipherKeys(self) -> None:
        """
        Test that the CBC payload JSON contains 'iv', 'value', and 'cipher' keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        data = json.loads(base64.b64decode(enc.encrypt("keys check")).decode())
        for key in ("iv", "value", "cipher"):
            self.assertIn(key, data)

# ===========================================================================
# TestEncrypterRoundtripGCM
# ===========================================================================

class TestEncrypterRoundtripGCM(TestCase):

    def testRoundtripAes128Gcm(self) -> None:
        """
        Test that AES-128-GCM encrypt then decrypt yields the original plaintext.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        original = "Hello, AES-128-GCM!"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundtripAes256Gcm(self) -> None:
        """
        Test that AES-256-GCM encrypt then decrypt yields the original plaintext.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        original = "Hello, AES-256-GCM!"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testGcmEncryptReturnsDifferentPayloadOnEachCall(self) -> None:
        """
        Test that two encryptions of the same plaintext produce different ciphertexts
        in GCM mode (due to random nonce generation).

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        ct1 = enc.encrypt("same text")
        ct2 = enc.encrypt("same text")
        self.assertNotEqual(ct1, ct2)

    def testGcmEncryptedPayloadIsValidBase64(self) -> None:
        """
        Test that the encrypted payload returned by GCM mode is valid base64.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        payload = enc.encrypt("test gcm payload")
        decoded = base64.b64decode(payload)
        self.assertIsInstance(decoded, bytes)

    def testGcmEncryptedPayloadContainsCipherField(self) -> None:
        """
        Test that the decoded GCM payload JSON includes a 'cipher' field.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        data = json.loads(base64.b64decode(enc.encrypt("gcm cipher field")).decode())
        self.assertEqual(data["cipher"], "AES-128-GCM")

    def testGcmEncryptedPayloadContainsTagField(self) -> None:
        """
        Test that the decoded GCM payload JSON includes a non-null 'tag' field.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        data = json.loads(base64.b64decode(enc.encrypt("gcm tag check")).decode())
        self.assertIn("tag", data)
        self.assertIsNotNone(data["tag"])

    def testGcmRoundtripWithLongText(self) -> None:
        """
        Test GCM roundtrip with a long plaintext.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        original = "y" * 1000
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testGcmRoundtripWithSingleCharacter(self) -> None:
        """
        Test GCM roundtrip with a single-character plaintext.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        self.assertEqual(enc.decrypt(enc.encrypt("Z")), "Z")

    def testGcmRoundtripWithSpecialCharacters(self) -> None:
        """
        Test GCM roundtrip with special characters and unicode.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        original = "!@#$%^&*() áéíóú ñ 中文 🔒"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testGcmEncryptedPayloadHasIvValueTagCipherKeys(self) -> None:
        """
        Test that the GCM payload JSON contains 'iv', 'value', 'tag', and 'cipher' keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        data = json.loads(base64.b64decode(enc.encrypt("keys check gcm")).decode())
        for key in ("iv", "value", "tag", "cipher"):
            self.assertIn(key, data)

# ===========================================================================
# TestEncrypterEncryptReturnType
# ===========================================================================

class TestEncrypterEncryptReturnType(TestCase):

    def testEncryptAes128CbcReturnsString(self) -> None:
        """
        Test that encrypt() returns a string for AES-128-CBC.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        result = enc.encrypt("data")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def testEncryptAes256CbcReturnsString(self) -> None:
        """
        Test that encrypt() returns a string for AES-256-CBC.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        result = enc.encrypt("data")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def testEncryptAes128GcmReturnsString(self) -> None:
        """
        Test that encrypt() returns a string for AES-128-GCM.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        result = enc.encrypt("data")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def testEncryptAes256GcmReturnsString(self) -> None:
        """
        Test that encrypt() returns a string for AES-256-GCM.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        result = enc.encrypt("data")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
