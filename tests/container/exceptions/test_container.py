from __future__ import annotations
from orionis.test import TestCase
from orionis.container.exceptions.container import CircularDependencyException

class TestCircularDependencyException(TestCase):

    # ------------------------------------------------------------------
    # Inheritance
    # ------------------------------------------------------------------

    def testIsSubclassOfException(self) -> None:
        """
        Test that CircularDependencyException is a subclass of Exception.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(CircularDependencyException, Exception))

    # ------------------------------------------------------------------
    # Instantiation — no message
    # ------------------------------------------------------------------

    def testCanBeInstantiatedWithoutMessage(self) -> None:
        """
        Test that CircularDependencyException can be raised without arguments.

        Returns
        -------
        None
            This method does not return a value.
        """
        exc = CircularDependencyException()
        self.assertIsInstance(exc, CircularDependencyException)

    def testArgsEmptyWhenNoMessageProvided(self) -> None:
        """
        Test that args is an empty tuple when no message is supplied.

        Returns
        -------
        None
            This method does not return a value.
        """
        exc = CircularDependencyException()
        self.assertEqual(exc.args, ())

    # ------------------------------------------------------------------
    # Instantiation — with message
    # ------------------------------------------------------------------

    def testCanBeInstantiatedWithMessage(self) -> None:
        """
        Test that CircularDependencyException stores a message correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        exc = CircularDependencyException("circular dependency detected")
        self.assertEqual(str(exc), "circular dependency detected")

    def testArgsContainsMessageWhenProvided(self) -> None:
        """
        Test that the args tuple contains the supplied message string.

        Returns
        -------
        None
            This method does not return a value.
        """
        msg = "A -> B -> A"
        exc = CircularDependencyException(msg)
        self.assertIn(msg, exc.args)

    # ------------------------------------------------------------------
    # Raise / catch
    # ------------------------------------------------------------------

    def testCanBeRaisedAndCaughtAsCircularDependencyException(self) -> None:
        """
        Test that the exception can be raised and caught by its own type.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(CircularDependencyException):
            raise CircularDependencyException("cycle")

    def testCanBeRaisedAndCaughtAsException(self) -> None:
        """
        Test that the exception can be caught by the base Exception handler.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(Exception):
            raise CircularDependencyException("cycle")

    def testRaisedExceptionPreservesMessage(self) -> None:
        """
        Test that the message is preserved after the exception is raised.

        Returns
        -------
        None
            This method does not return a value.
        """
        try:
            raise CircularDependencyException("A depends on B which depends on A")
        except CircularDependencyException as exc:
            self.assertEqual(str(exc), "A depends on B which depends on A")

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def testTwoInstancesAreNotTheSameObject(self) -> None:
        """
        Test that two separately constructed instances are distinct objects.

        Returns
        -------
        None
            This method does not return a value.
        """
        exc_a = CircularDependencyException("msg")
        exc_b = CircularDependencyException("msg")
        self.assertIsNot(exc_a, exc_b)
