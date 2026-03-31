import inspect
from orionis.services.encrypter.contracts.encrypter import IEncrypter
from orionis.test import TestCase

class _ConcreteEncrypter(IEncrypter):
    """Minimal concrete implementation used to verify the contract can be satisfied."""

    def encrypt(self, plaintext: str) -> str:
        return "stub_encrypted"

    def decrypt(self, payload: str) -> str:
        return "stub_decrypted"


class _PartialEncrypter(IEncrypter):
    """Subclass that implements only encrypt — intentionally incomplete."""

    def encrypt(self, plaintext: str) -> str:
        return plaintext

# ===========================================================================
# TestIEncrypterContract
# ===========================================================================

class TestIEncrypterContract(TestCase):

    def testIEncrypterCannotBeInstantiatedDirectly(self) -> None:
        """
        Test that IEncrypter raises TypeError when instantiated directly.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            IEncrypter()  # type: ignore[abstract]

    def testEncryptIsAbstractMethod(self) -> None:
        """
        Test that 'encrypt' is present in IEncrypter.__abstractmethods__.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("encrypt", IEncrypter.__abstractmethods__)

    def testDecryptIsAbstractMethod(self) -> None:
        """
        Test that 'decrypt' is present in IEncrypter.__abstractmethods__.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("decrypt", IEncrypter.__abstractmethods__)

    def testAbstractMethodsSetContainsExactlyEncryptAndDecrypt(self) -> None:
        """
        Test that __abstractmethods__ contains exactly 'encrypt' and 'decrypt'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(IEncrypter.__abstractmethods__, frozenset({"encrypt", "decrypt"}))

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Test that a subclass missing 'decrypt' cannot be instantiated.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            _PartialEncrypter()  # type: ignore[abstract]

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Test that a fully implemented subclass of IEncrypter can be instantiated.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _ConcreteEncrypter()
        self.assertIsInstance(enc, IEncrypter)

    def testConcreteSubclassIsInstanceOfIEncrypter(self) -> None:
        """
        Test that isinstance check passes for a concrete IEncrypter subclass.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _ConcreteEncrypter()
        self.assertIsInstance(enc, IEncrypter)

    def testEncryptSignatureAcceptsPlaintextArg(self) -> None:
        """
        Test that 'encrypt' is declared with a 'plaintext' parameter.

        Returns
        -------
        None
            This method does not return a value.
        """
        sig = inspect.signature(IEncrypter.encrypt)
        self.assertIn("plaintext", sig.parameters)

    def testDecryptSignatureAcceptsPayloadArg(self) -> None:
        """
        Test that 'decrypt' is declared with a 'payload' parameter.

        Returns
        -------
        None
            This method does not return a value.
        """
        sig = inspect.signature(IEncrypter.decrypt)
        self.assertIn("payload", sig.parameters)

    def testIEncrypterInheritsFromABC(self) -> None:
        """
        Test that IEncrypter inherits from ABC.

        Returns
        -------
        None
            This method does not return a value.
        """
        from abc import ABC
        self.assertTrue(issubclass(IEncrypter, ABC))

    def testEncryptMarkedAsAbstract(self) -> None:
        """
        Test that IEncrypter.encrypt carries the __isabstractmethod__ flag.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(getattr(IEncrypter.encrypt, "__isabstractmethod__", False))

    def testDecryptMarkedAsAbstract(self) -> None:
        """
        Test that IEncrypter.decrypt carries the __isabstractmethod__ flag.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(getattr(IEncrypter.decrypt, "__isabstractmethod__", False))

    def testConcreteEncryptReturnsString(self) -> None:
        """
        Test that the concrete stub's encrypt() returns a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _ConcreteEncrypter()
        result = enc.encrypt("hello")
        self.assertIsInstance(result, str)

    def testConcreteDecryptReturnsString(self) -> None:
        """
        Test that the concrete stub's decrypt() returns a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        enc = _ConcreteEncrypter()
        result = enc.decrypt("payload")
        self.assertIsInstance(result, str)
