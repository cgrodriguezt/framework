from orionis.luminate.support.standard.std import StdClass
from orionis.luminate.test.test_case import TestCase

class TestStdClass(TestCase):

    def testInitializationAndAccess(self):
        obj = StdClass(name='Raul', age=30)
        self.assertEqual(obj.name, 'Raul')
        self.assertEqual(obj.age, 30)

    def testToDictReturnsCorrectData(self):
        obj = StdClass(a=1, b=2)
        expected = {'a': 1, 'b': 2}
        self.assertEqual(obj.toDict(), expected)

    def testUpdateAttributes(self):
        obj = StdClass()
        obj.update(foo='bar', number=42)
        self.assertEqual(obj.foo, 'bar')
        self.assertEqual(obj.number, 42)

    def testUpdateReservedAttributeRaisesError(self):
        obj = StdClass()
        with self.assertRaises(ValueError):
            obj.update(__init__='bad')

    def testUpdateConflictingAttributeRaisesError(self):
        obj = StdClass()
        with self.assertRaises(ValueError):
            obj.update(toDict='oops')

    def testRemoveExistingAttributes(self):
        obj = StdClass(x=1, y=2)
        obj.remove('x')
        self.assertFalse(hasattr(obj, 'x'))
        self.assertTrue(hasattr(obj, 'y'))

    def testRemoveNonExistingAttributeRaisesError(self):
        obj = StdClass()
        with self.assertRaises(AttributeError):
            obj.remove('not_there')

    def testFromDictCreatesEquivalentInstance(self):
        data = {'a': 10, 'b': 20}
        obj = StdClass.from_dict(data)
        self.assertEqual(obj.toDict(), data)

    def testReprAndStr(self):
        obj = StdClass(x=5)
        self.assertIn("StdClass", repr(obj))
        self.assertIn("'x': 5", str(obj))

    def testEquality(self):
        a = StdClass(x=1, y=2)
        b = StdClass(x=1, y=2)
        c = StdClass(x=3)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)