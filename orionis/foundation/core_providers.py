from orionis.foundation.providers.catch_provider import CathcProvider
from orionis.foundation.providers.cli_request_provider import CLRequestProvider
from orionis.foundation.providers.console_provider import ConsoleProvider
from orionis.foundation.providers.directory_provider import DirectoryProvider
from orionis.foundation.providers.dumper_provider import DumperProvider
from orionis.foundation.providers.executor_provider import ConsoleExecuteProvider
from orionis.foundation.providers.inspirational_provider import InspirationalProvider
from orionis.foundation.providers.loader_provider import LoaderProvider
from orionis.foundation.providers.logger_provider import LoggerProvider
from orionis.foundation.providers.performance_counter_provider import (
    PerformanceCounterProvider,
)
from orionis.foundation.providers.progress_bar_provider import ProgressBarProvider
from orionis.foundation.providers.reactor_provider import ReactorProvider
from orionis.foundation.providers.scheduler_provider import ScheduleProvider
from orionis.foundation.providers.testing_provider import TestingProvider
from orionis.foundation.providers.workers_provider import WorkersProvider

def get_core_providers_mapping() -> tuple:
    """
    Return an immutable mapping of core provider classes.

    Returns
    -------
    tuple
        An immutable tuple of core provider classes.
    """
    # Create an immutable mapping of all core provider classes
    return (
        CathcProvider,
        CLRequestProvider,
        ConsoleProvider,
        DirectoryProvider,
        DumperProvider,
        ConsoleExecuteProvider,
        InspirationalProvider,
        LoggerProvider,
        PerformanceCounterProvider,
        ProgressBarProvider,
        ReactorProvider,
        ScheduleProvider,
        TestingProvider,
        WorkersProvider,
        LoaderProvider,
    )

# Core framework providers collection as an immutable mapping
CORE_PROVIDERS: tuple = get_core_providers_mapping()
