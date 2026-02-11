from unittest import skip
from orionis.test.cases.case import TestCase
from orionis.services.file.contracts.directory import IDirectory

class Prueba(TestCase):

    async def testProcess(self, directory: IDirectory):
        self.assertEqual(1, 12)

    def testSyncMethod(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod2(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod3(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod4(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod5(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod6(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod7(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod8(self, directory: IDirectory):
        self.assertEqual(1, 1)

    @skip("Skipping this test method for demonstration purposes.")
    def testSyncMethod9(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod10(self, directory: IDirectory):
        self.assertEqual(1, 1)

    @skip("Skipping this test method for demonstration purposes.")
    def testSyncMethod11(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod12(self, directory: IDirectory):
        self.assertEqual(1, 2)

    def testSyncMethod13(self, directory: IDirectory):
        raise RuntimeError("This is a test error to demonstrate ...")

    def testSyncMethod14(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod15(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod16(self, directory: IDirectory):
        self.assertEqual(1, 1)

    def testSyncMethod17(self, directory: IDirectory):
        self.assertEqual(1, 1)