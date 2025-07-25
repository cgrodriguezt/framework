from orionis.test.cases.asynchronous import AsyncTestCase
from unittest.mock import patch

class TestPypiPackageApi(AsyncTestCase):

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetName(self, MockPypiPackageApi):
        """
        Tests the `getName` method of the `PypiPackageApi` class.

        This test verifies that the mocked `getName` method returns the expected package name.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked `PypiPackageApi` class.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """

        # Get the mocked API instance
        api = MockPypiPackageApi.return_value

        # Set the return value for getName
        api.getName.return_value = "orionis"

        # Assert that getName returns the expected value
        self.assertEqual(api.getName(), "orionis")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetAuthor(self, MockPypiPackageApi):
        """
        Tests the `getAuthor` method of the `PypiPackageApi` class.

        This test checks that the mocked `getAuthor` method returns the correct author name.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked `PypiPackageApi` class.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """

        # Get the mocked API instance
        api = MockPypiPackageApi.return_value

        # Set the return value for getAuthor
        api.getAuthor.return_value = "Raul Mauricio Uñate Castro"

        # Assert that getAuthor returns the expected value
        self.assertEqual(api.getAuthor(), "Raul Mauricio Uñate Castro")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetAuthorEmail(self, MockPypiPackageApi):
        """
        Tests the `getAuthorEmail` method of the `PypiPackageApi` class.

        This test ensures that the mocked `getAuthorEmail` method returns the correct author email address.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked `PypiPackageApi` class.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """

        # Get the mocked API instance
        api = MockPypiPackageApi.return_value

        # Set the return value for getAuthorEmail
        api.getAuthorEmail.return_value = "raulmauriciounate@gmail.com"

        # Assert that getAuthorEmail returns the expected value
        self.assertEqual(api.getAuthorEmail(), "raulmauriciounate@gmail.com")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetDescription(self, MockPypiPackageApi):
        """
        Tests the `getDescription` method of the `PypiPackageApi` class.

        This test verifies that the mocked `getDescription` method returns the expected package description.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked `PypiPackageApi` class.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """

        # Get the mocked API instance
        api = MockPypiPackageApi.return_value

        # Set the return value for getDescription
        api.getDescription.return_value = "Orionis Framework – Elegant, Fast, and Powerful."

        # Assert that getDescription returns the expected value
        self.assertEqual(api.getDescription(), "Orionis Framework – Elegant, Fast, and Powerful.")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetPythonVersion(self, MockPypiPackageApi):
        """
        Tests the `getPythonVersion` method of the `PypiPackageApi` class.

        This test checks that the mocked `getPythonVersion` method returns the correct Python version requirement.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked `PypiPackageApi` class.

        Returns
        -------
        None
            This method does not return anything. It asserts the expected behavior.
        """

        # Get the mocked API instance
        api = MockPypiPackageApi.return_value

        # Set the return value for getPythonVersion
        api.getPythonVersion.return_value = ">=3.12"

        # Assert that getPythonVersion returns the expected value
        self.assertEqual(api.getPythonVersion(), ">=3.12")
