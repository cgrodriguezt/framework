from __future__ import annotations
from orionis.services.system.imports import Imports
from orionis.services.system.contracts.imports import IImports
from orionis.test import TestCase

# ===========================================================================
# TestImports
# ===========================================================================

class TestImports(TestCase):

    def testImplementsIImports(self) -> None:
        """
        Assert that Imports implements the IImports contract.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        self.assertIsInstance(instance, IImports)

    def testCanBeInstantiated(self) -> None:
        """
        Assert that Imports can be created without arguments.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        self.assertIsNotNone(instance)

    def testInitialImportsListIsEmpty(self) -> None:
        """
        Assert that the imports list is initially empty.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        self.assertIsInstance(instance.imports, list)
        self.assertEqual(len(instance.imports), 0)

    def testCollectReturnsSelf(self) -> None:
        """
        Assert that collect() returns the same Imports instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        result = instance.collect()
        self.assertIs(result, instance)

    def testCollectPopulatesImportsList(self) -> None:
        """
        Assert that collect() fills the imports list with module data.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        instance.collect()
        self.assertIsInstance(instance.imports, list)

    def testCollectItemsHaveExpectedKeys(self) -> None:
        """
        Assert that each item from collect() has name, file, and symbols keys.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        instance.collect()
        for item in instance.imports:
            self.assertIn("name", item)
            self.assertIn("file", item)
            self.assertIn("symbols", item)

    def testClearEmptiesImportsList(self) -> None:
        """
        Assert that clear() empties the imports list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        instance.collect()
        instance.clear()
        self.assertEqual(len(instance.imports), 0)

    def testCollectAfterClearRepopulates(self) -> None:
        """
        Assert that calling collect() after clear() repopulates the list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        instance.collect()
        count_first = len(instance.imports)
        instance.clear()
        instance.collect()
        self.assertEqual(len(instance.imports), count_first)

    def testMultipleCollectCallsDoNotDuplicate(self) -> None:
        """
        Assert that calling collect() twice does not duplicate entries.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        instance.collect()
        count_first = len(instance.imports)
        instance.collect()
        self.assertEqual(len(instance.imports), count_first)

    def testSymbolsIsAList(self) -> None:
        """
        Assert that each item's symbols field is a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        instance.collect()
        for item in instance.imports:
            self.assertIsInstance(item["symbols"], list)

    def testNameIsString(self) -> None:
        """
        Assert that each item's name field is a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = Imports()
        instance.collect()
        for item in instance.imports:
            self.assertIsInstance(item["name"], str)
