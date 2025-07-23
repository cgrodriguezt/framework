from abc import ABC, abstractmethod
from typing import Any
from orionis.foundation.config.testing.entities.testing import Testing as Configuration
from orionis.test.core.unit_test import UnitTest

class ITestKernel(ABC):
    """
    Abstract interface for test kernel implementations.

    This contract defines the required methods that any test kernel implementation
    must provide for the Orionis testing framework. It ensures consistent behavior
    across different test kernel implementations.

    The test kernel is responsible for:
    - Managing application context for testing
    - Validating and handling test configuration
    - Orchestrating test discovery and execution
    - Providing a unified interface for test operations
    """

    @abstractmethod
    def handle(
        self,
        config: Configuration = None,
        **kwargs: Any
    ) -> UnitTest:
        """
        Execute the complete test discovery and execution pipeline.

        This is the main entry point for running tests. Implementations must:
        1. Validate the provided configuration
        2. Discover test files based on configuration
        3. Configure and execute the test suite
        4. Return the test results

        Parameters
        ----------
        config : Configuration, optional
            A pre-configured Testing configuration instance. If None,
            implementations should create one from kwargs.
        **kwargs : Any
            Keyword arguments to create a Configuration instance if config is None.
            Common parameters include:
            - base_path : str, base directory for test discovery
            - folder_path : str or list, specific folders to search
            - pattern : str, file pattern for test discovery
            - verbosity : int, output verbosity level
            - execution_mode : str, test execution mode
            - max_workers : int, maximum number of worker threads
            - fail_fast : bool, stop on first failure

        Returns
        -------
        UnitTest
            The configured and executed test suite instance containing all results.

        Raises
        ------
        OrionisTestConfigException
            If the configuration validation fails.
        """
        pass
