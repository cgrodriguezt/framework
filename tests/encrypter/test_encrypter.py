from __future__ import annotations
import base64
import json
from orionis.encrypter.contracts.encrypter import IEncrypter
from orionis.encrypter.encrypter import Encrypter
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Fixed keys — deterministic, never change between test runs
# ---------------------------------------------------------------------------

# 16-byte key for all AES-128 cipher variants
_KEY_16: bytes = b"\x4b" * 16
# 32-byte key for all AES-256 cipher variants
_KEY_32: bytes = b"\x9f" * 32

# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

class _FakeApp:
    """Minimal application stub providing cipher configuration for tests."""

    def __init__(self, key: bytes, cipher: str) -> None:
        self._key = key
        self._cipher = cipher

    def config(self, path: str) -> object:
        """Return configuration value for the given path."""
        if path == "app.key":
            return self._key
        if path == "app.cipher":
            return self._cipher
        return None

def _make(cipher: str) -> Encrypter:
    """Create an Encrypter pre-configured for the given cipher name."""
    key = _KEY_16 if cipher.startswith("AES-128") else _KEY_32
    return Encrypter(_FakeApp(key, cipher))

# ===========================================================================
# Constants
# ===========================================================================

class TestEncrypterConstants(TestCase):

    def testAes128KeySizeIs16(self) -> None:
        """
        Verify AES_128_KEY_SIZE constant equals 16.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Encrypter.AES_128_KEY_SIZE, 16)

    def testAes256KeySizeIs32(self) -> None:
        """
        Verify AES_256_KEY_SIZE constant equals 32.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Encrypter.AES_256_KEY_SIZE, 32)

    def testCbcIvSizeIs16(self) -> None:
        """
        Verify CBC_IV_SIZE constant equals 16.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Encrypter.CBC_IV_SIZE, 16)

    def testGcmIvSizeIs12(self) -> None:
        """
        Verify GCM_IV_SIZE constant equals 12.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Encrypter.GCM_IV_SIZE, 12)

    def testGcmTagSizeIs16(self) -> None:
        """
        Verify GCM_TAG_SIZE constant equals 16.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Encrypter.GCM_TAG_SIZE, 16)

    def testPkcs7BlockSizeIs16(self) -> None:
        """
        Verify PKCS7_BLOCK_SIZE constant equals 16.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Encrypter.PKCS7_BLOCK_SIZE, 16)

    def testSupportedCiphersContainsAllFourModes(self) -> None:
        """
        Verify SUPPORTED_CIPHERS contains all four expected cipher names.

        Returns
        -------
        None
            This method does not return a value.
        """
        expected = frozenset({
            "AES-128-CBC", "AES-256-CBC",
            "AES-128-GCM", "AES-256-GCM",
        })
        self.assertEqual(Encrypter.SUPPORTED_CIPHERS, expected)

    def testSupportedCiphersIsFrozenSet(self) -> None:
        """
        Verify SUPPORTED_CIPHERS is a frozenset instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Encrypter.SUPPORTED_CIPHERS, frozenset)

# ===========================================================================
# __init__
# ===========================================================================

class TestEncrypterInit(TestCase):

    def testInitAes128CbcSucceeds(self) -> None:
        """
        Initialize Encrypter with a valid AES-128-CBC cipher and 16-byte key.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        self.assertEqual(enc.cipher, "AES-128-CBC")
        self.assertEqual(enc.key, _KEY_16)

    def testInitAes256CbcSucceeds(self) -> None:
        """
        Initialize Encrypter with a valid AES-256-CBC cipher and 32-byte key.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        self.assertEqual(enc.cipher, "AES-256-CBC")
        self.assertEqual(enc.key, _KEY_32)

    def testInitAes128GcmSucceeds(self) -> None:
        """
        Initialize Encrypter with a valid AES-128-GCM cipher and 16-byte key.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        self.assertEqual(enc.cipher, "AES-128-GCM")
        self.assertTrue(enc._is_gcm)

    def testInitAes256GcmSucceeds(self) -> None:
        """
        Initialize Encrypter with a valid AES-256-GCM cipher and 32-byte key.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        self.assertEqual(enc.cipher, "AES-256-GCM")
        self.assertTrue(enc._is_gcm)

    def testInitUnsupportedCipherRaisesValueError(self) -> None:
        """
        Raise ValueError when an unsupported cipher name is provided.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Encrypter(_FakeApp(_KEY_16, "AES-128-XTS"))

    def testInitShortKeyForAes128RaisesValueError(self) -> None:
        """
        Raise ValueError when the key is shorter than AES-128 requires.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Encrypter(_FakeApp(b"tooshort", "AES-128-CBC"))

    def testInitLongKeyForAes128RaisesValueError(self) -> None:
        """
        Raise ValueError when the key is longer than AES-128 requires.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Encrypter(_FakeApp(_KEY_32, "AES-128-CBC"))

    def testInitShortKeyForAes256RaisesValueError(self) -> None:
        """
        Raise ValueError when the key is shorter than AES-256 requires.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Encrypter(_FakeApp(_KEY_16, "AES-256-CBC"))

    def testInitCbcSetsIsGcmFalseAndAesgcmNone(self) -> None:
        """
        Verify CBC mode sets _is_gcm to False and _aesgcm to None.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        self.assertFalse(enc._is_gcm)
        self.assertIsNone(enc._aesgcm)

    def testInitGcmSetsIsGcmTrueAndAesgcmNotNone(self) -> None:
        """
        Verify GCM mode sets _is_gcm to True and creates an AESGCM instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        self.assertTrue(enc._is_gcm)
        self.assertIsNotNone(enc._aesgcm)

    def testInitEncrypterImplementsIEncrypter(self) -> None:
        """
        Verify Encrypter satisfies the IEncrypter contract.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        self.assertIsInstance(enc, IEncrypter)

# ===========================================================================
# encrypt()  # noqa: ERA001
# ===========================================================================

class TestEncrypterEncrypt(TestCase):

    def testEncryptNonStringRaisesTypeError(self) -> None:
        """
        Raise TypeError when encrypt receives a non-string argument.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        with self.assertRaises(TypeError):
            enc.encrypt(123)  # type: ignore[arg-type]

    def testEncryptNoneRaisesTypeError(self) -> None:
        """
        Raise TypeError when encrypt receives None.

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
        Raise ValueError when encrypt receives an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        with self.assertRaises(ValueError):
            enc.encrypt("")

    def testEncryptCbcReturnsString(self) -> None:
        """
        Return a non-empty string payload when encrypting with CBC mode.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        result = enc.encrypt("hello world")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def testEncryptGcmReturnsString(self) -> None:
        """
        Return a non-empty string payload when encrypting with GCM mode.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        result = enc.encrypt("hello world")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def testEncryptOutputIsDecodableBase64(self) -> None:
        """
        Verify the encrypted output is valid base64-encoded data.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        result = enc.encrypt("base64-test")
        decoded = base64.b64decode(result)
        self.assertIsInstance(decoded, bytes)

    def testEncryptPayloadContainsRequiredFields(self) -> None:
        """
        Verify the payload JSON contains iv, value, tag, and cipher fields.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        raw = enc.encrypt("fields-test")
        data = json.loads(base64.b64decode(raw))
        self.assertIn("iv", data)
        self.assertIn("value", data)
        self.assertIn("tag", data)
        self.assertIn("cipher", data)

    def testEncryptPayloadCipherMatchesConfiguredCipher(self) -> None:
        """
        Verify the cipher field in the payload matches the configured cipher.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        raw = enc.encrypt("cipher-field-test")
        data = json.loads(base64.b64decode(raw))
        self.assertEqual(data["cipher"], "AES-128-GCM")

    def testEncryptGcmTagFieldIsNotNull(self) -> None:
        """
        Verify the tag field is non-null in a GCM-encrypted payload.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        raw = enc.encrypt("gcm-tag-test")
        data = json.loads(base64.b64decode(raw))
        self.assertIsNotNone(data["tag"])

    def testEncryptCbcTagFieldIsNull(self) -> None:
        """
        Verify the tag field is null in a CBC-encrypted payload.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        raw = enc.encrypt("cbc-null-tag-test")
        data = json.loads(base64.b64decode(raw))
        self.assertIsNone(data["tag"])

    def testEncryptYieldsDifferentOutputOnRepeatedCalls(self) -> None:
        """
        Verify repeated encryptions of the same text produce different payloads.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        p1 = enc.encrypt("same-text")
        p2 = enc.encrypt("same-text")
        self.assertNotEqual(p1, p2)

# ===========================================================================
# decrypt()  # noqa: ERA001
# ===========================================================================

class TestEncrypterDecrypt(TestCase):

    def testDecryptNonStringRaisesTypeError(self) -> None:
        """
        Raise TypeError when decrypt receives a non-string argument.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        with self.assertRaises(TypeError):
            enc.decrypt(42)  # type: ignore[arg-type]

    def testDecryptNoneRaisesTypeError(self) -> None:
        """
        Raise TypeError when decrypt receives None.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        with self.assertRaises(TypeError):
            enc.decrypt(None)  # type: ignore[arg-type]

    def testDecryptEmptyStringRaisesValueError(self) -> None:
        """
        Raise ValueError when decrypt receives an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        with self.assertRaises(ValueError):
            enc.decrypt("")

    def testDecryptInvalidBase64RaisesValueError(self) -> None:
        """
        Raise ValueError when decrypt receives an invalid base64 string.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        with self.assertRaises(ValueError):
            enc.decrypt("!!!not-valid-base64!!!")

    def testDecryptBase64EncodedNonJsonRaisesValueError(self) -> None:
        """
        Raise ValueError when the base64 payload does not decode to valid JSON.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        payload = base64.b64encode(b"this-is-not-json").decode()
        with self.assertRaises(ValueError):
            enc.decrypt(payload)

    def testDecryptCipherMismatchRaisesValueError(self) -> None:
        """
        Raise ValueError when the payload cipher does not match the configured one.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc_a = _make("AES-128-CBC")
        enc_b = _make("AES-256-CBC")
        payload = enc_a.encrypt("mismatch-test")
        with self.assertRaises(ValueError):
            enc_b.decrypt(payload)

    def testDecryptCbcWithGcmPayloadRaisesValueError(self) -> None:
        """
        Raise ValueError when decrypting a GCM payload with a CBC encrypter.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc_gcm = _make("AES-128-GCM")
        enc_cbc = _make("AES-128-CBC")
        payload = enc_gcm.encrypt("cross-mode-test")
        with self.assertRaises(ValueError):
            enc_cbc.decrypt(payload)

# ===========================================================================
# Round-trip (encrypt → decrypt)
# ===========================================================================

class TestEncrypterRoundTrip(TestCase):

    def testRoundTripAes128Cbc(self) -> None:
        """
        Recover original plaintext after AES-128-CBC encrypt and decrypt.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        original = "round-trip-cbc-128"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripAes256Cbc(self) -> None:
        """
        Recover original plaintext after AES-256-CBC encrypt and decrypt.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        original = "round-trip-cbc-256"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripAes128Gcm(self) -> None:
        """
        Recover original plaintext after AES-128-GCM encrypt and decrypt.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        original = "round-trip-gcm-128"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripAes256Gcm(self) -> None:
        """
        Recover original plaintext after AES-256-GCM encrypt and decrypt.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        original = "round-trip-gcm-256"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripSingleCharacter(self) -> None:
        """
        Recover a single-character string after a full encrypt-decrypt cycle.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        original = "x"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripExactBlockBoundary(self) -> None:
        """
        Recover plaintext of exactly 16 bytes (one PKCS7 block) after a round trip.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        original = "a" * 16
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripMultipleBlocks(self) -> None:
        """
        Recover a plaintext spanning several encryption blocks after a round trip.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        original = "b" * 64
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripLongString(self) -> None:
        """
        Recover a long plaintext string intact after a full round trip.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        original = "z" * 4096
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripSpecialCharacters(self) -> None:
        """
        Recover plaintext with special ASCII characters after a round trip.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-CBC")
        original = r"!@#$%^&*()_+-=[]{}|;':\",./<>?"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripUnicodeCharacters(self) -> None:
        """
        Recover plaintext containing multibyte Unicode characters after a round trip.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-256-GCM")
        original = "こんにちは 你好 مرحبا"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripNewlinesAndTabs(self) -> None:
        """
        Recover plaintext containing newline and tab characters after a round trip.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-CBC")
        original = "line1\nline2\ttabbed"
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)

    def testRoundTripJsonString(self) -> None:
        """
        Recover a JSON-formatted string intact after a full round trip.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _make("AES-128-GCM")
        original = '{"key": "value", "num": 42}'
        self.assertEqual(enc.decrypt(enc.encrypt(original)), original)
