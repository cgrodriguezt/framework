from abc import ABC, abstractmethod
from orionis.luminate.config.entities.testing import Testing
from orionis.luminate.test.core.test_unit import UnitTest

class ITestSuite(ABC):
    """
    Provides utility methods to configure and execute unit tests from specified folders.
    """

    @staticmethod
    @abstractmethod
    def config(config:Testing) -> UnitTest:
        """
            Configures and initializes a test suite based on the provided configuration.
            Args:
                config (Testing): An instance of the `Testing` class containing configuration
                                  parameters for the test suite.
            Returns:
                UnitTest: An initialized test suite configured with the provided settings.
            Raises:
                OrionisTestConfigException: If the `config` parameter is not an instance of
                                            the `Testing` class.
            The function performs the following steps:
            1. Validates that the `config` parameter is an instance of the `Testing` class.
            2. Initializes a `UnitTest` object and assigns configuration values to it.
            3. Extracts configuration values such as `base_path`, `folder_path`, and `pattern`.
            4. Discovers folders matching the specified `folder_path` and `pattern`:
               - If `folder_path` is '*', all matching folders in the `base_path` are discovered.
               - If `folder_path` is a list, matching folders in each path are discovered.
               - Otherwise, matching folders in the specified `folder_path` are discovered.
            5. Adds discovered folders to the test suite by calling `discoverTestsInFolder`.
            Notes:
                - The `list_matching_folders` helper function is used to find folders matching
                  the specified pattern.
                - The `pattern` supports wildcard characters (`*` and `?`) for flexible matching.
                - The `test_name_pattern` and `tags` from the `config` are used when adding
                  folders to the test suite.
        """
        pass
