from unittest import skip
from orionis import IApplication
from orionis.test.cases.case import TestCase
from orionis.services.file.contracts.directory import IDirectory

class Prueba(TestCase):

    async def testAsyncMethod(
        self,
        app: IApplication,
        directory: IDirectory,
    ) -> None:
        """
        Verify that the application's root path matches the directory's root.

        Parameters
        ----------
        app : IApplication
            The application instance to test.
        directory : IDirectory
            The directory service to compare.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Assert that the root path from app and directory are equal.
        self.assertEqual(app.path('root'), directory.root())

    def testSyncMethod(
        self,
        app: IApplication,
        directory: IDirectory,
    ) -> None:
        """
        Verify that the application's root path matches the directory's root.

        Parameters
        ----------
        app : IApplication
            The application instance to test.
        directory : IDirectory
            The directory service to compare.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Assert that the root path from app and directory are equal.
        self.assertEqual(app.path('root'), directory.root())
