from __future__ import annotations
from dataclasses import dataclass, field
from orionis.support.entities.base import BaseEntity
from orionis.foundation.config.testing.enums import (
    ExecutionMode,
    PersistentDrivers,
    VerbosityMode,
)
from orionis.services.system.workers import Workers

@dataclass(frozen=True, kw_only=True)
class Testing(BaseEntity):
    """
    Configure test execution options for the testing framework.

    Parameters
    ----------
    verbosity : int | VerbosityMode, optional
        Verbosity level for test output. 0 = silent, 1 = minimal, 2 = detailed
        (default: 2).
    execution_mode : str | ExecutionMode, optional
        Mode of test execution. 'SEQUENTIAL' runs tests one after another,
        'PARALLEL' runs tests in parallel (default: 'SEQUENTIAL').
    max_workers : int, optional
        Maximum number of worker threads/processes for parallel execution
        (default: calculated by Workers).
    fail_fast : bool, optional
        If True, stop execution after the first test failure (default: False).
    throw_exception : bool, optional
        If True, raise an exception on test failure (default: False).
    base_path : str, optional
        Base directory where tests are located (default: 'tests').
    folder_path : str | list, optional
        Folder path pattern(s) to search for tests (default: '*').
    pattern : str, optional
        Filename pattern to identify test files (default: 'test_*.py').
    test_name_pattern : str | None, optional
        Pattern to match specific test names (default: None).
    persistent : bool, optional
        If True, keep test results persistent (default: False).
    persistent_driver : str | PersistentDrivers, optional
        Driver to use for persisting test results. Supported: 'sqlite', 'json'
        (default: 'json').
    web_report : bool, optional
        If True, generate a web report for test results (default: False).

    Notes
    -----
    All configuration options are validated on initialization. An exception is
    raised if any value is invalid.
    """

    verbosity: int | VerbosityMode = field(
        default=VerbosityMode.DETAILED.value,
        metadata={
            "description": "The verbosity level of the test output. Default is 2.",
            "default": VerbosityMode.DETAILED.value,
        },
    )

    execution_mode: str | ExecutionMode = field(
        default=ExecutionMode.SEQUENTIAL.value,
        metadata={
            "description": "The mode of test execution. Default is SEQUENTIAL",
            "default": ExecutionMode.SEQUENTIAL.value,
        },
    )

    max_workers: int = field(
        default=1,
        metadata={
            "description": (
                "The maximum number of worker threads/processes to use when running "
                "tests in parallel."
            ),
            "default": 1,
        },
    )

    fail_fast: bool = field(
        default=False,
        metadata={
            "description": (
                "Whether to stop execution after the first test failure. "
                "Default is False."
            ),
            "default": False,
        },
    )

    throw_exception: bool = field(
        default=False,
        metadata={
            "description": (
                "Whether to throw an exception if a test fails. Default is False."
            ),
            "default": False,
        },
    )

    folder_path: str | list = field(
        default="*",
        metadata={
            "description": (
                "The folder path pattern to search for tests. Default is '*'."
            ),
            "default": "*",
        },
    )

    pattern: str = field(
        default="test_*.py",
        metadata={
            "description": (
                "The filename pattern to identify test files. Default is 'test_*.py'."
            ),
            "default": "test_*.py",
        },
    )

    test_name_pattern: str | None = field(
        default=None,
        metadata={
            "description": (
                "A pattern to match specific test names. Default is None."
            ),
            "default": None,
        },
    )

    persistent: bool = field(
        default=False,
        metadata={
            "description": (
                "Whether to keep the test results persistent. Default is False."
            ),
            "default": False,
        },
    )

    persistent_driver: str | PersistentDrivers = field(
        default=PersistentDrivers.JSON.value,
        metadata={
            "description": (
                "Specifies the driver to use for persisting test results. Supported "
                "values: 'sqlite', 'json'. Default is 'sqlite'."
            ),
            "default": PersistentDrivers.JSON.value,
        },
    )

    web_report: bool = field(
        default=False,
        metadata={
            "description": (
                "Whether to generate a web report for the test results. "
                "Default is False."
            ),
            "default": False,
        },
    )

    def __validateVerbosity(self) -> None:
        """
        Validate and normalize the verbosity configuration.

        Parameters
        ----------
        self : Testing
            The instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        # Ensure verbosity is an integer or VerbosityMode
        if not isinstance(self.verbosity, (int, VerbosityMode)):
            error_msg = (
                f"Invalid type for 'verbosity': {type(self.verbosity).__name__}. "
                "It must be an integer or an instance of VerbosityMode."
            )
            raise TypeError(error_msg)

        if isinstance(self.verbosity, int):
            # Check that verbosity is within the allowed range
            max_verbosity = max(mode.value for mode in VerbosityMode)
            if self.verbosity < 0 or self.verbosity > max_verbosity:
                error_msg = (
                    f"Invalid value for 'verbosity': {self.verbosity}. "
                    "It must be an integer between 0 (silent) and 2 (detailed output)."
                )
                raise ValueError(error_msg)
        elif isinstance(self.verbosity, VerbosityMode):
            # Normalize enum to its value
            object.__setattr__(self, "verbosity", self.verbosity.value)

    def __validateExecutionMode(self) -> None:
        """
        Validate and normalize the execution_mode configuration.

        Parameters
        ----------
        self : Testing
            Instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        # Ensure execution_mode is a string or ExecutionMode enum
        if not isinstance(self.execution_mode, (str, ExecutionMode)):
            error_msg = (
                f"Invalid type for 'execution_mode': "
                f"{type(self.execution_mode).__name__}. "
                "It must be a string or an instance of ExecutionMode."
            )
            raise TypeError(error_msg)

        if isinstance(self.execution_mode, str):
            # Normalize string to enum value if valid
            options_modes = ExecutionMode._member_names_
            _value = str(self.execution_mode).upper().strip()
            if _value not in options_modes:
                error_msg = (
                    f"Invalid value for 'execution_mode': {self.execution_mode}. "
                    f"It must be one of: {options_modes!s}."
                )
                raise ValueError(error_msg)
            object.__setattr__(
                self, "execution_mode", ExecutionMode[_value].value,
            )
        elif isinstance(self.execution_mode, ExecutionMode):
            object.__setattr__(self, "execution_mode", self.execution_mode.value)

    def __validateMaxWorkers(self) -> None:
        """
        Validate and normalize the max_workers configuration.

        Parameters
        ----------
        self : Testing
            Instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        # Ensure max_workers is a positive integer
        if not isinstance(self.max_workers, int) or self.max_workers < 1:
            error_msg = (
                f"Invalid value for 'max_workers': {self.max_workers}. "
                "It must be a positive integer greater than 0."
            )
            raise ValueError(error_msg)

        # Ensure max_workers does not exceed system capability
        real_max_working = Workers().calculate()
        if self.max_workers > real_max_working:
            error_msg = (
                f"Invalid value for 'max_workers': {self.max_workers}. "
                "It must be less than or equal to the real maximum workers "
                f"available: {real_max_working}."
            )
            raise ValueError(error_msg)

    def __validateFailFast(self) -> None:
        """
        Validate the fail_fast configuration.

        Parameters
        ----------
        self : Testing
            Instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        if not isinstance(self.fail_fast, bool):
            error_msg = (
                f"Invalid type for 'fail_fast': {type(self.fail_fast).__name__}. "
                "It must be a boolean (True or False)."
            )
            raise TypeError(error_msg)

    def __validateThrowException(self) -> None:
        """
        Validate the throw_exception configuration.

        Parameters
        ----------
        self : Testing
            Instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        if not isinstance(self.throw_exception, bool):
            error_msg = (
                f"Invalid type for 'throw_exception': "
                f"{type(self.throw_exception).__name__}. "
                "It must be a boolean (True or False)."
            )
            raise TypeError(error_msg)

    def __validateFolderPath(self) -> None:
        """
        Validate the folder_path configuration.

        Parameters
        ----------
        self : Testing
            Instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        # Ensure folder_path is a string or a list of strings
        if not isinstance(self.folder_path, (str, list)):
            error_msg = (
                f"Invalid type for 'folder_path': {type(self.folder_path).__name__}. "
                "It must be a string or a list of strings representing the folder "
                "path pattern."
            )
            raise TypeError(error_msg)

        if isinstance(self.folder_path, list):
            # Ensure all elements in folder_path list are strings
            for i, folder in enumerate(self.folder_path):
                if not isinstance(folder, str):
                    error_msg = (
                        f"Invalid type for folder at index {i} in 'folder_path': "
                        f"{type(folder).__name__}. Each folder path must be a string."
                    )
                    raise TypeError(error_msg)

    def __validatePattern(self) -> None:
        """
        Validate the pattern configuration.

        Parameters
        ----------
        self : Testing
            Instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        if not isinstance(self.pattern, str):
            error_msg = (
                f"Invalid type for 'pattern': {type(self.pattern).__name__}. "
                "It must be a string representing the filename pattern for test files."
            )
            raise TypeError(error_msg)

    def __validateTestNamePattern(self) -> None:
        """
        Validate the test_name_pattern configuration.

        Parameters
        ----------
        self : Testing
            Instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        if self.test_name_pattern is not None and not isinstance(
            self.test_name_pattern, str,
        ):
            error_msg = (
                f"Invalid type for 'test_name_pattern': "
                f"{type(self.test_name_pattern).__name__}. "
                "It must be a string or None."
            )
            raise TypeError(error_msg)

    def __validatePersistentDriver(self: Testing) -> None:
        """
        Validate and normalize the persistent and persistent_driver configuration.

        Parameters
        ----------
        self : Testing
            Instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        # Ensure persistent is a boolean
        if not isinstance(self.persistent, bool):
            error_msg = (
                f"Invalid type for 'persistent': {type(self.persistent).__name__}. "
                "It must be a boolean (True or False)."
            )
            raise TypeError(error_msg)

        # If persistence is enabled, validate persistent_driver
        if self.persistent:
            if not isinstance(self.persistent_driver, (str, PersistentDrivers)):
                error_msg = (
                    f"Invalid type for 'persistent_driver': "
                    f"{type(self.persistent_driver).__name__}. "
                    "It must be a string or an instance of PersistentDrivers."
                )
                raise TypeError(error_msg)

            if isinstance(self.persistent_driver, str):
                # Normalize string to enum value if valid
                options_drivers = PersistentDrivers._member_names_
                _value = str(self.persistent_driver).upper().strip()
                if _value not in options_drivers:
                    error_msg = (
                        f"Invalid value for 'persistent_driver': "
                        f"{self.persistent_driver}. It must be one of: "
                        f"{options_drivers!s}."
                    )
                    raise ValueError(error_msg)
                object.__setattr__(
                    self, "persistent_driver", PersistentDrivers[_value].value,
                )
            else:
                object.__setattr__(
                    self, "persistent_driver", self.persistent_driver.value,
                )

    def __validateWebReport(self) -> None:
        """
        Validate the web_report configuration.

        Parameters
        ----------
        self : Testing
            Instance of the Testing configuration.

        Returns
        -------
        None
            This method does not return a value. Raises exceptions on error.
        """
        if not isinstance(self.web_report, bool):
            error_msg = (
                f"Invalid type for 'web_report': {type(self.web_report).__name__}. "
                "It must be a boolean (True or False)."
            )
            raise TypeError(error_msg)

    def __post_init__(self) -> None:
        """
        Validate and normalize configuration options after initialization.

        Ensures all configuration attributes are valid and normalized. Raises
        exceptions for invalid types or values. Converts enum/string values to
        canonical forms where appropriate.

        Returns
        -------
        None
            This method does not return a value. Exceptions are raised on error.
        """
        super().__post_init__()

        # Validate verbosity type and value
        self.__validateVerbosity()

        # Validate execution_mode type and value
        self.__validateExecutionMode()

        # Validate max_workers is a positive integer
        self.__validateMaxWorkers()

        # Validate fail_fast is boolean
        self.__validateFailFast()

        # Validate throw_exception is boolean
        self.__validateThrowException()

        # Validate folder_path is string or list of strings
        self.__validateFolderPath()

        # Validate pattern is string
        self.__validatePattern()

        # Validate test_name_pattern is string or None
        self.__validateTestNamePattern()

        # Validate persistent and persistent_driver
        self.__validatePersistentDriver()

        # Validate web_report is boolean
        self.__validateWebReport()
