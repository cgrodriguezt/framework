from __future__ import annotations
from abc import ABC
from orionis.encrypter.contracts.encrypter import IEncrypter
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Concrete stub — used for instantiation tests only
# ---------------------------------------------------------------------------

class _ConcreteEncrypter(IEncrypter):
    """Minimal IEncrypter implementation used only for structural tests."""

    def encrypt(self, _plaintext: str) -> str:  # NOSONAR
        """Return an empty string (stub)."""
        return ""

    def decrypt(self, _payload: str) -> str:  # NOSONAR
        """Return an empty string (stub)."""
        return ""

# ===========================================================================
# IEncrypter contract
# ===========================================================================

class TestIEncrypter(TestCase):

    # ------------------------------------------------------------------
    # Structural / ABC
    # ------------------------------------------------------------------

    def testIsAbstractBaseClass(self) -> None:
        """
        Verify IEncrypter is a subclass of ABC.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(IEncrypter, ABC))

    def testCannotBeInstantiatedDirectly(self) -> None:
        """
        Raise TypeError when IEncrypter is instantiated directly.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            IEncrypter()  # type: ignore[abstract]

    # ------------------------------------------------------------------
    # Abstract method presence
    # ------------------------------------------------------------------

    def testHasAbstractMethodEncrypt(self) -> None:
        """
        Verify 'encrypt' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("encrypt", IEncrypter.__abstractmethods__)

    def testHasAbstractMethodDecrypt(self) -> None:
        """
        Verify 'decrypt' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("decrypt", IEncrypter.__abstractmethods__)

    def testAbstractMethodsMatchExpectedSet(self) -> None:
        """
        Verify IEncrypter exposes exactly the expected abstract methods.

        Returns
        -------
        None
            This method does not return a value.
        """
        expected = frozenset({"encrypt", "decrypt"})
        self.assertEqual(IEncrypter.__abstractmethods__, expected)

    # ------------------------------------------------------------------
    # Concrete subclass
    # ------------------------------------------------------------------

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Instantiate a concrete subclass implementing all abstract methods.

        Returns
        -------
        None
            This method does not return a value.
        """
        obj = _ConcreteEncrypter()
        self.assertIsInstance(obj, IEncrypter)

    def testEncryptIsCallableOnConcreteSubclass(self) -> None:
        """
        Verify encrypt() is callable on a concrete subclass instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(callable(_ConcreteEncrypter().encrypt))

    def testDecryptIsCallableOnConcreteSubclass(self) -> None:
        """
        Verify decrypt() is callable on a concrete subclass instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(callable(_ConcreteEncrypter().decrypt))
