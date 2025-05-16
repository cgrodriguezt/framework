import re
from os import walk
from typing import List
from orionis.luminate.config.testing.entities.testing import Testing as Configuration
from orionis.luminate.test.suites.contracts.test_suite import ITestSuite
from orionis.luminate.test.suites.test_unit import UnitTest
from orionis.luminate.test.exceptions.test_config_exception import OrionisTestConfigException

class TestSuite(ITestSuite):
    """
    TestSuite provides static configuration and initialization of a unit test suite based on a given Testing configuration.
    Methods:
        config(config: Testing) -> UnitTest
            Configures and initializes a test suite using the provided Testing configuration.
            - Validates the type of the configuration object.
            - Sets up the UnitTest suite with parameters such as verbosity, execution mode, worker count, and error handling.
            - Discovers test folders based on base path, folder path(s), and filename pattern, supporting wildcards.
            - Adds discovered test folders to the suite, optionally filtering by test name pattern and tags.
        OrionisTestConfigException: If the provided config is not an instance of the Testing class.
    """

    def __new__(cls,
        verbosity: int = 2,
        execution_mode: str = "sequential",
        max_workers: int = 1,
        fail_fast: bool = False,
        print_result: bool = True,
        throw_exception: bool = False,
        base_path: str = 'tests',
        folder_path: str | list = '*',
        pattern: str = 'test_*.py',
        test_name_pattern: str | None = None,
        tags: List[str] | None = None
    ):
        """
        Allows instantiating TestSuite(...) and directly obtaining a configured UnitTest instance.
        Args:
            The same arguments as Testing.
        Returns:
            UnitTest: A configured UnitTest suite.
            The returned object supports methods such as:
                - configure(...)
                - discoverTestsInFolder(...)
                - run(...)
                - getResults()
                - and other UnitTest class methods.
        Raises:
            OrionisTestConfigException: If any argument is invalid.
        """
        config = Configuration(
            verbosity=verbosity,
            execution_mode=execution_mode,
            max_workers=max_workers,
            fail_fast=fail_fast,
            print_result=print_result,
            throw_exception=throw_exception,
            base_path=base_path,
            folder_path=folder_path,
            pattern=pattern,
            test_name_pattern=test_name_pattern,
            tags=tags if tags is not None else None
        )
        return cls.config(config)

    @staticmethod
    def config(config:Configuration) -> UnitTest:
        """
        Configures and initializes a UnitTest suite based on the provided Configuration configuration.
        Args:
            config (Configuration): An instance of the Configuration class containing configuration options for the test suite.
        Returns:
            UnitTest: An initialized UnitTest suite configured according to the provided settings.
        Raises:
            OrionisTestConfigException: If the config parameter is not an instance of the Configuration class.
        The function performs the following steps:
            - Validates the type of the config parameter.
            - Initializes a UnitTest suite and applies configuration values from the Configuration instance.
            - Discovers folders containing test files based on the specified base path, folder path(s), and filename pattern.
            - Adds discovered test folders to the UnitTest suite, applying optional test name patterns and tags.
            - Returns the configured UnitTest suite ready for execution.
        """

        # Check if the config is an instance of Configuration
        if not isinstance(config, Configuration):
            raise OrionisTestConfigException("The config parameter must be an instance of the Configuration class.")

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
                discovered_folders.extend(list_matching_folders(f"{base_path}/{custom_path}", pattern))
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