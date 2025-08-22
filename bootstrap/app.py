from pathlib import Path
from app.console.scheduler import Scheduler
from app.exceptions.handler import ExceptionHandler
from config.app import BootstrapApp
from config.auth import BootstrapAppAuth
from config.cache import BootstrapCache
from config.cors import BootstrapCors
from config.database import BootstrapDatabase
from config.filesystems import BootstrapFilesystems
from config.logging import BootstrapLogging
from config.mail import BootstrapMail
from config.queue import BootstrapQueue
from config.session import BootstrapSession
from config.testing import BootstrapTesting
from orionis.app import Orionis

"""
----------------------------------------------------------------------------
Orionis Application Bootstrapper
This module initializes and configures the Orionis application instance.
It sets up the application's root path, scheduler, exception handler, and
registers essential configurators such as app, authentication, cache, CORS,
and database settings.
Configuration Steps:
- Defines the application's root directory.
- Registers the task scheduler for console commands.
- Sets up the global exception handler for error management.
- Loads and applies configuration modules for core services.
Usage:
    Import this module to obtain a fully configured Orionis application
    instance ready for use.
----------------------------------------------------------------------------
"""
app = (
    Orionis(
        basePath = Path(__file__).parent.parent.resolve()
    )
    .setScheduler(
        Scheduler
    )
    .setExceptionHandler(
        ExceptionHandler
    )
    .withConfigurators(
        app=BootstrapApp(),
        auth=BootstrapAppAuth(),
        cache=BootstrapCache(),
        cors=BootstrapCors(),
        database=BootstrapDatabase(),
        filesystems=BootstrapFilesystems(),
        logging=BootstrapLogging(),
        mail=BootstrapMail(),
        queue=BootstrapQueue(),
        session=BootstrapSession(),
        testing=BootstrapTesting()
    )
    .create()
)