from orionis.metadata.framework import *
from orionis.test.cases.asynchronous import AsyncTestCase

class TestMetadataFramework(AsyncTestCase):
    """
    Test cases for the metadata constants and utility functions in orionis.metadata.framework.

    Notes
    -----
    This test suite validates the existence, type, and structure of metadata constants and utility
    functions provided by the `orionis.metadata.framework` module.
    """

    async def testConstantsExistAndAreStr(self):
        """
        Validate that all metadata constants exist and are of type `str`.

        This test iterates over a predefined list of metadata constants and checks
        that each constant is present and its type is `str`.

        Raises
        ------
        AssertionError
            If any constant is not a string.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Check each metadata constant for type str
        for const in [
            NAME, VERSION, AUTHOR, AUTHOR_EMAIL, DESCRIPTION,
            SKELETON, FRAMEWORK, DOCS, API, PYTHON_REQUIRES
        ]:
            self.assertIsInstance(const, str)

    async def testClassifiersStructure(self):
        """
        Ensure that `CLASSIFIERS` is a list of tuples containing strings.

        This test verifies the structure of the `CLASSIFIERS` constant, ensuring
        it is a list where each element is a tuple, and each tuple contains only strings.

        Raises
        ------
        AssertionError
            If `CLASSIFIERS` is not a list of tuples of strings.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Confirm CLASSIFIERS is a list
        self.assertIsInstance(CLASSIFIERS, list)

        # Check each item in CLASSIFIERS for tuple of strings
        for item in CLASSIFIERS:
            self.assertIsInstance(item, tuple)
            self.assertTrue(all(isinstance(part, str) for part in item))

    async def testGetClassifiers(self):
        """
        Verify that `get_classifiers` returns a list of classifier strings.

        This test calls the `get_classifiers` utility function and checks that
        the returned value is a list of strings, each representing a classifier.

        Raises
        ------
        AssertionError
            If the returned value is not a list of strings containing '::'.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Retrieve classifiers and validate their format
        classifiers = get_classifiers()
        self.assertIsInstance(classifiers, list)
        for c in classifiers:
            self.assertIsInstance(c, str)
            self.assertTrue(" :: " in c or len(c.split(" :: ")) > 1)

    async def testKeywords(self):
        """
        Check that `KEYWORDS` is a list of strings and contains required keywords.

        This test ensures that the `KEYWORDS` constant is a list of strings and
        verifies the presence of specific keywords relevant to the framework.

        Raises
        ------
        AssertionError
            If `KEYWORDS` is not a list of strings or required keywords are missing.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Confirm KEYWORDS is a list of strings
        self.assertIsInstance(KEYWORDS, list)
        for kw in KEYWORDS:
            self.assertIsInstance(kw, str)

        # Check for required keywords
        self.assertIn("orionis", KEYWORDS)
        self.assertIn("framework", KEYWORDS)

    async def testRequiresStructure(self):
        """
        Validate that `REQUIRES` is a list of 2-element tuples of strings.

        This test checks the structure of the `REQUIRES` constant, ensuring it is
        a list where each element is a tuple of length 2, and both elements are strings.

        Raises
        ------
        AssertionError
            If `REQUIRES` is not a list of 2-element tuples of strings.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Confirm REQUIRES is a list of 2-element tuples of strings
        self.assertIsInstance(REQUIRES, list)
        for req in REQUIRES:
            self.assertIsInstance(req, tuple)
            self.assertEqual(len(req), 2)
            self.assertTrue(all(isinstance(part, str) for part in req))

    async def testGetRequires(self):
        """
        Ensure that `get_requires` returns a list of requirement strings.

        This test calls the `get_requires` utility function and checks that the
        returned value is a list of strings, each representing a requirement and
        containing the '>=' version specifier.

        Raises
        ------
        AssertionError
            If the returned value is not a list of strings containing '>='.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Retrieve requirements and validate their format
        requires = get_requires()
        self.assertIsInstance(requires, list)
        for req in requires:
            self.assertIsInstance(req, str)
            self.assertIn(">=", req)