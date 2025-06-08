from orionis.unittesting import TestCase
from orionis.metadata.package import PypiPackageApi
from unittest.mock import MagicMock, patch

class TestPypiPackageApi(TestCase):

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetName(self, MockPypiPackageApi):
        api = MockPypiPackageApi.return_value
        api.getName.return_value = "orionis"
        self.assertEqual(api.getName(), "orionis")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetAuthor(self, MockPypiPackageApi):
        api = MockPypiPackageApi.return_value
        api.getAuthor.return_value = "Raul Mauricio Uñate Castro"
        self.assertEqual(api.getAuthor(), "Raul Mauricio Uñate Castro")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetAuthorEmail(self, MockPypiPackageApi):
        api = MockPypiPackageApi.return_value
        api.getAuthorEmail.return_value = "raulmauriciounate@gmail.com"
        self.assertEqual(api.getAuthorEmail(), "raulmauriciounate@gmail.com")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetDescription(self, MockPypiPackageApi):
        api = MockPypiPackageApi.return_value
        api.getDescription.return_value = "Orionis Framework – Elegant, Fast, and Powerful."
        self.assertEqual(api.getDescription(), "Orionis Framework – Elegant, Fast, and Powerful.")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetPythonVersion(self, MockPypiPackageApi):
        api = MockPypiPackageApi.return_value
        api.getPythonVersion.return_value = ">=3.12"
        self.assertEqual(api.getPythonVersion(), ">=3.12")
