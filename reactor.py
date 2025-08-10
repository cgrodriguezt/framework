import sys
from main import app
from orionis.console.contracts.kernel import IKernelCLI

# Resolve the test kernel instance from the application container
kernel: IKernelCLI = app.make(IKernelCLI)

kernel.handle(sys.argv)