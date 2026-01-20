from orionis.app import app
from app.console.scheduler import Scheduler
from app.exceptions.handler import ExceptionHandler
from app.providers.welcome_provider import WelcomeProvider
from pathlib import Path

# Configure the application cache directory.
app.withCache(
    path=(Path(__file__).parent.parent / "storage" / "framework" / "cache" / "bootstrap"),
    filename="setup",
    monitored_dirs=[
        Path(__file__).parent.parent / "bootstrap",
        Path(__file__).parent.parent / "config",
    ],
)

# Add routing configurations to the application.
app.withRouting(
    console=Path(__file__).parent.parent / "routes" / "console.py",
    health="/up",
)

# Add a custom command scheduler to the application.
app.withScheduler(Scheduler)

# Set a global custom exception handler.
app.withExceptionHandler(ExceptionHandler)

# Register service providers with the application.
app.withProviders([
    WelcomeProvider,
])

# Boot the application.
app.create()