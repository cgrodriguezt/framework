from orionis.app import app
from app.console.scheduler import Scheduler
from app.exceptions.handler import ExceptionHandler
from app.providers.welcome_provider import WelcomeProvider
from config.app import BootstrapApp
from config.auth import BootstrapAppAuth
from config.cache import BootstrapCache
from config.cors import BootstrapCors
from config.database import BootstrapDatabase
from config.filesystems import BootstrapFilesystems
from config.logging import BootstrapLogging
from config.mail import BootstrapMail
from config.paths import BootstrapPaths
from config.queue import BootstrapQueue
from config.session import BootstrapSession
from config.testing import BootstrapTesting

# Add a custom command scheduler to the application.
app.setScheduler(Scheduler)

# Set a global custom exception handler.
app.setExceptionHandler(ExceptionHandler)

# Register service providers with the application.
app.withProviders([
    WelcomeProvider,
])

# Register application configurator classes.
app.withConfigurators(
    app=BootstrapApp,
    auth=BootstrapAppAuth,
    cache=BootstrapCache,
    cors=BootstrapCors,
    database=BootstrapDatabase,
    filesystems=BootstrapFilesystems,
    logging=BootstrapLogging,
    mail=BootstrapMail,
    path=BootstrapPaths,
    queue=BootstrapQueue,
    session=BootstrapSession,
    testing=BootstrapTesting,
)

# Boot the application.
app.create()
