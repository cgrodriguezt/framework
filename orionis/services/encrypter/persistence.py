from __future__ import annotations
import os
from pathlib import Path
from typing import Any
import dill
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.padding import PKCS7

class Persistence:

    def __init__(
        self,
        path: Path,
        filename: str,
        cipher: str,
        key: bytes | str,
        magic: bytes,
        salt: bytes,
        info: bytes,
    ) -> None:
        """
        Initialize Persistence object with encryption configuration.

        Parameters
        ----------
        path : Path
            Directory path where the encrypted file will be stored.
        filename : str
            Base filename without extension for the encrypted file.
        cipher : str
            Cipher algorithm identifier (e.g., 'AES128GCM', 'AES256GCM').
        key : bytes | str
            Master key material for cryptographic key derivation.
        magic : bytes
            Magic byte sequence for file format identification.
        salt : bytes
            Cryptographic salt for key derivation function.
        info : bytes
            Additional context information for HKDF key derivation.

        Returns
        -------
        None
            Constructor returns None implicitly.
        """
        # Initialize data storage for pending persistence operations
        self.__data = None

        # Cache magic bytes for file format validation
        self.__magic = magic

        # Create target directory structure and set file path
        path.mkdir(parents=True, exist_ok=True)
        self.__filepath = path / f"{filename}.bin"

        # Normalize key input to bytes format for cryptographic operations
        if isinstance(key, str):
            key = key.encode()

        # Calculate required key length based on cipher specification
        key_size = 16 if "128" in cipher else 32

        # Derive cryptographic key using HKDF for enhanced security
        self.__key = HKDF(
            algorithm=hashes.SHA256(),
            length=key_size,
            salt=salt,
            info=info,
            backend=default_backend(),
        ).derive(key)

        # Configure cipher backend based on algorithm type
        if cipher.endswith("GCM"):
            self.__aesgcm = AESGCM(self.__key)
            self.__use_gcm = True
        else:
            self.__aesgcm = None
            self.__use_gcm = False

    def data(self, data: Any) -> Persistence:
        """
        Set data object for subsequent persistence operations.

        Parameters
        ----------
        data : Any
            Object to be serialized and encrypted for storage.

        Returns
        -------
        Persistence
            Current instance enabling fluent method chaining.
        """
        # Cache data object for deferred encryption and storage
        self.__data = data
        return self

    def save(self) -> bool:
        """
        Persist cached data to encrypted file on disk.

        Serialize stored data object using dill and encrypt the resulting
        bytes using the configured cipher mode (GCM or CBC). Write the
        encrypted payload to the target file with magic header.

        Returns
        -------
        bool
            True if persistence operation succeeds, False on any error.
        """
        # Guard against empty data scenarios
        if not self.__data:
            return False

        try:

            # Serialize data using highest compression protocol available
            raw = dill.dumps(
                self.__data,
                protocol=dill.HIGHEST_PROTOCOL,
            )

            # Apply encryption based on configured cipher mode
            if self.__use_gcm:
                nonce = os.urandom(12)  # Generate secure 96-bit nonce
                encrypted = self.__aesgcm.encrypt(nonce, raw, self.__magic)
                payload = nonce + encrypted
            else:
                payload = self.__encryptCbc(raw)

            # Write magic header followed by encrypted payload
            with Path.open(self.__filepath, "wb") as f:
                f.write(self.__magic)
                f.write(payload)

            # Return success status
            return True

        except Exception:

            # Return failure status on any exception
            return False

    def get(self) -> Any | None:
        """
        Retrieve and decrypt persisted data from encrypted file.

        Read the target file, validate magic header for format integrity,
        decrypt the payload using appropriate cipher mode, and deserialize
        the resulting bytes back to the original data object.

        Returns
        -------
        Any | None
            Deserialized data object on success, None on failure or missing
            file.
        """
        try:

            # Open target file for binary reading
            with Path.open(self.__filepath, "rb") as f:

                # Verify file format using magic header validation
                if f.read(len(self.__magic)) != self.__magic:
                    return None

                # Decrypt payload based on configured cipher mode
                if self.__use_gcm:
                    nonce = f.read(12)  # Read 96-bit nonce
                    encrypted = f.read()
                    raw = self.__aesgcm.decrypt(nonce, encrypted, self.__magic)
                else:
                    # Use CBC mode decryption for non-GCM ciphers
                    encrypted = f.read()
                    raw = self.__decryptCbc(encrypted)

            # Deserialize bytes back to original data structure
            return dill.loads(raw)

        except FileNotFoundError:

            # Handle missing file scenario gracefully
            return None

        except Exception:

            # Handle any decryption or deserialization errors
            return None

    def __encryptCbc(self, raw: bytes) -> bytes:
        """
        Encrypt data using AES CBC mode with PKCS7 padding.

        Parameters
        ----------
        raw : bytes
            Plaintext bytes to be encrypted.

        Returns
        -------
        bytes
            Initialization vector concatenated with encrypted ciphertext.
        """
        # Generate cryptographically secure 128-bit initialization vector
        iv = os.urandom(16)

        # Apply PKCS7 padding to align data with AES block boundaries
        padder = PKCS7(128).padder()
        padded = padder.update(raw) + padder.finalize()

        # Initialize AES cipher in CBC mode with generated IV
        cipher = Cipher(
            algorithms.AES(self.__key),
            modes.CBC(iv),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()

        # Prepend IV to ciphertext for decryption recovery
        return iv + encrypted

    def __decryptCbc(self, data: bytes) -> bytes:
        """
        Decrypt data using AES CBC mode with PKCS7 unpadding.

        Parameters
        ----------
        data : bytes
            Encrypted ciphertext with prepended initialization vector.

        Returns
        -------
        bytes
            Decrypted plaintext with padding removed.
        """
        # Split input into IV and ciphertext components
        iv = data[:16]
        encrypted = data[16:]

        # Initialize AES cipher in CBC mode for decryption
        cipher = Cipher(
            algorithms.AES(self.__key),
            modes.CBC(iv),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        padded = decryptor.update(encrypted) + decryptor.finalize()

        # Remove PKCS7 padding to restore original data length
        unpadder = PKCS7(128).unpadder()
        return unpadder.update(padded) + unpadder.finalize()
