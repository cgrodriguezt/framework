from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.testing.enums import VerbosityMode
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Testing(BaseEntity):
    """
    Configure testing settings.

    Parameters
    ----------
    verbosity : int | VerbosityMode
        Level of detail in test output. 0: silent, 1: standard, 2: detailed.
        Defaults to 2 (detailed).
    fail_fast : bool
        If True, stops execution at the first failure. Defaults to False.
    start_dir : str
        Directory to search for tests. Defaults to 'tests'.
    file_pattern : str
        Filename pattern to identify test files. Defaults to 'test_*.py'.
    method_pattern : str
        Pattern to filter specific test methods. Defaults to 'test*'.

    Returns
    -------
    None
        Instantiating this class does not return a value.
    """

    verbosity: int | VerbosityMode = field(
        default=VerbosityMode.DETAILED.value,
        metadata={
            "description": (
                "Level of detail in test output. 0: silent, 1: standard, 2: detailed. "
                "Defaults to 2 (detailed)."
            ),
            "default": VerbosityMode.DETAILED.value,
        },
    )

    fail_fast: bool = field(
        default=False,
        metadata={
            "description": (
                "If True, stops execution at the first failure. Defaults to False."
            ),
            "default": False,
        },
    )

    start_dir: str = field(
        default="tests",
        metadata={
            "description": (
                "Directory to search for tests. Defaults to 'tests'."
            ),
            "default": "tests",
        },
    )

    file_pattern: str = field(
        default="test_*.py",
        metadata={
            "description": (
                "Filename pattern to identify test files. Defaults to 'test_*.py'."
            ),
            "default": "test_*.py",
        },
    )

    method_pattern: str = field(
        default="test*",
        metadata={
            "description": (
                "Pattern to filter specific test methods. Defaults to 'test*'."
            ),
            "default": "test*"
        },
    )

    cache_results: bool = field(
        default=False,
        metadata={
            "description": (
                "Save a JSON file with the test results."
            ),
            "default": False,
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize Testing configuration after initialization.

        Parameters
        ----------
        self : Testing
            Instance of Testing being initialized.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If any property does not match its expected type.
        """
        # Validate verbosity is a valid VerbosityMode or int
        if isinstance(self.verbosity, int):
            valid_values = [mode.value for mode in VerbosityMode]
            if self.verbosity not in valid_values:
                error_msg = (
                    "verbosity must be a valid VerbosityMode value or VerbosityMode instance."
                )
                raise TypeError(error_msg)
        elif not isinstance(self.verbosity, VerbosityMode):
            error_msg = "verbosity must be int or VerbosityMode."
            raise TypeError(error_msg)

        # Normalize verbosity to int if it's a VerbosityMode instance
        if isinstance(self.verbosity, VerbosityMode):
            object.__setattr__(self, 'verbosity', self.verbosity.value)

        # Validate fail_fast is a boolean
        if not isinstance(self.fail_fast, bool):
            error_msg = "fail_fast must be bool."
            raise TypeError(error_msg)

        # Validate start_dir is a string
        if not isinstance(self.start_dir, str):
            error_msg = "start_dir must be str."
            raise TypeError(error_msg)

        # Validate file_pattern is a string
        if not isinstance(self.file_pattern, str):
            error_msg = "file_pattern must be str."
            raise TypeError(error_msg)

        # Validate method_pattern is a string
        if not isinstance(self.method_pattern, str):
            error_msg = "method_pattern must be str."
            raise TypeError(error_msg)
