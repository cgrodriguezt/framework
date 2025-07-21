
import os
import base64

class SecureKeyGenerator:
    """
    SecureKeyGenerator
    ==================

    Provides static methods for generating secure random keys in base64 format.

    Methods
    -------
    generate_key() : str
        Generates a secure random key encoded in base64.
    """

    @staticmethod
    def generate() -> str:
        """
        Generates a secure random key encoded in base64.

        Returns
        -------
        str
            A string containing the generated key in the format 'base64:<key>'.
        """
        key = os.urandom(32)
        encoded = base64.b64encode(key).decode('utf-8')
        return f"base64:{encoded}"