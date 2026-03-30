from orionis.metadata import framework as fw
from orionis.metadata.framework import (
    API,
    AUTHOR,
    AUTHOR_EMAIL,
    DESCRIPTION,
    DOCS,
    FRAMEWORK,
    NAME,
    PYTHON_REQUIRES,
    SKELETON,
    VERSION,
)
from orionis.test import TestCase

class TestMetadataFrameworkImport(TestCase):

    def testModuleImportSucceeds(self) -> None:
        """
        Test that the framework metadata module can be imported without errors.

        Returns
        -------
        None
            This method does not return a value.
        """
        import orionis.metadata.framework as m

        self.assertIsNotNone(m)

    def testPackageImportSucceeds(self) -> None:
        """
        Test that the orionis.metadata package can be imported without errors.

        Returns
        -------
        None
            This method does not return a value.
        """
        import orionis.metadata as pkg

        self.assertIsNotNone(pkg)

    def testAllExpectedAttributesExist(self) -> None:
        """
        Test that all expected constant attributes exist in the framework module.

        Returns
        -------
        None
            This method does not return a value.
        """
        expected = (
            "NAME",
            "VERSION",
            "AUTHOR",
            "AUTHOR_EMAIL",
            "DESCRIPTION",
            "SKELETON",
            "FRAMEWORK",
            "DOCS",
            "API",
            "PYTHON_REQUIRES",
        )
        for attr in expected:
            self.assertTrue(
                hasattr(fw, attr),
                msg=f"Missing attribute '{attr}' in orionis.metadata.framework",
            )

    def testFrameworkAttributeReachableViaPackage(self) -> None:
        """
        Test that the framework submodule is reachable through the package.

        Returns
        -------
        None
            This method does not return a value.
        """
        import orionis.metadata as pkg

        self.assertTrue(hasattr(pkg, "framework"))

# ===========================================================================
# TestMetadataFrameworkName
# ===========================================================================

class TestMetadataFrameworkName(TestCase):

    def testNameIsString(self) -> None:
        """
        Test that NAME is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(NAME, str)

    def testNameIsNotEmpty(self) -> None:
        """
        Test that NAME is not an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(NAME), 0)

    def testNameValueIsOrionis(self) -> None:
        """
        Test that NAME equals the expected value 'orionis'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(NAME, "orionis")

    def testNameIsLowerCase(self) -> None:
        """
        Test that NAME contains only lowercase characters (package naming convention).

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(NAME, NAME.lower())

    def testNameContainsNoWhitespace(self) -> None:
        """
        Test that NAME does not contain any whitespace characters.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertNotIn(" ", NAME)

# ===========================================================================
# TestMetadataFrameworkVersion
# ===========================================================================

class TestMetadataFrameworkVersion(TestCase):

    def testVersionIsString(self) -> None:
        """
        Test that VERSION is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(VERSION, str)

    def testVersionIsNotEmpty(self) -> None:
        """
        Test that VERSION is not an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(VERSION), 0)

    def testVersionMatchesNumericDotPattern(self) -> None:
        """
        Test that VERSION follows a numeric dot-separated pattern (e.g. '1.2.3').

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertRegex(VERSION, r"^\d+\.\d+(\.\d+)*$")

    def testVersionHasAtLeastTwoSegments(self) -> None:
        """
        Test that VERSION contains at least two dot-separated segments.

        Returns
        -------
        None
            This method does not return a value.
        """
        segments = VERSION.split(".")
        self.assertGreaterEqual(len(segments), 2)

    def testVersionSegmentsAreAllNumeric(self) -> None:
        """
        Test that every segment of VERSION is composed of digits only.

        Returns
        -------
        None
            This method does not return a value.
        """
        for segment in VERSION.split("."):
            self.assertTrue(
                segment.isdigit(),
                msg=f"Version segment '{segment}' is not numeric",
            )

    def testVersionContainsNoWhitespace(self) -> None:
        """
        Test that VERSION does not contain any whitespace characters.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertNotIn(" ", VERSION)

# ===========================================================================
# TestMetadataFrameworkAuthor
# ===========================================================================

class TestMetadataFrameworkAuthor(TestCase):

    def testAuthorIsString(self) -> None:
        """
        Test that AUTHOR is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(AUTHOR, str)

    def testAuthorIsNotEmpty(self) -> None:
        """
        Test that AUTHOR is not an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(AUTHOR.strip()), 0)

    def testAuthorContainsAtLeastTwoWords(self) -> None:
        """
        Test that AUTHOR contains at least two words (first and last name).

        Returns
        -------
        None
            This method does not return a value.
        """
        words = AUTHOR.strip().split()
        self.assertGreaterEqual(len(words), 2)

# ===========================================================================
# TestMetadataFrameworkAuthorEmail
# ===========================================================================

class TestMetadataFrameworkAuthorEmail(TestCase):

    def testAuthorEmailIsString(self) -> None:
        """
        Test that AUTHOR_EMAIL is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(AUTHOR_EMAIL, str)

    def testAuthorEmailIsNotEmpty(self) -> None:
        """
        Test that AUTHOR_EMAIL is not an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(AUTHOR_EMAIL.strip()), 0)

    def testAuthorEmailContainsAtSymbol(self) -> None:
        """
        Test that AUTHOR_EMAIL contains exactly one '@' character.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(AUTHOR_EMAIL.count("@"), 1)

    def testAuthorEmailMatchesBasicEmailPattern(self) -> None:
        """
        Test that AUTHOR_EMAIL matches a basic email address pattern.

        Returns
        -------
        None
            This method does not return a value.
        """
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        self.assertRegex(AUTHOR_EMAIL, pattern)

    def testAuthorEmailContainsNoWhitespace(self) -> None:
        """
        Test that AUTHOR_EMAIL contains no whitespace characters.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertNotIn(" ", AUTHOR_EMAIL)

    def testAuthorEmailHasDomainWithDot(self) -> None:
        """
        Test that the domain part of AUTHOR_EMAIL contains a dot.

        Returns
        -------
        None
            This method does not return a value.
        """
        domain = AUTHOR_EMAIL.split("@")[1]
        self.assertIn(".", domain)

# ===========================================================================
# TestMetadataFrameworkDescription
# ===========================================================================

class TestMetadataFrameworkDescription(TestCase):

    def testDescriptionIsString(self) -> None:
        """
        Test that DESCRIPTION is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(DESCRIPTION, str)

    def testDescriptionIsNotEmpty(self) -> None:
        """
        Test that DESCRIPTION is not an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(DESCRIPTION.strip()), 0)

    def testDescriptionContainsFrameworkName(self) -> None:
        """
        Test that DESCRIPTION references the framework name 'Orionis'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("Orionis", DESCRIPTION)

    def testDescriptionHasMeaningfulLength(self) -> None:
        """
        Test that DESCRIPTION is longer than 20 characters to ensure it is meaningful.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(DESCRIPTION), 20)

# ===========================================================================
# TestMetadataFrameworkUrls
# ===========================================================================

class TestMetadataFrameworkUrls(TestCase):

    _URL_CONSTANTS = {
        "SKELETON": SKELETON,
        "FRAMEWORK": FRAMEWORK,
        "DOCS": DOCS,
        "API": API,
    }

    def testSkeletonIsString(self) -> None:
        """
        Test that SKELETON is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(SKELETON, str)

    def testSkeletonIsNotEmpty(self) -> None:
        """
        Test that SKELETON is not an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(SKELETON.strip()), 0)

    def testSkeletonStartsWithHttps(self) -> None:
        """
        Test that SKELETON starts with 'https://'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(SKELETON.startswith("https://"))

    def testFrameworkIsString(self) -> None:
        """
        Test that FRAMEWORK is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(FRAMEWORK, str)

    def testFrameworkIsNotEmpty(self) -> None:
        """
        Test that FRAMEWORK is not an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(FRAMEWORK.strip()), 0)

    def testFrameworkStartsWithHttps(self) -> None:
        """
        Test that FRAMEWORK starts with 'https://'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(FRAMEWORK.startswith("https://"))

    def testDocsIsString(self) -> None:
        """
        Test that DOCS is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(DOCS, str)

    def testDocsIsNotEmpty(self) -> None:
        """
        Test that DOCS is not an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(DOCS.strip()), 0)

    def testDocsStartsWithHttps(self) -> None:
        """
        Test that DOCS starts with 'https://'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(DOCS.startswith("https://"))

    def testApiIsString(self) -> None:
        """
        Test that API is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(API, str)

    def testApiIsNotEmpty(self) -> None:
        """
        Test that API is not an empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(API.strip()), 0)

    def testApiStartsWithHttps(self) -> None:
        """
        Test that API starts with 'https://'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(API.startswith("https://"))

    def testAllUrlsAreUnique(self) -> None:
        """
        Test that SKELETON, FRAMEWORK, DOCS, and API are all distinct URLs.

        Returns
        -------
        None
            This method does not return a value.
        """
        urls = [SKELETON, FRAMEWORK, DOCS, API]
        self.assertEqual(len(urls), len(set(urls)))

    def testAllUrlsContainDomain(self) -> None:
        """
        Test that every URL constant contains at least one dot in the domain part.

        Returns
        -------
        None
            This method does not return a value.
        """
        for name, url in self._URL_CONSTANTS.items():
            # Strip protocol and check the remaining part contains a dot
            remainder = url.replace("https://", "").replace("http://", "")
            self.assertIn(
                ".",
                remainder,
                msg=f"URL constant '{name}' has no dot in the domain",
            )

    def testAllUrlsContainNoWhitespace(self) -> None:
        """
        Test that none of the URL constants contain whitespace characters.

        Returns
        -------
        None
            This method does not return a value.
        """
        for name, url in self._URL_CONSTANTS.items():
            self.assertNotIn(
                " ",
                url,
                msg=f"URL constant '{name}' contains whitespace",
            )

    def testSkeletonContainsOrionis(self) -> None:
        """
        Test that SKELETON URL references the orionis-framework organisation.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("orionis", SKELETON.lower())

    def testFrameworkContainsOrionis(self) -> None:
        """
        Test that FRAMEWORK URL references the orionis-framework organisation.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("orionis", FRAMEWORK.lower())

    def testApiPointsToPypi(self) -> None:
        """
        Test that API URL points to the PyPI JSON endpoint.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("pypi", API.lower())

# ===========================================================================
# TestMetadataFrameworkPythonRequires
# ===========================================================================

class TestMetadataFrameworkPythonRequires(TestCase):
    """Tests for the PYTHON_REQUIRES constant."""

    def testPythonRequiresIsTuple(self) -> None:
        """
        Test that PYTHON_REQUIRES is a tuple.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(PYTHON_REQUIRES, tuple)

    def testPythonRequiresHasAtLeastTwoElements(self) -> None:
        """
        Test that PYTHON_REQUIRES contains at least two elements (major, minor).

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreaterEqual(len(PYTHON_REQUIRES), 2)

    def testPythonRequiresAllElementsAreIntegers(self) -> None:
        """
        Test that every element in PYTHON_REQUIRES is an integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        for i, elem in enumerate(PYTHON_REQUIRES):
            self.assertIsInstance(elem, int, msg=f"Element at index {i} is not an int")

    def testPythonRequiresMajorVersionIsAtLeastThree(self) -> None:
        """
        Test that the major Python version required is at least 3.

        Returns
        -------
        None
            This method does not return a value.
        """
        major = PYTHON_REQUIRES[0]
        self.assertGreaterEqual(major, 3)

    def testPythonRequiresMinorVersionIsNonNegative(self) -> None:
        """
        Test that the minor Python version required is a non-negative integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        minor = PYTHON_REQUIRES[1]
        self.assertGreaterEqual(minor, 0)

    def testPythonRequiresIsNotEmpty(self) -> None:
        """
        Test that PYTHON_REQUIRES is not an empty tuple.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(len(PYTHON_REQUIRES), 0)

    def testPythonRequiresCanBeUsedForVersionComparison(self) -> None:
        """
        Test that PYTHON_REQUIRES can be compared against sys.version_info.

        The tuple must be comparable element-wise with sys.version_info,
        which requires all elements to be integers.

        Returns
        -------
        None
            This method does not return a value.
        """
        import sys

        # Check the comparison operation itself doesn't raise
        result = PYTHON_REQUIRES <= sys.version_info[: len(PYTHON_REQUIRES)]
        self.assertIsInstance(result, bool)

    def testPythonRequiresMajorMinorArePositive(self) -> None:
        """
        Test that both the major and minor version numbers are positive integers.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertGreater(PYTHON_REQUIRES[0], 0)
        self.assertGreaterEqual(PYTHON_REQUIRES[1], 0)
