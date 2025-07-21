import gc
import os
import re
from os import walk
import sys
from orionis.foundation.config.testing.entities.testing import Testing
from orionis.foundation.contracts.application import IApplication
from orionis.test.contracts.kernel import ITestKernel
from orionis.test.core.unit_test import UnitTest
from orionis.test.exceptions import OrionisTestConfigException

class TestKernel(ITestKernel):

    # Attributes
    # __unit_test is a singleton instance of UnitTest that will be used to run tests.
    # It is initialized once and reused across the TestKernel instance.
    __unit_test: UnitTest = UnitTest()

    def __init__(
        self,
        app: IApplication,
        config: Testing | dict = None,
        **kwargs
    ) -> None:
        """
        Initializes the test kernel with the provided application instance and configuration.
        Args:
            app (IApplication): The application instance to be tested. Must be an instance of IApplication.
            config (Testing | dict, optional): The configuration for the test kernel. Can be an instance of the Testing dataclass, a dictionary of configuration values, or None. If None, configuration will be initialized using keyword arguments.
            **kwargs: Additional keyword arguments used to initialize the Testing configuration if `config` is None.
        Raises:
            OrionisTestConfigException: If the provided application instance is not of type IApplication, or if there is an error initializing the configuration.
        """

        # Attributes
        self.__config = None
        self.__app = None

        # Validate the application instance
        if not isinstance(app, IApplication):
            raise OrionisTestConfigException(
                f"Invalid application instance provided. Expected an instance of IApplication, got {type(app).__module__}.{type(app).__name__}."
            )

        # Initialize the logger configuration using **kwargs if provided
        if config is None:

            # Try to initialize with default values from Testing dataclass
            try:

                # Initialize the Testing configuration with default values
                self.__config = Testing(**kwargs)

            except Exception as e:

                # If initialization fails, raise an exception with detailed information
                raise OrionisTestConfigException(
                    f"Error initializing logger configuration: {e}. "
                    "Please check the provided parameters. "
                    f"Expected a Logging dataclass or a configuration dictionary. "
                    f"Type received: {type(config).__module__}.{type(config).__name__}. "
                    f"Expected: {Testing.__module__}.{Testing.__name__} or dict."
                )

        # If config is a dictionary, convert it to Logging
        elif isinstance(config, dict):
            self.__config = Testing(**config)

        # If config is already an instance of Logging, use it directly
        elif isinstance(config, Testing):
            self.__config = config

    def __listMatchingFolders(self, base_path: str, custom_path: str, pattern: str):

            matched_folders = []
            for root, _, files in walk(custom_path):
                for file in files:
                    if re.fullmatch(pattern.replace('*', '.*').replace('?', '.'), file):
                        relative_path = root.replace(base_path, '').replace('\\', '/').lstrip('/')
                        if relative_path not in matched_folders:
                            matched_folders.append(relative_path)
            return matched_folders

    def handle(self, *args, **kwargs) -> UnitTest:

        # Assign the application instance to the test suite
        self.__unit_test.setApplication(self.__app)

        # Configure the test suite with validated configuration values
        self.__unit_test.configure(
            verbosity=self.__config.verbosity,
            execution_mode=self.__config.execution_mode,
            max_workers=self.__config.max_workers,
            fail_fast=self.__config.fail_fast,
            print_result=self.__config.print_result,
            throw_exception=self.__config.throw_exception,
            persistent=self.__config.persistent,
            persistent_driver=self.__config.persistent_driver,
            web_report=self.__config.web_report
        )

        # Extract configuration values for test discovery
        base_path = self.__config.base_path
        folder_path = self.__config.folder_path
        pattern = self.__config.pattern

        

        # Discover test folders based on configuration
        discovered_folders = []
        if folder_path == '*':
            # Search all folders under base_path
            discovered_folders.extend(self.__listMatchingFolders(base_path, base_path, pattern))
        elif isinstance(folder_path, list):
            # Search specific folders provided in the list
            for custom_path in folder_path:
                discovered_folders.extend(self.__listMatchingFolders(base_path, f"{base_path}/{custom_path}", pattern))
        else:
            # Search single specified folder
            discovered_folders.extend(self.__listMatchingFolders(base_path, folder_path, pattern))

        # Add discovered folders to the test suite for execution
        for folder in discovered_folders:
            self.__unit_test.discoverTestsInFolder(
                folder_path=folder,
                base_path=base_path,
                pattern=pattern,
                test_name_pattern=self.__config.test_name_pattern if self.__config.test_name_pattern else None,
                tags=self.__config.tags if self.__config.tags else None
            )

        # Execute the test suite and return the results
        return self.__unit_test.run()