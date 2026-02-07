import asyncio
from pathlib import Path
from app.console.scheduler import Scheduler
from app.exceptions.handler import ExceptionHandler
from app.providers.welcome_provider import WelcomeProvider
from orionis import Application, IApplication

# Determine the root directory of the application.
root = Path(__file__).parent.parent

# Initialize the application instance.
app: IApplication = Application()

# Configure the application cache directory.
app.withCache(
    path=(root / "storage" / "framework" / "cache" / "bootstrap"),
    monitored_dirs=[
        root / "app",
        root / "bootstrap",
        root / "config",
        root / "routes",
    ],
    monitored_files=[
        root / ".env",
    ]
)

# Add routing configurations to the application.
app.withRouting(
    console=root / "routes" / "console.py",
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
