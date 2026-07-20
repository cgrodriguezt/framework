from orionis.console.reactor_provider import ReactorProvider
from orionis.console.scheduler_provider import ScheduleProvider
from orionis.failure.provider import CatchProvider
from orionis.http.routes.provider import RouterProvider
from orionis.log.provider import LoggerProvider
from orionis.test.provider import TestingProvider

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
        CatchProvider,
        LoggerProvider,
        ReactorProvider,
        RouterProvider,
        ScheduleProvider,
        TestingProvider,
    )

# Core framework providers collection as an immutable mapping
CORE_PROVIDERS: tuple = get_core_providers_mapping()
