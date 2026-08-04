from __future__ import annotations
import json
from orionis.orm.collections.paginator import Paginator
from orionis.support.types.collection import Collection
from orionis.test import TestCase

class TestPaginator(TestCase):

    def _make(self, total: int, page: int, per_page: int) -> Paginator:
        """Build a paginator with dictionary items for serialization."""
        return Paginator(
            items=Collection([{"id": 1}, {"id": 2}]),
            total=total,
            page=page,
            per_page=per_page,
        )

    def testMetadataDerivation(self) -> None:
        """
        Derive lastPage and navigation flags from the metadata.

        Validates the pagination arithmetic.
        """
        paginator = self._make(total=5, page=2, per_page=2)
        self.assertEqual(paginator.last_page, 3)
        self.assertTrue(paginator.has_next)
        self.assertTrue(paginator.has_previous)
        self.assertEqual(len(paginator), 2)

    def testBoundaryPages(self) -> None:
        """
        Report navigation flags correctly on boundary pages.

        Validates the first and last page flags.
        """
        first = self._make(total=4, page=1, per_page=2)
        self.assertFalse(first.has_previous)
        self.assertTrue(first.has_next)

        last = self._make(total=4, page=2, per_page=2)
        self.assertTrue(last.has_previous)
        self.assertFalse(last.has_next)

    def testEmptyResultKeepsOnePage(self) -> None:
        """
        Keep lastPage at one for empty result sets.

        Validates the empty pagination floor.
        """
        paginator = Paginator(
            items=Collection([]),
            total=0,
            page=1,
            per_page=10,
        )
        self.assertEqual(paginator.last_page, 1)
        self.assertFalse(paginator.has_next)

    def testInvalidPageArgumentsRaise(self) -> None:
        """
        Raise ValueError for non-positive page arguments.

        Validates the constructor guards.
        """
        with self.assertRaises(ValueError):
            self._make(total=1, page=0, per_page=2)
        with self.assertRaises(ValueError):
            self._make(total=1, page=1, per_page=0)

    def testSerialization(self) -> None:
        """
        Serialize items and metadata into dict and JSON forms.

        Validates the serialization contract.
        """
        paginator = self._make(total=5, page=1, per_page=2)
        data = paginator.toDict()
        self.assertEqual(data["total"], 5)
        self.assertEqual(data["items"], [{"id": 1}, {"id": 2}])
        decoded = json.loads(paginator.toJson())
        self.assertEqual(decoded["lastPage"], 3)
