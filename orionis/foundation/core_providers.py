from orionis.foundation.providers.application_provider import ApplicationProvider
from orionis.foundation.providers.catch_provider import CathcProvider
from orionis.foundation.providers.logger_provider import LoggerProvider
from orionis.foundation.providers.reactor_provider import ReactorProvider
from orionis.foundation.providers.router_provider import RouterProvider
from orionis.foundation.providers.scheduler_provider import ScheduleProvider
from orionis.foundation.providers.testing_provider import TestingProvider

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
        ApplicationProvider,
        CathcProvider,
        LoggerProvider,
        ReactorProvider,
        RouterProvider,
        ScheduleProvider,
        TestingProvider,
    )

# Core framework providers collection as an immutable mapping
CORE_PROVIDERS: tuple = get_core_providers_mapping()
