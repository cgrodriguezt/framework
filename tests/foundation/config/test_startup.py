from orionis.test import TestCase
from orionis.foundation.config.startup import Configuration
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.auth.entities.auth import Auth
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.http.entitites.http import HTTP
from orionis.foundation.config.database.entities.database import Database
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.queue.entities.queue import Queue
from orionis.foundation.config.session.entities.session import Session
from orionis.foundation.config.testing.entities.testing import Testing

# ===========================================================================
# Configuration (startup) entity
# ===========================================================================

class TestConfigurationEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Configuration can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Configuration()
        self.assertIsInstance(c, Configuration)

    def testDefaultAppIsAppInstance(self) -> None:
        """
        Test that the app attribute defaults to an App instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().app, App)

    def testDefaultAuthIsAuthInstance(self) -> None:
        """
        Test that the auth attribute defaults to an Auth instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().auth, Auth)

    def testDefaultCacheIsCacheInstance(self) -> None:
        """
        Test that the cache attribute defaults to a Cache instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().cache, Cache)

    def testDefaultHttpIsHttpInstance(self) -> None:
        """
        Test that the http attribute defaults to an HTTP instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().http, HTTP)

    def testDefaultDatabaseIsDatabaseInstance(self) -> None:
        """
        Test that the database attribute defaults to a Database instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().database, Database)

    def testDefaultFilesystemsIsFilesystemsInstance(self) -> None:
        """
        Test that the filesystems attribute defaults to a Filesystems instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().filesystems, Filesystems)

    def testDefaultLoggingIsLoggingInstance(self) -> None:
        """
        Test that the logging attribute defaults to a Logging instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().logging, Logging)

    def testDefaultMailIsMailInstance(self) -> None:
        """
        Test that the mail attribute defaults to a Mail instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().mail, Mail)

    def testDefaultQueueIsQueueInstance(self) -> None:
        """
        Test that the queue attribute defaults to a Queue instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().queue, Queue)

    def testDefaultSessionIsSessionInstance(self) -> None:
        """
        Test that the session attribute defaults to a Session instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().session, Session)

    def testDefaultTestingIsTestingInstance(self) -> None:
        """
        Test that the testing attribute defaults to a Testing instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Configuration().testing, Testing)

    def testAppDictConversion(self) -> None:
        """
        Test that passing a dict for app is converted to an App instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Configuration(app={})
        self.assertIsInstance(c.app, App)

    def testAuthDictConversion(self) -> None:
        """
        Test that passing a dict for auth is converted to an Auth instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Configuration(auth={})
        self.assertIsInstance(c.auth, Auth)

    def testCacheDictConversion(self) -> None:
        """
        Test that passing a dict for cache is converted to a Cache instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Configuration(cache={})
        self.assertIsInstance(c.cache, Cache)

    def testHttpDictConversion(self) -> None:
        """
        Test that passing a dict for http is converted to an HTTP instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Configuration(http={})
        self.assertIsInstance(c.http, HTTP)

    def testInvalidAppTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for app raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Configuration(app="invalid")  # type: ignore[arg-type]

    def testInvalidMailTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for mail raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Configuration(mail=123)  # type: ignore[arg-type]

    def testInvalidCacheTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for cache raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Configuration(cache=42)  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Configuration instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        c = Configuration()
        with self.assertRaises(FrozenInstanceError):
            c.app = App()  # type: ignore[misc]
