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
        Test that all metadata constants exist and are of type `str`.

        Raises
        ------
        AssertionError
            If any constant is not a string.
        """
        for const in [
            NAME, VERSION, AUTHOR, AUTHOR_EMAIL, DESCRIPTION,
            SKELETON, FRAMEWORK, DOCS, API, PYTHON_REQUIRES
        ]:
            self.assertIsInstance(const, str)

    async def testClassifiersStructure(self):
        """
        Test that `CLASSIFIERS` is a list of tuples of strings.

        Raises
        ------
        AssertionError
            If `CLASSIFIERS` is not a list of tuples of strings.
        """
        self.assertIsInstance(CLASSIFIERS, list)
        for item in CLASSIFIERS:
            self.assertIsInstance(item, tuple)
            self.assertTrue(all(isinstance(part, str) for part in item))

    async def testGetClassifiers(self):
        """
        Test that `get_classifiers` returns a list of classifier strings.

        Raises
        ------
        AssertionError
            If the returned value is not a list of strings containing '::'.
        """
        classifiers = get_classifiers()
        self.assertIsInstance(classifiers, list)
        for c in classifiers:
            self.assertIsInstance(c, str)
            self.assertTrue(" :: " in c or len(c.split(" :: ")) > 1)

    async def testKeywords(self):
        """
        Test that `KEYWORDS` is a list of strings and contains specific keywords.

        Raises
        ------
        AssertionError
            If `KEYWORDS` is not a list of strings or required keywords are missing.
        """
        self.assertIsInstance(KEYWORDS, list)
        for kw in KEYWORDS:
            self.assertIsInstance(kw, str)
        self.assertIn("orionis", KEYWORDS)
        self.assertIn("framework", KEYWORDS)

    async def testRequiresStructure(self):
        """
        Test that `REQUIRES` is a list of 2-element tuples of strings.

        Raises
        ------
        AssertionError
            If `REQUIRES` is not a list of 2-element tuples of strings.
        """
        self.assertIsInstance(REQUIRES, list)
        for req in REQUIRES:
            self.assertIsInstance(req, tuple)
            self.assertEqual(len(req), 2)
            self.assertTrue(all(isinstance(part, str) for part in req))

    async def testGetRequires(self):
        """
        Test that `get_requires` returns a list of requirement strings.

        Raises
        ------
        AssertionError
            If the returned value is not a list of strings containing '>='.
        """
        requires = get_requires()
        self.assertIsInstance(requires, list)
        for req in requires:
            self.assertIsInstance(req, str)
            self.assertIn(">=", req)