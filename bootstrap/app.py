from pathlib import Path
from app.console.scheduler import Scheduler
from app.exceptions.handler import ExceptionHandler
from app.providers.app_service_provider import AppServiceProvider
from orionis.foundation.application import Application
from orionis.foundation.enums.lifespan import Lifespan
from orionis.foundation.enums.runtimes import Runtime

# Create the application instance with caching enabled
app = Application(
    base_path=Path(__file__).parent.parent,
    compiled=True,
    compiled_path="storage/framework/bootstrap",
    compiled_invalidation_paths=[
        "app",
        "bootstrap",
        "config",
        "resources",
        "routes",
        ".env"
    ],
)

# Register route files for different runtime contexts
app.withRouting(
    console="routes/console.py",
    web="routes/web.py",
    api="routes/api.py",
    health="/up",
)

# Attach scheduler for CLI runtime scheduled jobs
app.withScheduler(Scheduler)

# Set global exception handler for all unhandled exceptions
app.withExceptionHandler(ExceptionHandler)

# Register service providers for dependency injection
app.withProviders(
    AppServiceProvider,
    # Add additional providers below...
)

# Boot the application and prepare the runtime environment
app.create()