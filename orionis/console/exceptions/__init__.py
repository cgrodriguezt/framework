"""
Orionis CLI Framework Exceptions.

===============================

This package provides custom exception classes for the Orionis CLI framework.

Classes
-------
CLIOrionisException
    Base exception for CLI errors.
CLIOrionisRuntimeError
    Exception for runtime errors in the CLI.
CLIOrionisScheduleException
    Exception for scheduling-related errors.
CLIOrionisTypeError
    Exception for type-related errors in the CLI.
CLIOrionisValueError
    Exception for value-related errors in the CLI.
"""

from .cli_exceptions import (
    CLIOrionisException,
    CLIOrionisRuntimeError,
    CLIOrionisScheduleException,
    CLIOrionisTypeError,
    CLIOrionisValueError,
)

__all__ = [
    "CLIOrionisException",
    "CLIOrionisRuntimeError",
    "CLIOrionisScheduleException",
    "CLIOrionisTypeError",
    "CLIOrionisValueError",
]
