from orionis.console.contracts.reactor import IReactor
from orionis.test.cases.asynchronous import AsyncTestCase

class TestConsoleReactor(AsyncTestCase):

    async def onAsyncSetup(self, reactor: IReactor):
        self.reactor = reactor
        self.dd(str(self.reactor))