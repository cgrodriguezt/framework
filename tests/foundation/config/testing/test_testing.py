from orionis.test import TestCase
from orionis.foundation.config.testing.entities.testing import Testing
from orionis.foundation.config.testing.enums.verbosity import VerbosityMode

# ===========================================================================
# VerbosityMode enum
# ===========================================================================

class TestVerbosityModeEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that SILENT, MINIMAL and DETAILED members exist in VerbosityMode.

        Returns
        -------
        None
            This method does not return a value.
        """
        for name in ("SILENT", "MINIMAL", "DETAILED"):
            self.assertIn(name, VerbosityMode._member_names_)

    def testMemberValues(self) -> None:
        """
        Test the integer values assigned to each VerbosityMode member.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(VerbosityMode.SILENT.value, 0)
        self.assertEqual(VerbosityMode.MINIMAL.value, 1)
        self.assertEqual(VerbosityMode.DETAILED.value, 2)

    def testLookupByName(self) -> None:
        """
        Test that VerbosityMode members can be retrieved by their name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(VerbosityMode["DETAILED"], VerbosityMode.DETAILED)

    def testLookupByValue(self) -> None:
        """
        Test that VerbosityMode members can be retrieved by their integer value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(VerbosityMode(0), VerbosityMode.SILENT)

    def testUnknownValueRaises(self) -> None:
        """
        Test that an unknown verbosity value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            VerbosityMode(99)

    def testMemberCount(self) -> None:
        """
        Test that exactly three VerbosityMode members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(VerbosityMode), 3)

    def testValuesAreIntegers(self) -> None:
        """
        Test that all VerbosityMode values are integers.

        Returns
        -------
        None
            This method does not return a value.
        """
        for member in VerbosityMode:
            self.assertIsInstance(member.value, int)

# ===========================================================================
# Testing entity
# ===========================================================================

class TestTestingEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Testing can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        t = Testing()
        self.assertIsInstance(t, Testing)

    def testDefaultVerbosityIsDetailedValue(self) -> None:
        """
        Test that the default verbosity equals VerbosityMode.DETAILED.value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Testing().verbosity, VerbosityMode.DETAILED.value)

    def testDefaultFailFastIsFalse(self) -> None:
        """
        Test that fail_fast defaults to False.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertFalse(Testing().fail_fast)

    def testDefaultStartDir(self) -> None:
        """
        Test that start_dir defaults to 'tests'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Testing().start_dir, "tests")

    def testDefaultFilePattern(self) -> None:
        """
        Test that file_pattern defaults to 'test_*.py'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Testing().file_pattern, "test_*.py")

    def testDefaultMethodPattern(self) -> None:
        """
        Test that method_pattern defaults to 'test*'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Testing().method_pattern, "test*")

    def testVerbosityEnumNormalization(self) -> None:
        """
        Test that passing a VerbosityMode enum is stored as its integer value.

        Returns
        -------
        None
            This method does not return a value.
        """
        t = Testing(verbosity=VerbosityMode.SILENT)
        self.assertEqual(t.verbosity, VerbosityMode.SILENT.value)

    def testVerbosityValidIntAccepted(self) -> None:
        """
        Test that a valid integer verbosity (0, 1, or 2) is accepted.

        Returns
        -------
        None
            This method does not return a value.
        """
        for v in (0, 1, 2):
            t = Testing(verbosity=v)
            self.assertEqual(t.verbosity, v)

    def testInvalidVerbosityIntRaisesTypeError(self) -> None:
        """
        Test that an out-of-range integer verbosity raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Testing(verbosity=99)

    def testInvalidVerbosityTypeRaisesTypeError(self) -> None:
        """
        Test that a non-integer, non-VerbosityMode verbosity raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Testing(verbosity="detailed")  # type: ignore[arg-type]

    def testInvalidFailFastTypeRaisesTypeError(self) -> None:
        """
        Test that a non-boolean fail_fast raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Testing(fail_fast="yes")  # type: ignore[arg-type]

    def testInvalidStartDirTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string start_dir raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Testing(start_dir=123)  # type: ignore[arg-type]

    def testInvalidFilePatternTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string file_pattern raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Testing(file_pattern=0)  # type: ignore[arg-type]

    def testInvalidMethodPatternTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string method_pattern raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Testing(method_pattern=[])  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Testing instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        t = Testing()
        with self.assertRaises(FrozenInstanceError):
            t.verbosity = 0  # type: ignore[misc]
