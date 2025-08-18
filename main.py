from orionis.app import Orionis

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

# Configure the global application settings
app.setConfigApp(
    timezone="America/Bogota"
)

# Configure the application for testing
app.setConfigTesting(
    execution_mode="sequential",
    persistent=False,
    web_report=False
)

# Initialize the application
app.create()