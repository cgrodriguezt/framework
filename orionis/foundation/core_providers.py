from orionis.cache.provider import CacheProvider
from orionis.console.reactor_provider import ReactorProvider
from orionis.console.scheduler_provider import ScheduleProvider
from orionis.database.database_provider import DatabaseProvider
from orionis.database.schema_provider import SchemaProvider
from orionis.failure.provider import CatchProvider
from orionis.http.routes.provider import RouterProvider
from orionis.localization.provider import LocalizationProvider
from orionis.logging.provider import LoggerProvider
from orionis.storage.provider import StorageProvider
from orionis.test.provider import TestingProvider
from orionis.view.provider import ViewServiceProvider

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
        CacheProvider,
        CatchProvider,
        DatabaseProvider,
        LocalizationProvider,
        LoggerProvider,
        ReactorProvider,
        RouterProvider,
        ScheduleProvider,
        StorageProvider,
        SchemaProvider,
        TestingProvider,
        ViewServiceProvider,
    )

# Core framework providers collection as an immutable mapping
CORE_PROVIDERS: tuple = get_core_providers_mapping()
