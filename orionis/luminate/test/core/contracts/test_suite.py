from abc import ABC, abstractmethod
from orionis.luminate.config.entities.testing import Testing
from orionis.luminate.test.core.test_unit import UnitTest

class ITestSuite(ABC):
    """
    Interface for configuring and initializing a UnitTest suite using a provided Testing configuration.
    Methods:
        config(config: Testing) -> UnitTest:
    """

    @staticmethod
    @abstractmethod
    def config(config:Testing) -> UnitTest:
        """
        Configures and initializes a UnitTest suite based on the provided Testing configuration.
        Args:
            config (Testing): An instance of the Testing class containing configuration options for the test suite.
        Returns:
            UnitTest: An initialized UnitTest suite configured according to the provided settings.
        Raises:
            OrionisTestConfigException: If the config parameter is not an instance of the Testing class.
        The function performs the following steps:
            - Validates the type of the config parameter.
            - Initializes a UnitTest suite and applies configuration values from the Testing instance.
            - Discovers folders containing test files based on the specified base path, folder path(s), and filename pattern.
            - Adds discovered test folders to the UnitTest suite, applying optional test name patterns and tags.
            - Returns the configured UnitTest suite ready for execution.
        """
        pass
