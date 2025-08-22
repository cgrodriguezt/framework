from pathlib import Path
from app.console.scheduler import Scheduler
from app.exceptions.handler import ExceptionHandler
from config.app import BootstrapApp
from config.auth import BootstrapAppAuth
from config.cache import BootstrapCache
from config.cors import BootstrapCors
from config.database import BootstrapDatabase
from orionis.app import Orionis

# Create and configure the Orionis application instance
app = Orionis().setPaths(
        root=Path().cwd()
    ).setScheduler(
        Scheduler
    ).setExceptionHandler(
        ExceptionHandler
    ).withConfigurators(
        app=BootstrapApp(),
        auth=BootstrapAppAuth(),
        cache=BootstrapCache(),
        cors=BootstrapCors(),
        database=BootstrapDatabase()
    ).create()