from orionis.foundation.application import Orionis
from orionis.foundation.contracts.application import IApplication

app: IApplication = Orionis()
app.load([
    # Add your service providers here
])
