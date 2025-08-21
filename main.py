from pathlib import Path
from orionis.app import Orionis
from app.console.scheduler import Scheduler

"""
Initializes and configures an Orionis application instance for testing.

This script creates an instance of the Orionis application, configures it for a testing environment
by setting the execution mode to sequential, disabling persistence, and turning off web reporting.
Finally, it initializes the application instance.

Attributes
----------
app : Orionis
    Instance of the Orionis application, configured for testing.
"""

# Create and configure the Orionis application instance
app = Orionis()

# Set the scheduler for the application
app.setScheduler(Scheduler)

# Configure the global application settings
app.setConfigApp(
    timezone="America/Bogota",
    debug=True
)

# Configure the paths for the application
app.setPaths(
    root=Path().cwd(),
)

# Configure the logging settings
app.setConfigLogging(
    default='stack'
)

# Configure the application for testing
app.setConfigTesting(
    execution_mode="sequential",
    persistent=False,
    web_report=False
)

# Initialize the application
app.create()