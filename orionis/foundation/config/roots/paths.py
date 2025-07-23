from dataclasses import dataclass, field, fields
from pathlib import Path
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Paths(BaseEntity):

    console_scheduler: str = field(
        default = str(Path('app/console/kernel.py').resolve()),
        metadata = {
            'description': 'Path to the console scheduler (Kernel) file.',
            'default': str(Path('app/console/kernel.py').resolve())
        }
    )

    console_commands: str = field(
        default = str(Path('app/console/commands').resolve()),
        metadata = {
            'description': 'Directory containing custom ArtisanStyle console commands.',
            'default': str(Path('app/console/commands').resolve())
        }
    )

    http_controllers: str = field(
        default = str(Path('app/http/controllers').resolve()),
        metadata = {
            'description': 'Directory containing HTTP controller classes.',
            'default': str(Path('app/http/controllers').resolve())
        }
    )

    http_middleware: str = field(
        default = str(Path('app/http/middleware').resolve()),
        metadata = {
            'description': 'Directory containing HTTP middleware classes.',
            'default': str(Path('app/http/middleware').resolve())
        }
    )

    http_requests: str = field(
        default = str(Path('app/http/requests').resolve()),
        metadata = {
            'description': 'Directory containing HTTP form request validation classes.',
            'default': str(Path('app/http/requests').resolve())
        }
    )

    models: str = field(
        default = str(Path('app/models').resolve()),
        metadata = {
            'description': 'Directory containing ORM model classes.',
            'default': str(Path('app/models').resolve())
        }
    )

    providers: str = field(
        default = str(Path('app/providers').resolve()),
        metadata = {
            'description': 'Directory containing service provider classes.',
            'default': str(Path('app/providers').resolve())
        }
    )

    events: str = field(
        default = str(Path('app/events').resolve()),
        metadata = {
            'description': 'Directory containing event classes.',
            'default': str(Path('app/events').resolve())
        }
    )

    listeners: str = field(
        default = str(Path('app/listeners').resolve()),
        metadata = {
            'description': 'Directory containing event listener classes.',
            'default': str(Path('app/listeners').resolve())
        }
    )

    notifications: str = field(
        default = str(Path('app/notifications').resolve()),
        metadata = {
            'description': 'Directory containing notification classes.',
            'default': str(Path('app/notifications').resolve())
        }
    )

    jobs: str = field(
        default = str(Path('app/jobs').resolve()),
        metadata = {
            'description': 'Directory containing queued job classes.',
            'default': str(Path('app/jobs').resolve())
        }
    )

    policies: str = field(
        default = str(Path('app/policies').resolve()),
        metadata = {
            'description': 'Directory containing authorization policy classes.',
            'default': str(Path('app/policies').resolve())
        }
    )

    exceptions: str = field(
        default = str(Path('app/exceptions').resolve()),
        metadata = {
            'description': 'Directory containing exception handler classes.',
            'default': str(Path('app/exceptions').resolve())
        }
    )

    services: str = field(
        default = str(Path('app/services').resolve()),
        metadata = {
            'description': 'Directory containing business logic service classes.',
            'default': str(Path('app/services').resolve())
        }
    )

    views: str = field(
        default = str(Path('resources/views').resolve()),
        metadata = {
            'description': 'Directory containing template view files.',
            'default': str(Path('resources/views').resolve())
        }
    )

    lang: str = field(
        default = str(Path('resources/lang').resolve()),
        metadata = {
            'description': 'Directory containing internationalization files.',
            'default': str(Path('resources/lang').resolve())
        }
    )

    assets: str = field(
        default = str(Path('resources/assets').resolve()),
        metadata = {
            'description': 'Directory containing frontend assets (JS, CSS, images).',
            'default': str(Path('resources/assets').resolve())
        }
    )

    routes_web: str = field(
        default = str(Path('routes/web.py').resolve()),
        metadata = {
            'description': 'Path to the web routes definition file.',
            'default': str(Path('routes/web.py').resolve())
        }
    )

    routes_api: str = field(
        default = str(Path('routes/api.py').resolve()),
        metadata = {
            'description': 'Path to the API routes definition file.',
            'default': str(Path('routes/api.py').resolve())
        }
    )

    routes_console: str = field(
        default = str(Path('routes/console.py').resolve()),
        metadata = {
            'description': 'Path to the console routes definition file.',
            'default': str(Path('routes/console.py').resolve())
        }
    )

    routes_channels: str = field(
        default = str(Path('routes/channels.py').resolve()),
        metadata = {
            'description': 'Path to the broadcast channels routes file.',
            'default': str(Path('routes/channels.py').resolve())
        }
    )

    config: str = field(
        default = str(Path('config').resolve()),
        metadata = {
            'description': 'Directory containing application configuration files.',
            'default': str(Path('config').resolve())
        }
    )

    migrations: str = field(
        default = str(Path('database/migrations').resolve()),
        metadata = {
            'description': 'Directory containing database migration files.',
            'default': str(Path('database/migrations').resolve())
        }
    )

    seeders: str = field(
        default = str(Path('database/seeders').resolve()),
        metadata = {
            'description': 'Directory containing database seeder files.',
            'default': str(Path('database/seeders').resolve())
        }
    )

    factories: str = field(
        default = str(Path('database/factories').resolve()),
        metadata = {
            'description': 'Directory containing model factory files.',
            'default': str(Path('database/factories').resolve())
        }
    )

    storage_logs: str = field(
        default = str(Path('storage/logs').resolve()),
        metadata = {
            'description': 'Directory containing application log files.',
            'default': str(Path('storage/logs').resolve())
        }
    )

    storage_framework: str = field(
        default = str(Path('storage/framework').resolve()),
        metadata = {
            'description': 'Directory for framework-generated files (cache, sessions, views).',
            'default': str(Path('storage/framework').resolve())
        }
    )

    storage_sessions: str = field(
        default = str(Path('storage/framework/sessions').resolve()),
        metadata = {
            'description': 'Directory containing session files.',
            'default': str(Path('storage/framework/sessions').resolve())
        }
    )

    storage_cache: str = field(
        default = str(Path('storage/framework/cache').resolve()),
        metadata = {
            'description': 'Directory containing framework cache files.',
            'default': str(Path('storage/framework/cache').resolve())
        }
    )

    storage_views: str = field(
        default = str(Path('storage/framework/views').resolve()),
        metadata = {
            'description': 'Directory containing compiled view files.',
            'default': str(Path('storage/framework/views').resolve())
        }
    )

    def __post_init__(self) -> None:
        """
        Ensures all path attributes are of type str.

        Raises
        ------
        OrionisIntegrityException
            If any attribute is not a string.
        """
        for field_ in fields(self):
            value = getattr(self, field_.name)
            if not isinstance(value, str):
                raise OrionisIntegrityException(
                    f"Invalid type for '{field_.name}': expected str, got {type(value).__name__}"
                )

    def getConsoleScheduler(self) -> Path:
        """
        Returns the absolute path to the console scheduler (Kernel) file.

        Returns
        -------
        pathlib.Path
            Path to the console scheduler file used for scheduled tasks.
        """
        return Path(self.console_scheduler)

    def getConsoleCommands(self) -> Path:
        """
        Returns the absolute path to the directory containing custom console commands.

        Returns
        -------
        pathlib.Path
            Path to the directory for Artisan-style console commands.
        """
        return Path(self.console_commands)

    def getHttpControllers(self) -> Path:
        """
        Returns the absolute path to the HTTP controllers directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing HTTP controller classes.
        """
        return Path(self.http_controllers)

    def getHttpMiddleware(self) -> Path:
        """
        Returns the absolute path to the HTTP middleware directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing HTTP middleware classes.
        """
        return Path(self.http_middleware)

    def getHttpRequests(self) -> Path:
        """
        Returns the absolute path to the HTTP requests directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing HTTP form request validation classes.
        """
        return Path(self.http_requests)

    def getModels(self) -> Path:
        """
        Returns the absolute path to the models directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing ORM model classes.
        """
        return Path(self.models)

    def getProviders(self) -> Path:
        """
        Returns the absolute path to the service providers directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing service provider classes.
        """
        return Path(self.providers)

    def getEvents(self) -> Path:
        """
        Returns the absolute path to the events directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing event classes.
        """
        return Path(self.events)

    def getListeners(self) -> Path:
        """
        Returns the absolute path to the event listeners directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing event listener classes.
        """
        return Path(self.listeners)

    def getNotifications(self) -> Path:
        """
        Returns the absolute path to the notifications directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing notification classes.
        """
        return Path(self.notifications)

    def getJobs(self) -> Path:
        """
        Returns the absolute path to the queued jobs directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing queued job classes.
        """
        return Path(self.jobs)

    def getPolicies(self) -> Path:
        """
        Returns the absolute path to the authorization policies directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing authorization policy classes.
        """
        return Path(self.policies)

    def getExceptions(self) -> Path:
        """
        Returns the absolute path to the exceptions directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing exception handler classes.
        """
        return Path(self.exceptions)

    def getServices(self) -> Path:
        """
        Returns the absolute path to the services directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing business logic service classes.
        """
        return Path(self.services)

    def getViews(self) -> Path:
        """
        Returns the absolute path to the views directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing template view files.
        """
        return Path(self.views)

    def getLang(self) -> Path:
        """
        Returns the absolute path to the language files directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing internationalization files.
        """
        return Path(self.lang)

    def getAssets(self) -> Path:
        """
        Returns the absolute path to the assets directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing frontend assets (JS, CSS, images).
        """
        return Path(self.assets)

    def getRoutesWeb(self) -> Path:
        """
        Returns the absolute path to the web routes definition file.

        Returns
        -------
        pathlib.Path
            Path to the web routes definition file.
        """
        return Path(self.routes_web)

    def getRoutesApi(self) -> Path:
        """
        Returns the absolute path to the API routes definition file.

        Returns
        -------
        pathlib.Path
            Path to the API routes definition file.
        """
        return Path(self.routes_api)

    def getRoutesConsole(self) -> Path:
        """
        Returns the absolute path to the console routes definition file.

        Returns
        -------
        pathlib.Path
            Path to the console routes definition file.
        """
        return Path(self.routes_console)

    def getRoutesChannels(self) -> Path:
        """
        Returns the absolute path to the broadcast channels routes file.

        Returns
        -------
        pathlib.Path
            Path to the broadcast channels routes file.
        """
        return Path(self.routes_channels)

    def getConfig(self) -> Path:
        """
        Returns the absolute path to the configuration directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing application configuration files.
        """
        return Path(self.config)

    def getMigrations(self) -> Path:
        """
        Returns the absolute path to the migrations directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing database migration files.
        """
        return Path(self.migrations)

    def getSeeders(self) -> Path:
        """
        Returns the absolute path to the seeders directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing database seeder files.
        """
        return Path(self.seeders)

    def getFactories(self) -> Path:
        """
        Returns the absolute path to the model factories directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing model factory files.
        """
        return Path(self.factories)

    def getStorageLogs(self) -> Path:
        """
        Returns the absolute path to the logs directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing application log files.
        """
        return Path(self.storage_logs)

    def getStorageFramework(self) -> Path:
        """
        Returns the absolute path to the framework storage directory.

        Returns
        -------
        pathlib.Path
            Path to the directory for framework-generated files (cache, sessions, views).
        """
        return Path(self.storage_framework)

    def getStorageSessions(self) -> Path:
        """
        Returns the absolute path to the sessions storage directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing session files.
        """
        return Path(self.storage_sessions)

    def getStorageCache(self) -> Path:
        """
        Returns the absolute path to the cache storage directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing framework cache files.
        """
        return Path(self.storage_cache)

    def getStorageViews(self) -> Path:
        """
        Returns the absolute path to the compiled views storage directory.

        Returns
        -------
        pathlib.Path
            Path to the directory containing compiled view files.
        """
        return Path(self.storage_views)