from __future__ import annotations
import base64
from orionis.test import TestCase
from orionis.foundation.config.app.enums.ciphers import Cipher
from orionis.services.environment.key.key_generator import SecureKeyGenerator

# ---------------------------------------------------------------------------
# TestSecureKeyGeneratorKeySizes
# ---------------------------------------------------------------------------

class TestSecureKeyGeneratorKeySizes(TestCase):

    def testKeySizesContainsAllCiphers(self):
        """
        Confirm that KEY_SIZES maps every supported Cipher member.

        Ensures the class-level mapping is complete so that all Cipher
        variants yield a valid key length at generation time.
        """
        for cipher in Cipher:
            self.assertIn(cipher, SecureKeyGenerator.KEY_SIZES)

    def testAes128CbcKeySize(self):
        """
        Verify that AES-128-CBC maps to a 16-byte key size.

        Validates that the stored key length matches the AES-128 standard.
        """
        self.assertEqual(SecureKeyGenerator.KEY_SIZES[Cipher.AES_128_CBC], 16)

    def testAes256CbcKeySize(self):
        """
        Verify that AES-256-CBC maps to a 32-byte key size.

        Validates that the stored key length matches the AES-256 standard.
        """
        self.assertEqual(SecureKeyGenerator.KEY_SIZES[Cipher.AES_256_CBC], 32)

    def testAes128GcmKeySize(self):
        """
        Verify that AES-128-GCM maps to a 16-byte key size.

        Validates that the stored key length matches the AES-128 GCM standard.
        """
        self.assertEqual(SecureKeyGenerator.KEY_SIZES[Cipher.AES_128_GCM], 16)

    def testAes256GcmKeySize(self):
        """
        Verify that AES-256-GCM maps to a 32-byte key size.

        Validates that the stored key length matches the AES-256 GCM standard.
        """
        self.assertEqual(SecureKeyGenerator.KEY_SIZES[Cipher.AES_256_GCM], 32)

# ---------------------------------------------------------------------------
# TestSecureKeyGeneratorOutputFormat
# ---------------------------------------------------------------------------

class TestSecureKeyGeneratorOutputFormat(TestCase):

    def testDefaultGenerateReturnsString(self):
        """
        Confirm that generate() returns a string with the default cipher.

        Validates the return type contract for the most common usage path.
        """
        result = SecureKeyGenerator.generate()
        self.assertIsInstance(result, str)

    def testDefaultGenerateStartsWithBase64Prefix(self):
        """
        Confirm that the generated key starts with 'base64:'.

        Ensures the output format is compatible with the Laravel APP_KEY
        convention used by the framework.
        """
        result = SecureKeyGenerator.generate()
        self.assertTrue(result.startswith("base64:"))

    def testDefaultGenerateContainsSingleColon(self):
        """
        Verify that the generated key contains exactly one colon delimiter.

        Confirms the 'base64:<encoded>' format is strict and does not embed
        extra colons in the Base64 payload.
        """
        result = SecureKeyGenerator.generate()
        self.assertEqual(result.count(":"), 1)

    def testDefaultGeneratePayloadIsValidBase64(self):
        """
        Confirm that the portion after 'base64:' is valid Base64-encoded data.

        Validates that the encoded payload can be decoded without errors,
        proving the key is correctly formatted.
        """
        result = SecureKeyGenerator.generate()
        encoded = result.split(":", 1)[1]
        try:
            base64.b64decode(encoded, validate=True)
        except Exception as exc:
            self.fail(f"Payload is not valid Base64: {exc}")

# ---------------------------------------------------------------------------
# TestSecureKeyGeneratorKeyLength
# ---------------------------------------------------------------------------

class TestSecureKeyGeneratorKeyLength(TestCase):

    def testAes256CbcProduces32ByteKey(self):
        """
        Verify that AES-256-CBC generates a 32-byte decoded key.

        Decodes the Base64 payload and confirms the raw entropy length
        matches the expected 32 bytes for AES-256.
        """
        result = SecureKeyGenerator.generate(Cipher.AES_256_CBC)
        decoded = base64.b64decode(result.split(":", 1)[1])
        self.assertEqual(len(decoded), 32)

    def testAes128CbcProduces16ByteKey(self):
        """
        Verify that AES-128-CBC generates a 16-byte decoded key.

        Decodes the Base64 payload and confirms the raw entropy length
        matches the expected 16 bytes for AES-128.
        """
        result = SecureKeyGenerator.generate(Cipher.AES_128_CBC)
        decoded = base64.b64decode(result.split(":", 1)[1])
        self.assertEqual(len(decoded), 16)

    def testAes256GcmProduces32ByteKey(self):
        """
        Verify that AES-256-GCM generates a 32-byte decoded key.

        Decodes the Base64 payload and confirms the raw entropy length
        matches the expected 32 bytes for AES-256 in GCM mode.
        """
        result = SecureKeyGenerator.generate(Cipher.AES_256_GCM)
        decoded = base64.b64decode(result.split(":", 1)[1])
        self.assertEqual(len(decoded), 32)

    def testAes128GcmProduces16ByteKey(self):
        """
        Verify that AES-128-GCM generates a 16-byte decoded key.

        Decodes the Base64 payload and confirms the raw entropy length
        matches the expected 16 bytes for AES-128 in GCM mode.
        """
        result = SecureKeyGenerator.generate(Cipher.AES_128_GCM)
        decoded = base64.b64decode(result.split(":", 1)[1])
        self.assertEqual(len(decoded), 16)

# ---------------------------------------------------------------------------
# TestSecureKeyGeneratorStringInput
# ---------------------------------------------------------------------------

class TestSecureKeyGeneratorStringInput(TestCase):

    def testGenerateWithStringAes256Cbc(self):
        """
        Accept the string 'AES-256-CBC' and generate a valid 32-byte key.

        Confirms that string cipher inputs are converted to Cipher enums
        before key generation without raising any error.
        """
        result = SecureKeyGenerator.generate("AES-256-CBC")
        decoded = base64.b64decode(result.split(":", 1)[1])
        self.assertEqual(len(decoded), 32)

    def testGenerateWithStringAes128Cbc(self):
        """
        Accept the string 'AES-128-CBC' and generate a valid 16-byte key.

        Confirms that string conversion for CBC-128 mode works correctly.
        """
        result = SecureKeyGenerator.generate("AES-128-CBC")
        decoded = base64.b64decode(result.split(":", 1)[1])
        self.assertEqual(len(decoded), 16)

    def testGenerateWithStringAes256Gcm(self):
        """
        Accept the string 'AES-256-GCM' and generate a valid 32-byte key.

        Confirms that string conversion for GCM-256 mode works correctly.
        """
        result = SecureKeyGenerator.generate("AES-256-GCM")
        decoded = base64.b64decode(result.split(":", 1)[1])
        self.assertEqual(len(decoded), 32)

    def testGenerateWithStringAes128Gcm(self):
        """
        Accept the string 'AES-128-GCM' and generate a valid 16-byte key.

        Confirms that string conversion for GCM-128 mode works correctly.
        """
        result = SecureKeyGenerator.generate("AES-128-GCM")
        decoded = base64.b64decode(result.split(":", 1)[1])
        self.assertEqual(len(decoded), 16)

    def testGenerateWithInvalidStringRaisesValueError(self):
        """
        Raise ValueError when an unsupported cipher string is provided.

        Validates that the string-to-enum conversion raises ValueError
        for unrecognized cipher names, preventing silent fallbacks.
        """
        with self.assertRaises(ValueError):
            SecureKeyGenerator.generate("AES-512-CBC")

    def testErrorMessageContainsCipherName(self):
        """
        Include the invalid cipher name in the ValueError message.

        Ensures the error message is informative enough for the caller to
        identify which cipher string caused the failure.
        """
        invalid = "INVALID-CIPHER"
        try:
            SecureKeyGenerator.generate(invalid)
            self.fail("Expected ValueError was not raised")
        except ValueError as exc:
            self.assertIn(invalid, str(exc))

    def testErrorMessageContainsValidOptions(self):
        """
        Include at least one valid option in the ValueError message.

        Confirms that the error message guides the caller toward a
        supported cipher rather than providing no context.
        """
        try:
            SecureKeyGenerator.generate("BAD")
        except ValueError as exc:
            self.assertIn("AES-256-CBC", str(exc))

    def testLowercaseCipherStringRaisesError(self):
        """
        Raise ValueError when a lowercase cipher string is provided.

        Validates that cipher string matching is case-sensitive, since Cipher
        enum values are defined in uppercase format.
        """
        with self.assertRaises(ValueError):
            SecureKeyGenerator.generate("aes-256-cbc")

# ---------------------------------------------------------------------------
# TestSecureKeyGeneratorRandomness
# ---------------------------------------------------------------------------

class TestSecureKeyGeneratorRandomness(TestCase):

    def testSuccessiveCallsProduceDifferentKeys(self):
        """
        Verify that two consecutive generate() calls return different keys.

        Confirms that each invocation uses fresh entropy from os.urandom
        rather than reusing a cached or static value.
        """
        key_a = SecureKeyGenerator.generate()
        key_b = SecureKeyGenerator.generate()
        self.assertNotEqual(key_a, key_b)

    def testLargeSetOfKeysAreUnique(self):
        """
        Verify that a batch of fifty generated keys contains no duplicates.

        Provides a statistical confidence check for the randomness of the
        underlying os.urandom source.
        """
        keys = {SecureKeyGenerator.generate() for _ in range(50)}
        self.assertEqual(len(keys), 50)
