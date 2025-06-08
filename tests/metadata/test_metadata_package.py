from orionis.unittesting import TestCase
from orionis.metadata.package import PypiPackageApi

class TestPypiPackageApi(TestCase):

    async def testGetName(self):
        """
        Test getName method.

        Tests that getName returns the correct package name.

        Returns
        -------
        None
        """
        api = PypiPackageApi()
        self.assertEqual(api.getName(), "orionis")

    async def testGetAuthor(self):
        """
        Test getAuthor method.

        Tests that getAuthor returns the correct author name.

        Returns
        -------
        None
        """
        api = PypiPackageApi()
        self.assertEqual(api.getAuthor(), "Raul Mauricio Uñate Castro")

    async def testGetAuthorEmail(self):
        """
        Test getAuthorEmail method.

        Tests that getAuthorEmail returns the correct author email.

        Returns
        -------
        None
        """
        api = PypiPackageApi()
        self.assertEqual(api.getAuthorEmail(), "raulmauriciounate@gmail.com")

    async def testGetDescription(self):
        """
        Test getDescription method.

        Tests that getDescription returns the correct description.

        Returns
        -------
        None
        """
        api = PypiPackageApi()
        self.assertEqual(api.getDescription(), "Orionis Framework – Elegant, Fast, and Powerful.")

    async def testGetPythonVersion(self):
        """
        Test getPythonVersion method.

        Tests that getPythonVersion returns the correct required Python version.

        Returns
        -------
        None
        """
        api = PypiPackageApi()
        self.assertEqual(api.getPythonVersion(), ">=3.12")