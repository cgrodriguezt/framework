from orionis.foundation.application import Application
from orionis.foundation.contracts.application import IApplication

# Initialize and create the application instance
app: IApplication = Application()

# Create the application (set up configurations, services, etc.)
app.create()