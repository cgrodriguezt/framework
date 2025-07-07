from orionis import Orionis, IOrionis
from orionis.test.contracts.kernel import ITestKernel

app: IOrionis = Orionis()
app.load([
    # Add your service providers here
])