from __future__ import annotations
import base64
import json
import os
from typing import TYPE_CHECKING, ClassVar
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from orionis.foundation.config.app.enums.ciphers import Cipher as OrionisCipher
from orionis.services.encrypter.contracts.encrypter import IEncrypter

if TYPE_CHECKING:
    from orionis.foundation.contracts.application import IApplication

class Encrypter(IEncrypter):

    AES_128_KEY_SIZE = 16
    AES_256_KEY_SIZE = 32
    CBC_IV_SIZE = 16
    GCM_IV_SIZE = 12
    GCM_TAG_SIZE = 16
    PKCS7_BLOCK_SIZE = 16
    SUPPORTED_CIPHERS: ClassVar[list[str]] = [cipher.value for cipher in OrionisCipher]

    def __init__(
        self,
        app: IApplication,
    ) -> None:
        """Initialize the encrypter with application configuration.

        Parameters
        ----------
        app : IApplication
            The application instance providing configuration access.

        Returns
        -------
        None
            This method initializes the instance and returns None.

        Raises
        ------
        ValueError
            If the cipher is not supported or key length is invalid.
        """
        # Get configuration values from application
        self.key: bytes = app.config("app.key")
        self.cipher: str = app.config("app.cipher")

        # Validate cipher is supported
        if self.cipher not in self.SUPPORTED_CIPHERS:
            error_msg = (
                f"Cipher '{self.cipher}' not supported. "
                f"Use one of: {self.SUPPORTED_CIPHERS}"
            )
            raise ValueError(error_msg)

        # Validate key length according to cipher requirements
        key_len = len(self.key)
        if self.cipher.startswith("AES-128") and key_len != self.AES_128_KEY_SIZE:
            error_msg = f"Key must be {self.AES_128_KEY_SIZE} bytes for AES-128"
            raise ValueError(error_msg)
        if self.cipher.startswith("AES-256") and key_len != self.AES_256_KEY_SIZE:
            error_msg = f"Key must be {self.AES_256_KEY_SIZE} bytes for AES-256"
            raise ValueError(error_msg)

    def encrypt(
        self,
        plaintext: str,
    ) -> str:
        """Encrypt plaintext using the configured cipher algorithm.

        Parameters
        ----------
        plaintext : str
            The text to encrypt.

        Returns
        -------
        str
            Base64-encoded encrypted payload containing IV, value, tag, and cipher.

        Raises
        ------
        TypeError
            If plaintext is not a string.
        ValueError
            If plaintext is empty or has encoding issues.
        EncryptionError
            If encryption fails.
        """
        if not isinstance(plaintext, str):
            error_msg = "Plaintext must be a string"
            raise TypeError(error_msg)

        if not plaintext:
            error_msg = "Plaintext cannot be empty"
            raise ValueError(error_msg)

        try:
            # Convert plaintext to UTF-8 bytes for encryption
            data = plaintext.encode("utf-8")
        except UnicodeEncodeError as e:
            error_msg = f"UTF-8 encoding error: {e}"
            raise ValueError(error_msg) from e

        try:
            # Choose encryption method based on cipher mode
            if "GCM" in self.cipher:
                return self.__encryptGCM(data)
            return self.__encryptCBC(data)
        except Exception as e:
            error_msg = f"Error during encryption: {e}"
            raise RuntimeError(error_msg) from e

    def decrypt(
        self,
        payload: str,
    ) -> str:
        """Decrypt an encrypted payload using the configured cipher algorithm.

        Parameters
        ----------
        payload : str
            Base64-encoded encrypted payload containing IV, value, tag, and cipher.

        Returns
        -------
        str
            The decrypted plaintext as a UTF-8 string.

        Raises
        ------
        TypeError
            If payload is not a string.
        ValueError
            If payload is empty or invalid.
        DecryptionError
            If decryption fails.
        """
        if not isinstance(payload, str):
            error_msg = "Payload must be a string"
            raise TypeError(error_msg)

        if not payload:
            error_msg = "Payload cannot be empty"
            raise ValueError(error_msg)

        # Decode and validate the payload structure
        data = self.__decodePayload(payload)
        cipher, iv, value, tag = self.__extractPayloadData(data)

        # Validate cipher compatibility and IV size
        self.__validateCipherMatch(cipher)
        self.__validateIvSize(cipher, iv)

        # Perform the actual decryption
        return self.__performDecryption(cipher, value, iv, tag)

    def __decodePayload(
        self,
        payload: str,
    ) -> dict:
        """Decode base64 payload and convert to JSON dictionary.

        Parameters
        ----------
        payload : str
            Base64-encoded JSON payload string to decode.

        Returns
        -------
        dict
            Decoded JSON data as dictionary.

        Raises
        ------
        ValueError
            If payload cannot be decoded or parsed as JSON.
        """
        try:
            # Decode base64 and convert bytes to UTF-8 string
            decoded = base64.b64decode(payload).decode("utf-8")
            # Parse JSON string into dictionary
            return json.loads(decoded)
        except (json.JSONDecodeError, base64.binascii.Error) as e:
            # Raise error if decoding or parsing fails
            error_msg = f"Invalid payload: {e}"
            raise ValueError(error_msg) from e

    def __extractPayloadData(
        self,
        data: dict,
    ) -> tuple[str, bytes, bytes, bytes | None]:
        """Extract and validate payload data fields.

        Parameters
        ----------
        data : dict
            Dictionary containing encrypted payload fields.

        Returns
        -------
        tuple[str, bytes, bytes, bytes | None]
            Tuple containing (cipher, iv, value, tag) where tag may be None.

        Raises
        ------
        ValueError
            If required fields are missing or base64 decoding fails.
        """
        # Check for required fields in payload
        required_fields = ["iv", "value", "cipher"]
        for field in required_fields:
            if field not in data:
                error_msg = f"Required field '{field}' not found in payload"
                raise ValueError(error_msg)

        try:
            # Extract cipher name
            cipher = data["cipher"]
            # Decode base64 encoded fields
            iv = base64.b64decode(data["iv"])
            value = base64.b64decode(data["value"])
            # Tag is optional, decode only if present
            tag = base64.b64decode(data["tag"]) if data.get("tag") else None
            return cipher, iv, value, tag
        except base64.binascii.Error as e:
            error_msg = f"Error decoding payload data: {e}"
            raise ValueError(error_msg) from e

    def __validateCipherMatch(
        self,
        cipher: str,
    ) -> None:
        """Validate that payload cipher matches the configured cipher.

        Parameters
        ----------
        cipher : str
            The cipher algorithm name from the payload.

        Returns
        -------
        None
            This method validates compatibility and returns None.

        Raises
        ------
        ValueError
            If the payload cipher does not match the configured cipher.
        """
        # Check cipher compatibility between payload and configuration
        if cipher != self.cipher:
            error_msg = (
                f"Payload cipher '{cipher}' does not match "
                f"configured cipher '{self.cipher}'"
            )
            raise ValueError(error_msg)

    def __validateIvSize(
        self,
        cipher: str,
        iv: bytes,
    ) -> None:
        """Validate that the IV size matches the cipher requirements.

        Parameters
        ----------
        cipher : str
            The cipher algorithm name to validate against.
        iv : bytes
            The initialization vector bytes to validate.

        Returns
        -------
        None
            This method validates IV size and returns None.

        Raises
        ------
        ValueError
            If IV size does not match the cipher requirements.
        """
        # Check IV size for GCM mode ciphers
        if "GCM" in cipher and len(iv) != self.GCM_IV_SIZE:
            error_msg = (
                f"Invalid IV for GCM: expected {self.GCM_IV_SIZE} bytes, "
                f"received {len(iv)}"
            )
            raise ValueError(error_msg)

        # Check IV size for CBC mode ciphers
        if "CBC" in cipher and len(iv) != self.CBC_IV_SIZE:
            error_msg = (
                f"Invalid IV for CBC: expected {self.CBC_IV_SIZE} bytes, "
                f"received {len(iv)}"
            )
            raise ValueError(error_msg)

    def __performDecryption(
        self,
        cipher: str,
        value: bytes,
        iv: bytes,
        tag: bytes | None,
    ) -> str:
        """Perform decryption based on the cipher mode.

        Parameters
        ----------
        cipher : str
            The cipher algorithm name specifying the mode.
        value : bytes
            The encrypted data to decrypt.
        iv : bytes
            The initialization vector used during encryption.
        tag : bytes | None
            The authentication tag for GCM mode, None for CBC mode.

        Returns
        -------
        str
            The decrypted plaintext as a UTF-8 string.

        Raises
        ------
        ValueError
            If tag requirements are not met for GCM mode.
        RuntimeError
            If decryption fails for any reason.
        """
        try:

            # Handle GCM mode decryption with tag validation
            if "GCM" in cipher:
                if tag is None:
                    error_msg = "Tag required for GCM mode"
                    raise ValueError(error_msg)
                if len(tag) != self.GCM_TAG_SIZE:
                    error_msg = (
                        f"Invalid tag: expected {self.GCM_TAG_SIZE} bytes, "
                        f"received {len(tag)}"
                    )
                    raise ValueError(error_msg)
                return self.__decryptGCM(value, iv, tag).decode("utf-8")

            # Handle CBC mode decryption
            return self.__decryptCBC(value, iv).decode("utf-8")

        except Exception as e:

            error_msg = f"Error during decryption: {e}"
            raise RuntimeError(error_msg) from e

    def __encryptCBC(
        self,
        data: bytes,
    ) -> str:
        """Encrypt data using AES-CBC with PKCS7 padding.

        Parameters
        ----------
        data : bytes
            The raw data to encrypt.

        Returns
        -------
        str
            Base64-encoded JSON payload containing IV, encrypted value, and cipher.

        Raises
        ------
        RuntimeError
            If CBC encryption fails.
        """
        try:

            # Generate random IV for CBC mode
            iv = os.urandom(self.CBC_IV_SIZE)
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=default_backend(),
            )
            encryptor = cipher.encryptor()

            # Apply PKCS7 padding to align data to block size
            pad_len = self.PKCS7_BLOCK_SIZE - (len(data) % self.PKCS7_BLOCK_SIZE)
            data += bytes([pad_len]) * pad_len

            # Perform encryption
            ct = encryptor.update(data) + encryptor.finalize()

            # Build payload with encrypted data
            payload = {
                "iv": base64.b64encode(iv).decode(),
                "value": base64.b64encode(ct).decode(),
                "tag": None,
                "cipher": self.cipher,
            }

            # Return base64-encoded JSON payload
            return base64.b64encode(json.dumps(payload).encode("utf-8")).decode()

        except Exception as e:

            # Raise error if encryption fails
            error_msg = f"Error en encriptación CBC: {e}"
            raise RuntimeError(error_msg) from e

    def __decryptCBC(
        self,
        ct: bytes,
        iv: bytes,
    ) -> bytes:
        """Decrypt CBC-encrypted data and remove PKCS7 padding.

        Parameters
        ----------
        ct : bytes
            The encrypted ciphertext to decrypt.
        iv : bytes
            The initialization vector used during encryption.

        Returns
        -------
        bytes
            The decrypted plaintext with padding removed.

        Raises
        ------
        ValueError
            If decrypted data is empty or padding is invalid.
        RuntimeError
            If CBC decryption fails.
        """
        try:

            # Create cipher instance and decryptor for CBC mode
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()

            # Perform decryption
            data = decryptor.update(ct) + decryptor.finalize()

            # Validate decrypted data is not empty
            if len(data) == 0:
                error_msg = "Decrypted data is empty"
                raise ValueError(error_msg)

            # Extract padding length from last byte
            pad_len = data[-1]

            # Validate padding length is within acceptable range
            if pad_len == 0 or pad_len > self.PKCS7_BLOCK_SIZE:
                error_msg = f"Invalid PKCS7 padding length: {pad_len}"
                raise ValueError(error_msg)

            # Verify padding bytes are consistent
            for i in range(pad_len):
                if data[-(i+1)] != pad_len:
                    error_msg = "Corrupted PKCS7 padding"
                    raise ValueError(error_msg)

            # Return data with padding removed
            return data[:-pad_len]

        except ValueError:

            # Re-raise ValueErrors for padding issues
            raise
        except Exception as e:

            # Raise error if decryption fails
            error_msg = f"Error in CBC decryption: {e}"
            raise RuntimeError(error_msg) from e

    def __encryptGCM(
        self,
        data: bytes,
    ) -> str:
        """Encrypt data using AES-GCM mode with authentication.

        Parameters
        ----------
        data : bytes
            The raw data to encrypt.

        Returns
        -------
        str
            Base64-encoded JSON payload containing IV, encrypted value, tag, and cipher.

        Raises
        ------
        RuntimeError
            If GCM encryption fails.
        """
        try:

            # Generate random IV for GCM mode
            iv = os.urandom(self.GCM_IV_SIZE)
            aesgcm = AESGCM(self.key)
            ct = aesgcm.encrypt(iv, data, None)

            # Separate ciphertext and tag (last bytes according to GCM_TAG_SIZE)
            value, tag = ct[:-self.GCM_TAG_SIZE], ct[-self.GCM_TAG_SIZE:]

            # Build payload with encrypted data and authentication tag
            payload = {
                "iv": base64.b64encode(iv).decode(),
                "value": base64.b64encode(value).decode(),
                "tag": base64.b64encode(tag).decode(),
                "cipher": self.cipher,
            }

            # Return base64-encoded JSON payload
            return base64.b64encode(json.dumps(payload).encode("utf-8")).decode()

        except Exception as e:

            # Raise error if encryption fails
            error_msg = f"Error in GCM encryption: {e}"
            raise RuntimeError(error_msg) from e

    def __decryptGCM(
        self,
        value: bytes,
        iv: bytes,
        tag: bytes | None,
    ) -> bytes:
        """Decrypt GCM-encrypted data using AESGCM with authentication tag.

        Parameters
        ----------
        value : bytes
            The encrypted ciphertext to decrypt.
        iv : bytes
            The initialization vector used during encryption.
        tag : bytes | None
            The authentication tag for GCM mode verification.

        Returns
        -------
        bytes
            The decrypted plaintext as raw bytes.

        Raises
        ------
        ValueError
            If tag is None or GCM verification fails.
        RuntimeError
            If GCM decryption fails for any other reason.
        """
        try:

            # Validate authentication tag is provided
            if tag is None:
                error_msg = "Tag required for GCM decryption"
                raise ValueError(error_msg)

            # Create AESGCM instance and decrypt with tag verification
            aesgcm = AESGCM(self.key)
            return aesgcm.decrypt(iv, value + tag, None)

        except ValueError:

            # Re-raise ValueError for tag validation issues
            raise
        except Exception as e:

            # Raise error if decryption fails
            error_msg = f"Error in GCM decryption: {e}"
            raise RuntimeError(error_msg) from e
