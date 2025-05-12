import re
from os import walk
from orionis.luminate.config.entities.testing import Testing
from orionis.luminate.test.core.contracts.test_suite import ITestSuite
from orionis.luminate.test.core.test_unit import UnitTest
from orionis.luminate.test.exceptions.test_config_exception import OrionisTestConfigException

class TestSuite(ITestSuite):

    @staticmethod
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

        # Check if the config is an instance of Testing
        if not isinstance(config, Testing):
            raise OrionisTestConfigException("The config parameter must be an instance of the Testing class.")

        # Initialize the test suite
        tests = UnitTest()

        # Assign config values to the test suite
        tests.configure(
            verbosity=config.verbosity,
            execution_mode=config.execution_mode,
            max_workers=config.max_workers,
            fail_fast=config.fail_fast,
            print_result=config.print_result,
            throw_exception=config.throw_exception
        )

        # Extract configuration values
        base_path = config.base_path
        folder_path = config.folder_path
        pattern = config.pattern

        # Helper function to list folders matching the pattern
        def list_matching_folders(custom_path: str, pattern: str):
            matched_folders = []
            for root, _, files in walk(custom_path):
                for file in files:
                    if re.fullmatch(pattern.replace('*', '.*').replace('?', '.'), file):
                        relative_path = root.replace(base_path, '').replace('\\', '/').lstrip('/')
                        if relative_path not in matched_folders:
                            matched_folders.append(relative_path)
            return matched_folders

        # Discover folders
        discovered_folders = []
        if folder_path == '*':
            discovered_folders.extend(list_matching_folders(base_path, pattern))
        elif isinstance(folder_path, list):
            for custom_path in folder_path:
                discovered_folders.extend(list_matching_folders(custom_path, pattern))
        else:
            discovered_folders.extend(list_matching_folders(folder_path, pattern))

        # Add discovered folders to the test suite
        for folder in discovered_folders:
            tests.discoverTestsInFolder(
                folder_path=folder,
                base_path=base_path,
                pattern=pattern,
                test_name_pattern=config.test_name_pattern if config.test_name_pattern else None,
                tags=config.tags if config.tags else None
            )

        # Return the initialized test suite
        return tests