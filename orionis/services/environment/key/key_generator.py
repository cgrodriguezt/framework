import os
import base64

class SecureKeyGenerator:
    """
    Provides static methods for generating secure random keys in base64 format.

    Methods
    -------
    generate_key() : str
        Generates a secure random key encoded in base64.
    """

    @staticmethod
    def generate() -> str:
        """
        Generates a secure random key and encodes it in base64 format.

        This method creates a cryptographically secure random key of 32 bytes,
        encodes it using base64 encoding, and returns the result as a string
        prefixed with 'base64:'.

        Returns
        -------
        str
            A string in the format 'base64:<key>', where <key> is a base64-encoded
            representation of a securely generated 32-byte random key.
        """

        # Generate 32 bytes of cryptographically secure random data
        key = os.urandom(32)

        # Encode the random bytes using base64 and decode to a UTF-8 string
        encoded = base64.b64encode(key).decode('utf-8')

        # Return the key in the required format
        return f"base64:{encoded}"