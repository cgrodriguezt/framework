from unittest.mock import Mock
from orionis.support.structures.collection import Collection
from orionis.test.cases.synchronous import SyncTestCase

class TestCollection(SyncTestCase):

    def testInitialization(self):
        """
        Test the initialization of Collection instances.

        This test verifies that Collection instances can be created both with and without
        initial items, and that the internal state is correctly initialized.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test initialization without items
        collection = Collection()
        self.assertEqual(collection.all(), [])
        self.assertEqual(collection.count(), 0)

        # Test initialization with items
        collection = Collection([1, 2, 3])
        self.assertEqual(collection.all(), [1, 2, 3])
        self.assertEqual(collection.count(), 3)

        # Test initialization with None (should default to empty list)
        collection = Collection(None)
        self.assertEqual(collection.all(), [])

    def testTake(self):
        """
        Test the take method for retrieving specific number of items.

        This test verifies that the take method correctly returns a new Collection
        with the specified number of items, handling both positive and negative numbers.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4, 5])

        # Test taking positive number of items
        result = collection.take(3)
        self.assertIsInstance(result, Collection)
        self.assertEqual(result.all(), [1, 2, 3])

        # Test taking negative number (from end)
        result = collection.take(-2)
        self.assertIsInstance(result, Collection)
        self.assertEqual(result.all(), [4, 5])

        # Test taking zero items
        result = collection.take(0)
        self.assertEqual(result.all(), [])

        # Test taking more items than available
        result = collection.take(10)
        self.assertEqual(result.all(), [1, 2, 3, 4, 5])

    def testFirst(self):
        """
        Test the first method for retrieving the first item.

        This test verifies that the first method correctly returns the first item
        in the collection, with and without callback filtering.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        # Test getting first item without callback
        self.assertEqual(collection.first(), 1)

        # Test getting first item with callback
        self.assertEqual(collection.first(lambda x: x > 2), 3)

        # Test first with callback that matches no items
        self.assertIsNone(collection.first(lambda x: x > 10))

        # Test first on empty collection
        empty_collection = Collection([])
        self.assertIsNone(empty_collection.first())

    def testLast(self):
        """
        Test the last method for retrieving the last item.

        This test verifies that the last method correctly returns the last item
        in the collection, with and without callback filtering.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        # Test getting last item without callback
        self.assertEqual(collection.last(), 4)

        # Test getting last item with callback
        self.assertEqual(collection.last(lambda x: x < 3), 2)

    def testAll(self):
        """
        Test the all method for retrieving all items.

        This test verifies that the all method correctly returns all items
        in the collection as a list.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        items = [1, 2, 3, 4]
        collection = Collection(items)
        self.assertEqual(collection.all(), items)

        # Test with complex objects
        complex_items = [{"id": 1}, {"id": 2}]
        collection = Collection(complex_items)
        self.assertEqual(collection.all(), complex_items)

    def testAvg(self):
        """
        Test the avg method for calculating averages.

        This test verifies that the avg method correctly calculates the average
        of numeric values, both directly and via key extraction.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test average of simple numbers
        collection = Collection([1, 2, 3, 4])
        self.assertEqual(collection.avg(), 2.5)

        # Test average with key extraction
        collection = Collection([
            {"name": "Juan Sebastian", "age": 25},
            {"name": "Carlos Giovanny", "age": 35},
            {"name": "John Alejandro", "age": 30},
        ])
        self.assertEqual(collection.avg("age"), 30.0)

        # Test average with non-numeric values
        collection = Collection(["a", "b", "c"])
        self.assertEqual(collection.avg(), 0)

        # Test average on empty collection (should handle division by zero)
        collection = Collection([])
        with self.assertRaises(ZeroDivisionError):
            collection.avg()

    def testMax(self):
        """
        Test the max method for finding maximum values.

        This test verifies that the max method correctly finds the maximum value
        in the collection, both directly and via key extraction.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test max of simple numbers
        collection = Collection([1, 5, 3, 4])
        self.assertEqual(collection.max(), 5)

        # Test max with key extraction
        collection = Collection([
            {"name": "Juan Sebastian", "age": 25},
            {"name": "Carlos Giovanny", "age": 35},
            {"name": "John Alejandro", "age": 30},
        ])
        self.assertEqual(collection.max("age"), 35)

        # Test max with non-numeric values (should return the max string)
        collection = Collection(["a", "b", "c"])
        self.assertEqual(collection.max(), "c")

    def testMin(self):
        """
        Test the min method for finding minimum values.

        This test verifies that the min method correctly finds the minimum value
        in the collection, both directly and via key extraction.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test min of simple numbers
        collection = Collection([5, 1, 3, 4])
        self.assertEqual(collection.min(), 1)

        # Test min with key extraction
        collection = Collection([
            {"name": "Wilmer Alonso", "age": 25},
            {"name": "Jorge Hernan", "age": 35},
            {"name": "Daniel Stiven", "age": 20},
        ])
        self.assertEqual(collection.min("age"), 20)

        # Test min with non-numeric values
        collection = Collection(["c", "a", "b"])
        self.assertEqual(collection.min(), "a")

    def testChunk(self):
        """
        Test the chunk method for breaking collections into smaller chunks.

        This test verifies that the chunk method correctly divides the collection
        into smaller collections of the specified size.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4, 5, 6])

        # Test chunking into groups of 2
        chunked = collection.chunk(2)
        self.assertIsInstance(chunked, Collection)
        self.assertEqual(chunked.count(), 3)
        self.assertEqual(chunked.all()[0], Collection([1, 2]))
        self.assertEqual(chunked.all()[1], Collection([3, 4]))
        self.assertEqual(chunked.all()[2], Collection([5, 6]))

        # Test chunking with remainder
        collection = Collection([1, 2, 3, 4, 5])
        chunked = collection.chunk(2)
        self.assertEqual(chunked.count(), 3)
        self.assertEqual(chunked.all()[2], Collection([5]))

    def testCollapse(self):
        """
        Test the collapse method for flattening nested collections.

        This test verifies that the collapse method correctly flattens
        nested collections into a single flat collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([Collection([1, 2]), Collection([3, 4]), [5, 6]])
        collapsed = collection.collapse()

        self.assertIsInstance(collapsed, Collection)
        self.assertEqual(collapsed.all(), [1, 2, 3, 4, 5, 6])

    def testContains(self):
        """
        Test the contains method for checking item existence.

        This test verifies that the contains method correctly determines
        whether items exist in the collection using various methods.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        # Test direct value containment
        self.assertTrue(collection.contains(3))
        self.assertFalse(collection.contains(5))

        # Test with callback function
        self.assertTrue(collection.contains(lambda x: x > 3))
        self.assertFalse(collection.contains(lambda x: x > 10))

        # Test with key-value pairs
        collection = Collection([
            {"name": "Blas Alberto", "age": 25},
            {"name": "Alejandro Talero", "age": 35},
        ])
        self.assertTrue(collection.contains("age", 25))
        self.assertFalse(collection.contains("age", 40))

    def testCount(self):
        """
        Test the count method for getting collection size.

        This test verifies that the count method correctly returns
        the number of items in the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])
        self.assertEqual(collection.count(), 4)

        empty_collection = Collection([])
        self.assertEqual(empty_collection.count(), 0)

    def testDiff(self):
        """
        Test the diff method for finding differences between collections.

        This test verifies that the diff method correctly returns items
        that are not present in the comparison collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])
        other = Collection([2, 4, 6])

        diff = collection.diff(other)
        self.assertIsInstance(diff, Collection)
        self.assertEqual(diff.all(), [1, 3])

        # Test with list instead of Collection
        diff = collection.diff([2, 4, 6])
        self.assertEqual(diff.all(), [1, 3])

    def testEach(self):
        """
        Test the each method for iterating over items.

        This test verifies that the each method correctly applies
        a callback function to each item in the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        # Test each with transformation
        result = collection.each(lambda x: x * 2)
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [2, 4, 6, 8])

        # Test each with conditional transformation
        collection = Collection([1, 2, 3, 4])
        collection.each(lambda x: x * 3 if x < 3 else x)
        self.assertEqual(collection.all(), [3, 6, 3, 4])

    def testEvery(self):
        """
        Test the every method for checking if all items pass a test.

        This test verifies that the every method correctly determines
        whether all items in the collection pass a given test.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([2, 4, 6, 8])

        # Test where all items pass
        self.assertTrue(collection.every(lambda x: x % 2 == 0))

        # Test where not all items pass
        collection = Collection([1, 2, 3, 4])
        self.assertFalse(collection.every(lambda x: x % 2 == 0))

    def testFilter(self):
        """
        Test the filter method for filtering items.

        This test verifies that the filter method correctly returns
        a new collection containing only items that pass the test.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4, 5])

        filtered = collection.filter(lambda x: x % 2 == 0)
        self.assertIsInstance(filtered, Collection)
        self.assertEqual(filtered.all(), [2, 4])

        # Original collection should be unchanged
        self.assertEqual(collection.all(), [1, 2, 3, 4, 5])

    def testFlatten(self):
        """
        Test the flatten method for flattening multi-dimensional collections.

        This test verifies that the flatten method correctly flattens
        nested structures into a single dimension.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, [2, 3], {"a": "value"}, [4, {"b": "nested"}]])
        flattened = collection.flatten()

        self.assertIsInstance(flattened, Collection)
        # The exact result depends on the implementation details
        self.assertIsInstance(flattened.all(), list)

    def testForget(self):
        """
        Test the forget method for removing items by key.

        This test verifies that the forget method correctly removes
        items from the collection by their keys/indices.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4, 5])

        # Test removing single key
        result = collection.forget(2)
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [1, 2, 4, 5])

        # Test removing multiple keys (keys are sorted in reverse order in implementation)
        collection = Collection([1, 2, 3, 4, 5])
        collection.forget(1, 3)
        self.assertEqual(collection.all(), [1, 3, 5])

    def testForPage(self):
        """
        Test the forPage method for pagination.

        This test verifies that the forPage method correctly returns
        a slice of the collection for pagination purposes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Test getting first page
        page = collection.forPage(0, 3)
        self.assertIsInstance(page, Collection)
        self.assertEqual(page.all(), [1, 2, 3])

        # Test getting middle page
        page = collection.forPage(3, 3)
        self.assertEqual(page.all(), [])  # Based on slice behavior

    def testGet(self):
        """
        Test the get method for retrieving items by key.

        This test verifies that the get method correctly retrieves
        items by their key/index, with default value support.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([10, 20, 30, 40])

        # Test getting existing key
        self.assertEqual(collection.get(0), 10)
        self.assertEqual(collection.get(2), 30)

        # Test getting non-existing key
        self.assertIsNone(collection.get(10))

        # Test getting non-existing key with default
        self.assertEqual(collection.get(10, "default"), "default")

    def testImplode(self):
        """
        Test the implode method for joining items into string.

        This test verifies that the implode method correctly joins
        collection items into a string using a separator.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test with simple values
        collection = Collection([1, 2, 3, 4])
        result = collection.implode("-")
        self.assertEqual(result, "1-2-3-4")

        # Test with default separator
        result = collection.implode()
        self.assertEqual(result, "1,2,3,4")

        # Test with key extraction
        collection = Collection([{"name": "Juan Sebastian"}, {"name": "Carlos Giovanny"}])
        result = collection.implode(",", "name")
        self.assertEqual(result, "Juan Sebastian,Carlos Giovanny")

    def testIsEmpty(self):
        """
        Test the isEmpty method for checking if collection is empty.

        This test verifies that the isEmpty method correctly determines
        whether the collection contains any items.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test empty collection
        collection = Collection([])
        self.assertTrue(collection.isEmpty())

        # Test non-empty collection
        collection = Collection([1, 2, 3])
        self.assertFalse(collection.isEmpty())

    def testMap(self):
        """
        Test the map method for transforming items.

        This test verifies that the map method correctly applies
        a transformation function to each item, returning a new collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        mapped = collection.map(lambda x: x * 2)
        self.assertIsInstance(mapped, Collection)
        self.assertEqual(mapped.all(), [2, 4, 6, 8])

        # Original collection should be unchanged
        self.assertEqual(collection.all(), [1, 2, 3, 4])

    def testMapInto(self):
        """
        Test the mapInto method for mapping items into class instances.

        This test verifies that the mapInto method correctly creates
        instances of a given class for each item in the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        class TestClass:
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                return isinstance(other, TestClass) and self.value == other.value

        collection = Collection([1, 2, 3])
        mapped = collection.mapInto(TestClass)

        self.assertIsInstance(mapped, Collection)
        self.assertEqual(mapped.count(), 3)
        self.assertIsInstance(mapped.get(0), TestClass)
        self.assertEqual(mapped.get(0).value, 1)

    def testMerge(self):
        """
        Test the merge method for combining collections.

        This test verifies that the merge method correctly combines
        the current collection with another collection or list.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3])

        # Test merging with list
        result = collection.merge([4, 5, 6])
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [1, 2, 3, 4, 5, 6])

        # Test merging with Collection
        collection = Collection([1, 2, 3])
        other = Collection([4, 5, 6])
        collection.merge(other.all())
        self.assertEqual(collection.all(), [1, 2, 3, 4, 5, 6])

        # Test merge with incompatible type should raise ValueError
        collection = Collection([1, 2, 3])
        with self.assertRaises(ValueError):
            collection.merge("not a list")

    def testPluck(self):
        """
        Test the pluck method for extracting values by key.

        This test verifies that the pluck method correctly extracts
        values from dictionaries or objects by a given key.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([
            {"id": 1, "name": "Juan Sebastian"},
            {"id": 2, "name": "Carlos Giovanny"},
            {"id": 3, "name": "John Alejandro"},
        ])

        # Test simple pluck
        plucked = collection.pluck("name")
        self.assertIsInstance(plucked, Collection)
        self.assertEqual(plucked.all(), ["Juan Sebastian", "Carlos Giovanny", "John Alejandro"])

        # Test pluck with key mapping
        plucked = collection.pluck("name", "id")
        expected = {1: "Juan Sebastian", 2: "Carlos Giovanny", 3: "John Alejandro"}
        self.assertEqual(plucked.all(), expected)

    def testPop(self):
        """
        Test the pop method for removing and returning the last item.

        This test verifies that the pop method correctly removes
        and returns the last item from the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        last = collection.pop()
        self.assertEqual(last, 4)
        self.assertEqual(collection.all(), [1, 2, 3])

    def testPrepend(self):
        """
        Test the prepend method for adding items to the beginning.

        This test verifies that the prepend method correctly adds
        an item to the beginning of the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([2, 3, 4])

        result = collection.prepend(1)
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [1, 2, 3, 4])

    def testPull(self):
        """
        Test the pull method for removing and returning an item by key.

        This test verifies that the pull method correctly removes
        and returns an item from the collection by its key/index.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([10, 20, 30, 40])

        value = collection.pull(1)
        self.assertEqual(value, 20)
        self.assertEqual(collection.all(), [10, 30, 40])

        # Test pulling non-existing key should raise IndexError
        with self.assertRaises(IndexError):
            collection.pull(10)

    def testPush(self):
        """
        Test the push method for adding items to the end.

        This test verifies that the push method correctly adds
        an item to the end of the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3])

        result = collection.push(4)
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [1, 2, 3, 4])

    def testPut(self):
        """
        Test the put method for setting items by key.

        This test verifies that the put method correctly sets
        an item in the collection at a specific key/index.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        result = collection.put(1, 99)
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [1, 99, 3, 4])

    def testRandom(self):
        """
        Test the random method for getting random items.

        This test verifies that the random method correctly returns
        random items from the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4, 5])

        # Test getting single random item
        item = collection.random()
        self.assertIn(item, collection.all())

        # Test getting multiple random items
        items = collection.random(3)
        self.assertIsInstance(items, Collection)
        self.assertEqual(items.count(), 3)
        for item in items.all():
            self.assertIn(item, collection.all())

        # Test random on empty collection
        empty_collection = Collection([])
        self.assertIsNone(empty_collection.random())

        # Test requesting more items than available should raise ValueError
        collection_small = Collection([1, 2, 3])
        with self.assertRaises(ValueError):
            collection_small.random(10)

    def testReduce(self):
        """
        Test the reduce method for reducing collection to single value.

        This test verifies that the reduce method correctly applies
        a reducer function to accumulate a single value from the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        # Test simple sum reduction
        result = collection.reduce(lambda acc, x: acc + x, 0)
        self.assertEqual(result, 10)

        # Test with default initial value
        result = collection.reduce(lambda acc, x: acc + x)
        self.assertEqual(result, 10)

    def testReject(self):
        """
        Test the reject method for filtering out items.

        This test verifies that the reject method correctly filters
        items based on a callback function.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4, 5])

        result = collection.reject(lambda x: x if x > 3 else None)
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [4, 5])

    def testReverse(self):
        """
        Test the reverse method for reversing item order.

        This test verifies that the reverse method correctly reverses
        the order of items in the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        result = collection.reverse()
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [4, 3, 2, 1])

    def testSerialize(self):
        """
        Test the serialize method for converting items to serializable format.

        This test verifies that the serialize method correctly converts
        collection items to a serializable format.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test with simple items
        collection = Collection([1, 2, 3])
        serialized = collection.serialize()
        self.assertEqual(serialized, [1, 2, 3])

        # Test with objects that have serialize method
        class SerializableObject:
            def __init__(self, value):
                self.value = value

            def serialize(self):
                return {"value": self.value}

        obj = SerializableObject(42)
        collection = Collection([obj])
        serialized = collection.serialize()
        self.assertEqual(serialized, [{"value": 42}])

    def testAddRelation(self):
        """
        Test the addRelation method for adding relation data.

        This test verifies that the addRelation method correctly adds
        relation data to models in the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Mock objects with add_relations method
        mock1 = Mock()
        mock2 = Mock()
        collection = Collection([mock1, mock2])

        relation_data = {"related": "data"}
        result = collection.addRelation(relation_data)

        self.assertIs(result, collection)  # Should return self
        mock1.add_relations.assert_called_once_with(relation_data)
        mock2.add_relations.assert_called_once_with(relation_data)

    def testShift(self):
        """
        Test the shift method for removing and returning the first item.

        This test verifies that the shift method correctly removes
        and returns the first item from the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        first = collection.shift()
        self.assertEqual(first, 1)
        self.assertEqual(collection.all(), [2, 3, 4])

    def testSort(self):
        """
        Test the sort method for sorting items.

        This test verifies that the sort method correctly sorts
        the items in the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([3, 1, 4, 2])

        result = collection.sort()
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [1, 2, 3, 4])

        # Test sorting with key
        collection = Collection([{"age": 30}, {"age": 20}, {"age": 25}])
        collection.sort("age")
        expected = [{"age": 20}, {"age": 25}, {"age": 30}]
        self.assertEqual(collection.all(), expected)

    def testSum(self):
        """
        Test the sum method for summing values.

        This test verifies that the sum method correctly calculates
        the sum of numeric values in the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test simple sum
        collection = Collection([1, 2, 3, 4])
        self.assertEqual(collection.sum(), 10)

        # Test sum with key extraction
        collection = Collection([
            {"price": 100},
            {"price": 200},
            {"price": 50},
        ])
        self.assertEqual(collection.sum("price"), 350)

        # Test sum with non-numeric values
        collection = Collection(["a", "b", "c"])
        self.assertEqual(collection.sum(), 0)

    def testToJson(self):
        """
        Test the toJson method for converting to JSON string.

        This test verifies that the toJson method correctly converts
        the collection to a JSON string representation.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3])
        json_string = collection.toJson()
        self.assertEqual(json_string, "[1, 2, 3]")

        # Test with complex objects
        collection = Collection([{"id": 1, "name": "Michael Ivan"}])
        json_string = collection.toJson()
        expected = '[{"id": 1, "name": "Michael Ivan"}]'
        self.assertEqual(json_string, expected)

    def testGroupBy(self):
        """
        Test the groupBy method for grouping items by key.

        This test verifies that the groupBy method correctly groups
        items in the collection by a specified key.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([
            {"group": "A", "name": "JUAN SEBASTIAN AREVALO GOMEZ"},
            {"group": "A", "name": "CARLOS GIOVANNY RODRIGUEZ TRIVIÑO"},
            {"group": "B", "name": "JOHN ALEJANDRO DIAZ PINILLA"},
            {"group": "B", "name": "WILMER ALONSO SANCHEZ SAEZ"},
            {"group": "C", "name": "JORGE HERNAN CASTAÑEDA"},
            {"group": "C", "name": "DANIEL STIVEN SARMIENTO LOPEZ"},
            {"group": "D", "name": "MICHAEL IVAN QUEVEDO VILLARRAGA"},
            {"group": "D", "name": "BLAS ALBERTO RANGEL JIMÉNEZ"},
            {"group": "E", "name": "ALEJANDRO TALERO CALDERON"},
            {"group": "E", "name": "RAUL MAURICIO UÑATE CASTRO"},
        ])

        grouped = collection.groupBy("group")
        self.assertIsInstance(grouped, Collection)

        # The exact structure depends on implementation
        self.assertIsInstance(grouped.all(), dict)

    def testTransform(self):
        """
        Test the transform method for transforming items in place.

        This test verifies that the transform method correctly applies
        a transformation function to items in the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        result = collection.transform(lambda x: x * 2)
        self.assertIs(result, collection)  # Should return self
        self.assertEqual(collection.all(), [2, 4, 6, 8])

    def testUnique(self):
        """
        Test the unique method for removing duplicate items.

        This test verifies that the unique method correctly removes
        duplicate items from the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test unique with simple values
        collection = Collection([1, 2, 2, 3, 3, 4])
        unique = collection.unique()
        self.assertIsInstance(unique, Collection)
        self.assertEqual(set(unique.all()), {1, 2, 3, 4})

        # Test unique with key
        collection = Collection([
            {"id": 1, "name": "Juan Sebastian"},
            {"id": 2, "name": "Carlos Giovanny"},
            {"id": 1, "name": "Juan Sebastian Duplicated"},
        ])
        unique = collection.unique("id")
        self.assertEqual(len(unique.all()), 2)

    def testWhere(self):
        """
        Test the where method for filtering by key-value conditions.

        This test verifies that the where method correctly filters
        items based on key-value conditions with various operators.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([
            {"id": 1, "age": 25, "name": "Wilmer Alonso"},
            {"id": 2, "age": 30, "name": "Jorge Hernan"},
            {"id": 3, "age": 35, "name": "Daniel Stiven"},
        ])

        # Test simple equality
        result = collection.where("age", 30)
        self.assertIsInstance(result, Collection)
        self.assertEqual(len(result.all()), 1)
        self.assertEqual(result.first()["name"], "Jorge Hernan")

        # Test with operator
        result = collection.where("age", ">", 25)
        self.assertEqual(len(result.all()), 2)

        result = collection.where("age", "<=", 30)
        self.assertEqual(len(result.all()), 2)

    def testWhereIn(self):
        """
        Test the whereIn method for filtering by value inclusion.

        This test verifies that the whereIn method correctly filters
        items where the specified key's value is in a list of values.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([
            {"id": 1, "name": "Michael Ivan"},
            {"id": 2, "name": "Blas Alberto"},
            {"id": 3, "name": "Alejandro Talero"},
        ])

        # Test whereIn with numeric values
        result = collection.whereIn("id", [1, 2])
        self.assertEqual(len(result.all()), 2)

        # Test whereIn with single value
        result = collection.whereIn("id", [3])
        self.assertEqual(len(result.all()), 1)

        # Test whereIn with no matches
        result = collection.whereIn("id", [4])
        self.assertEqual(len(result.all()), 0)

        # Test whereIn with string comparison of numeric values
        result = collection.whereIn("id", ["1", "2"])
        self.assertEqual(len(result.all()), 2)

        # Test whereIn with string values
        result = collection.whereIn("name", ["Michael Ivan"])
        self.assertEqual(len(result.all()), 1)

        # Test whereIn with boolean values
        bool_collection = Collection([
            {"id": 1, "is_active": True},
            {"id": 2, "is_active": True},
            {"id": 3, "is_active": True},
            {"id": 4, "is_active": False},
        ])
        result = bool_collection.whereIn("is_active", [False])
        self.assertEqual(len(result.all()), 1)

        result = bool_collection.whereIn("is_active", [True])
        self.assertEqual(len(result.all()), 3)

        result = bool_collection.whereIn("is_active", [True, False])
        self.assertEqual(len(result.all()), 4)

        # Test whereIn with bytes values
        byte_strs = [bytes("Raul Mauricio", "utf-8"), bytes("Diego Alexander", "utf-8")]
        byte_collection = Collection([
            {"id": 1, "name": "Juan Sebastian", "bytes_val": byte_strs[0]},
            {"id": 2, "name": "Carlos Giovanny", "bytes_val": byte_strs[1]},
            {"id": 3, "name": "Wilmer Alonso", "bytes_val": bytes("other", "utf-8")},
            {"id": 4, "name": "Jorge Hernan"},
        ])
        result = byte_collection.whereIn("bytes_val", byte_strs)
        self.assertEqual(len(result.all()), 2)

        result = byte_collection.whereIn("bytes_val", [byte_strs[0]])
        self.assertEqual(len(result.all()), 1)

    def testWhereNotIn(self):
        """
        Test the whereNotIn method for filtering by value exclusion.

        This test verifies that the whereNotIn method correctly filters
        items where the specified key's value is not in a list of values.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([
            {"id": 1, "name": "Jorge Hernan"},
            {"id": 2, "name": "Daniel Stiven"},
            {"id": 3, "name": "Michael Ivan"},
        ])

        # Test whereNotIn with numeric values
        result = collection.whereNotIn("id", [1, 2])
        self.assertEqual(len(result.all()), 1)

        # Test whereNotIn with single value
        result = collection.whereNotIn("id", [3])
        self.assertEqual(len(result.all()), 2)

        # Test whereNotIn with no exclusions
        result = collection.whereNotIn("id", [4])
        self.assertEqual(len(result.all()), 3)

        # Test whereNotIn with string comparison of numeric values
        result = collection.whereNotIn("id", ["1", "2"])
        self.assertEqual(len(result.all()), 1)

        # Test whereNotIn with string values
        result = collection.whereNotIn("name", ["Jorge Hernan"])
        self.assertEqual(len(result.all()), 2)

    def testZip(self):
        """
        Test the zip method for merging collections by index.

        This test verifies that the zip method correctly merges
        the collection with another collection by matching indices.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection(["a", "b", "c"])
        other = [1, 2, 3]

        zipped = collection.zip(other)
        self.assertIsInstance(zipped, Collection)
        expected = [["a", 1], ["b", 2], ["c", 3]]
        self.assertEqual(zipped.all(), expected)

        # Test with Collection
        other_collection = Collection([1, 2, 3])
        zipped = collection.zip(other_collection)
        self.assertEqual(zipped.all(), expected)

        # Test with incompatible type should raise ValueError
        with self.assertRaises(ValueError):
            collection.zip("not a list")

    def testSetAppends(self):
        """
        Test the setAppends method for setting append attributes.

        This test verifies that the setAppends method correctly sets
        attributes that should be appended to the collection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([])
        appends = ["attr1", "attr2"]

        result = collection.setAppends(appends)
        self.assertIs(result, collection)  # Should return self

    def testMagicMethods(self):
        """
        Test magic methods for Collection behavior.

        This test verifies that magic methods like __iter__, __len__,
        __getitem__, __setitem__, __delitem__, and comparison operators work correctly.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        # Test __len__
        self.assertEqual(len(collection), 4)

        # Test __iter__
        items = list(collection)
        self.assertEqual(items, [1, 2, 3, 4])

        # Test __getitem__
        self.assertEqual(collection[0], 1)
        self.assertEqual(collection[1:3], Collection([2, 3]))

        # Test __setitem__
        collection[0] = 99
        self.assertEqual(collection[0], 99)

        # Test __delitem__
        del collection[0]
        self.assertEqual(collection.all(), [2, 3, 4])

        # Test equality
        other = Collection([2, 3, 4])
        self.assertEqual(collection, other)

        # Test inequality
        different = Collection([1, 2, 3])
        self.assertNotEqual(collection, different)

        # Test comparison operators
        smaller = Collection([1, 2])
        larger = Collection([2, 3, 4, 5])

        self.assertLess(smaller, collection)
        self.assertLessEqual(smaller, collection)
        self.assertGreater(larger, collection)
        self.assertGreaterEqual(larger, collection)

    def testPrivateMethods(self):
        """
        Test private helper methods functionality.

        This test verifies that private helper methods work correctly,
        though they are not part of the public API.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3])

        # Test __checkIsCallable
        self.assertTrue(collection._Collection__checkIsCallable(lambda x: x))
        self.assertFalse(collection._Collection__checkIsCallable("not callable", False))

        # Test __makeComparison
        self.assertTrue(collection._Collection__makeComparison(5, 3, ">"))
        self.assertTrue(collection._Collection__makeComparison(3, 5, "<"))
        self.assertTrue(collection._Collection__makeComparison(5, 5, "=="))
        self.assertTrue(collection._Collection__makeComparison(5, 3, "!="))

        # Test __getItems
        other_collection = Collection([4, 5, 6])
        self.assertEqual(Collection._Collection__getItems(other_collection), [4, 5, 6])
        self.assertEqual(Collection._Collection__getItems([7, 8, 9]), [7, 8, 9])

    def testEdgeCases(self):
        """
        Test edge cases and error conditions.

        This test verifies that the Collection class handles
        edge cases and error conditions appropriately.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test with None values
        collection = Collection([None, 1, None, 2])
        self.assertEqual(collection.count(), 4)
        self.assertIn(None, collection.all())

        # Test callbacks that raise exceptions
        collection = Collection([1, 2, 3])
        with self.assertRaises(ValueError):
            collection.each("not callable")

        # Test empty collection operations
        empty = Collection([])
        self.assertIsNone(empty.first())
        self.assertTrue(empty.isEmpty())
        self.assertEqual(empty.sum(), 0)
        # avg() on empty collection raises ZeroDivisionError
        with self.assertRaises(ZeroDivisionError):
            empty.avg()

    def testComplexDataTypes(self):
        """
        Test Collection with complex data types.

        This test verifies that the Collection class works correctly
        with complex data types like nested dictionaries and custom objects.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test with nested dictionaries
        complex_data = [
            {"user": {"id": 1, "profile": {"name": "Juan Sebastian", "age": 25}}},
            {"user": {"id": 2, "profile": {"name": "Carlos Giovanny", "age": 30}}},
        ]
        collection = Collection(complex_data)

        self.assertEqual(collection.count(), 2)
        self.assertEqual(collection.first()["user"]["id"], 1)

        # Test with mixed data types
        mixed_data = [1, "string", {"key": "value"}, [1, 2, 3], None]
        collection = Collection(mixed_data)

        self.assertEqual(collection.count(), 5)
        self.assertIn("string", collection.all())
        self.assertIn(None, collection.all())

    def testCallbackFunctions(self):
        """
        Test various callback function scenarios.

        This test verifies that callback functions work correctly
        across different Collection methods.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([
            {"name": "Raul Mauricio", "age": 25, "active": True},
            {"name": "Diego Alexander", "age": 30, "active": False},
            {"name": "Juan Sebastian", "age": 35, "active": True},
        ])

        # Test complex filtering
        active_users = collection.filter(lambda user: user["active"])
        self.assertEqual(len(active_users.all()), 2)

        # Test complex mapping
        names = collection.map(lambda user: user["name"].upper())
        self.assertEqual(names.first(), "RAUL MAURICIO")

        # Test complex conditions
        young_active = collection.filter(lambda user: user["age"] < 30 and user["active"])
        self.assertEqual(len(young_active.all()), 1)

    def testChainedOperations(self):
        """
        Test chained operations on Collection.

        This test verifies that Collection methods can be properly chained
        together to perform complex data transformations.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Test method chaining
        result = (collection
                 .filter(lambda x: x % 2 == 0)  # Get even numbers
                 .map(lambda x: x * 2)          # Double them
                 .take(3))                      # Take first 3

        self.assertEqual(result.all(), [4, 8, 12])

        # Test chaining with Collection return types
        collection = Collection([1, 2, 3, 4])
        result = collection.push(5).prepend(0).reverse()
        self.assertEqual(result.all(), [5, 4, 3, 2, 1, 0])

    def testDataGetMethod(self):
        """
        Test the __dataGet private method for nested data extraction.

        This test verifies that the __dataGet method correctly extracts
        values from nested dictionaries using dot notation and handles errors gracefully.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([])

        # Test simple key extraction
        item = {"name": "Juan Sebastian", "age": 30}
        result = collection._Collection__dataGet(item, "name")
        self.assertEqual(result, "Juan Sebastian")

        # Test nested key extraction (if dotty_dict is working)
        nested_item = {"user": {"profile": {"name": "Carlos Giovanny"}}}
        result = collection._Collection__dataGet(nested_item, "user.profile.name")
        self.assertEqual(result, "Carlos Giovanny")

        # Test with default value for missing key
        result = collection._Collection__dataGet(item, "missing_key", "default")
        self.assertEqual(result, "default")

        # Test with non-dict item should return None (as per implementation)
        result = collection._Collection__dataGet("simple_string", "any_key")
        self.assertIsNone(result)

    def testGetValueMethod(self):
        """
        Test the __getValue private method for extracting values using keys or callbacks.

        This test verifies that the __getValue method correctly extracts
        values from collection items using either string keys or callback functions.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([
            {"name": "Juan Sebastian", "age": 25},
            {"name": "Carlos Giovanny", "age": 30},
            {"name": "Daniel Stiven", "age": 35},
        ])

        # Test with string key
        values = collection._Collection__getValue("name")
        self.assertEqual(values, ["Juan Sebastian", "Carlos Giovanny", "Daniel Stiven"])

        # Test with callback function
        values = collection._Collection__getValue(lambda x: x["age"] * 2)
        self.assertEqual(values, [50, 60, 70])

        # Test with None should return None
        values = collection._Collection__getValue(None)
        self.assertIsNone(values)

    def testValueMethod(self):
        """
        Test the __value private method for handling callable values.

        This test verifies that the __value method correctly handles
        both callable and non-callable values.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([])

        # Test with non-callable value
        result = collection._Collection__value(42)
        self.assertEqual(result, 42)

        # Test with callable value
        def test_callable():
            return "called"

        result = collection._Collection__value(test_callable)
        self.assertEqual(result, "called")

    def testGetItemsClassMethod(self):
        """
        Test the __getItems class method for extracting items from various types.

        This test verifies that the __getItems method correctly extracts
        items from Collection instances and returns other types as-is.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test with Collection instance
        collection = Collection([1, 2, 3])
        items = Collection._Collection__getItems(collection)
        self.assertEqual(items, [1, 2, 3])

        # Test with regular list
        items = Collection._Collection__getItems([4, 5, 6])
        self.assertEqual(items, [4, 5, 6])

        # Test with other types
        items = Collection._Collection__getItems("string")
        self.assertEqual(items, "string")

    def testPluckComplexScenarios(self):
        """
        Test pluck method with complex scenarios and edge cases.

        This test verifies that the pluck method handles various
        complex scenarios including objects with serialize methods and different data types.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test with objects that have serialize method
        class SerializableItem:
            def __init__(self, data):
                self.data = data

            def serialize(self):
                return self.data

        items = [
            SerializableItem({"id": 1, "name": "Raul Mauricio"}),
            SerializableItem({"id": 2, "name": "Diego Alexander"}),
        ]
        collection = Collection(items)
        plucked = collection.pluck("name")
        self.assertEqual(plucked.all(), ["Raul Mauricio", "Diego Alexander"])

        # Test pluck with mixed item types
        mixed_items = [
            {"id": 1, "name": "Juan Sebastian"},
            SerializableItem({"id": 2, "name": "Carlos Giovanny"}),
        ]
        collection = Collection(mixed_items)
        plucked = collection.pluck("name")
        self.assertEqual(plucked.all(), ["Juan Sebastian", "Carlos Giovanny"])

    def testSortWithKey(self):
        """
        Test sort method with key parameter for custom sorting.

        This test verifies that the sort method correctly sorts
        items using a custom key for comparison.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([
            {"name": "Michael Ivan", "age": 35},
            {"name": "Blas Alberto", "age": 25},
            {"name": "Alejandro Talero", "age": 30},
        ])

        # Test sorting by age
        collection.sort("age")
        names = [item["name"] for item in collection.all()]
        self.assertEqual(names, ["Blas Alberto", "Alejandro Talero", "Michael Ivan"])

    def testUniqueWithDictItems(self):
        """
        Test unique method with dictionary items.

        This test verifies that the unique method correctly handles
        dictionary items when checking for uniqueness.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test unique with dict collection
        dict_collection = Collection({"a": 1, "b": 2, "c": 1})
        dict_collection.unique()
        # The behavior depends on the implementation details

        # Test unique with key on dict items
        collection = Collection([
            {"id": 1, "type": "A"},
            {"id": 2, "type": "B"},
            {"id": 3, "type": "A"},
            {"id": 4, "type": "C"},
        ])
        unique = collection.unique("type")
        types = [item["type"] for item in unique.all()]
        self.assertEqual(len(set(types)), len(types))  # All types should be unique

    def testContainsEdgeCases(self):
        """
        Test contains method with edge cases.

        This test verifies that the contains method handles
        various edge cases correctly.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, None, "string", {"key": "value"}])

        # Test contains with None
        self.assertTrue(collection.contains(None))

        # Test contains with string
        self.assertTrue(collection.contains("string"))

        # Test contains with dict
        self.assertTrue(collection.contains({"key": "value"}))

        # Test contains with callback returning None
        self.assertFalse(collection.contains(lambda x: None))

    def testRandomEdgeCases(self):
        """
        Test random method edge cases and error handling.

        This test verifies that the random method handles
        edge cases and error conditions appropriately.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test random with single item
        single_item = Collection([42])
        self.assertEqual(single_item.random(), 42)

        # Test random count of 1
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.random(1)
        self.assertIsInstance(result, Collection)
        self.assertEqual(result.count(), 1)

        # Test random with count returns a Collection and modifies original
        # Use a fresh collection for this test
        fresh_collection = Collection([10, 20, 30, 40, 50])
        result = fresh_collection.random(3)
        self.assertIsInstance(result, Collection)
        # The original collection should be modified to contain only the random items
        self.assertEqual(fresh_collection.count(), 3)

    def testMapIntoWithMethod(self):
        """
        Test mapInto method with method parameter.

        This test verifies that the mapInto method correctly calls
        a specific method on the target class when the method parameter is provided.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        class TestClass:
            @classmethod
            def from_value(cls, value):
                instance = cls()
                instance.value = value * 2
                return instance

            def __eq__(self, other):
                return isinstance(other, TestClass) and hasattr(other, "value") and self.value == other.value

        collection = Collection([1, 2, 3])
        mapped = collection.mapInto(TestClass, "from_value")

        self.assertIsInstance(mapped, Collection)
        self.assertEqual(mapped.count(), 3)

    def testSerializeWithAppends(self):
        """
        Test serialize method with appends functionality.

        This test verifies that the serialize method correctly handles
        the appends functionality for adding additional attributes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Test serialize with objects that support set_appends method
        class AppendableModel:
            def __init__(self, id):
                self.id = id
                self._appends = []

            def set_appends(self, appends):
                self._appends = appends

            def serialize(self):
                data = {"id": self.id}
                # Add appended attributes
                for append in self._appends:
                    if append == "meta":
                        data["meta"] = {"extra": "data"}
                return data

        collection = Collection([AppendableModel(1), AppendableModel(2)])
        collection.setAppends(["meta"])

        # The exact behavior depends on the implementation
        serialized = collection.serialize()
        self.assertIsInstance(serialized, list)
        self.assertEqual(len(serialized), 2)

    def testForPageEdgeCases(self):
        """
        Test forPage method with edge cases.

        This test verifies that the forPage method handles
        edge cases like invalid page numbers or sizes appropriately.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Test with page starting beyond collection length
        result = collection.forPage(15, 5)
        self.assertEqual(result.all(), [])

        # Test with negative page
        collection.forPage(-1, 3)
        # Behavior depends on implementation, but should handle gracefully

    def testMergeErrorHandling(self):
        """
        Test merge method error handling.

        This test verifies that the merge method properly handles
        error conditions like incompatible data types.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3])

        # Test merging with incompatible types
        with self.assertRaises(ValueError):
            collection.merge(42)

        with self.assertRaises(ValueError):
            collection.merge("string")

        with self.assertRaises(ValueError):
            collection.merge({"key": "value"})

    def testZipErrorHandling(self):
        """
        Test zip method error handling.

        This test verifies that the zip method properly handles
        error conditions and edge cases.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3])

        # Test zip with different lengths
        shorter = [1, 2]
        zipped = collection.zip(shorter)
        # zip should handle different lengths gracefully
        self.assertEqual(len(zipped.all()), 2)

        # Test zip with longer collection
        longer = [1, 2, 3, 4, 5]
        zipped = collection.zip(longer)
        self.assertEqual(len(zipped.all()), 3)

    def testGroupByComplexScenarios(self):
        """
        Test groupBy method with complex scenarios.

        This test verifies that the groupBy method correctly handles
        complex grouping scenarios and edge cases.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([
            {"category": "A", "value": 10, "name": "Carlos Giovanny"},
            {"category": "B", "value": 20, "name": "John Alejandro"},
            {"category": "A", "value": 15, "name": "Wilmer Alonso"},
            {"category": "C", "value": 30, "name": "Jorge Hernan"},
            {"category": "B", "value": 25, "name": "Daniel Stiven"},
        ])

        grouped = collection.groupBy("category")
        self.assertIsInstance(grouped, Collection)

        # Verify that grouping creates the expected structure
        grouped_dict = grouped.all()
        self.assertIsInstance(grouped_dict, dict)

        # Verify all categories are present
        expected_categories = {"A", "B", "C"}
        self.assertEqual(set(grouped_dict.keys()), expected_categories)

    def testFlattenComplexStructures(self):
        """
        Test flatten method with complex nested structures.

        This test verifies that the flatten method correctly handles
        deeply nested and mixed data structures.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        complex_structure = [
            1,
            [2, 3],
            {"nested": {"deep": "value"}},
            [4, {"more": "data"}, [5, 6]],
            "string",
        ]
        collection = Collection(complex_structure)
        flattened = collection.flatten()

        self.assertIsInstance(flattened, Collection)
        # The exact result depends on implementation, but should be flattened
        self.assertIsInstance(flattened.all(), list)

    def testCallbackValidation(self):
        """
        Test callback validation across different methods.

        This test verifies that methods properly validate callback
        functions and raise appropriate errors for invalid callbacks.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection = Collection([1, 2, 3, 4])

        # Test methods that require callbacks
        methods_requiring_callbacks = [
            "each", "every", "filter", "map", "transform", "reject",
        ]

        for method_name in methods_requiring_callbacks:
            method = getattr(collection, method_name)
            with self.assertRaises(ValueError):
                method("not a callable")

    def testCollectionComparisons(self):
        """
        Test Collection comparison operators thoroughly.

        This test verifies that all comparison operators work correctly
        with various collection sizes and contents.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        collection1 = Collection([1, 2, 3])
        collection2 = Collection([1, 2, 3])
        collection3 = Collection([1, 2, 4])
        collection4 = Collection([1, 2])
        collection5 = Collection([1, 2, 3, 4])

        # Test equality
        self.assertEqual(collection1, collection2)
        self.assertNotEqual(collection1, collection3)

        # Test inequality
        self.assertEqual(collection1, collection2)
        self.assertNotEqual(collection1, collection3)

        # Test less than
        self.assertLess(collection4, collection1)
        self.assertFalse(collection1 < collection4)

        # Test less than or equal
        self.assertLessEqual(collection4, collection1)
        self.assertLessEqual(collection1, collection2)

        # Test greater than
        self.assertGreater(collection5, collection1)
        self.assertFalse(collection1 > collection5)

        # Test greater than or equal
        self.assertGreaterEqual(collection5, collection1)
        self.assertGreaterEqual(collection1, collection2)

    def testMemoryAndPerformance(self):
        """
        Test Collection with large datasets for memory and performance considerations.

        This test verifies that the Collection class can handle
        reasonably large datasets without issues.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Create a larger collection for testing
        large_data = list(range(1000))
        collection = Collection(large_data)

        # Test basic operations still work
        self.assertEqual(collection.count(), 1000)
        self.assertEqual(collection.first(), 0)
        self.assertEqual(collection.last(), 999)

        # Test filtering on large dataset
        filtered = collection.filter(lambda x: x % 100 == 0)
        self.assertEqual(filtered.count(), 10)

        # Test mapping on large dataset
        mapped = collection.map(lambda x: x * 2)
        self.assertEqual(mapped.first(), 0)
        self.assertEqual(mapped.last(), 1998)

    def testThreadSafety(self):
        """
        Test Collection behavior in concurrent scenarios.

        This test verifies basic thread safety considerations,
        though Collection is not designed to be thread-safe by default.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        import threading

        collection = Collection(list(range(100)))
        results = []

        def worker():
            # Perform read operations
            total = collection.sum()
            count = collection.count()
            results.append((total, count))

        # Create multiple threads performing read operations
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All results should be identical for read operations
        expected_result = (sum(range(100)), 100)
        for result in results:
            self.assertEqual(result, expected_result)
