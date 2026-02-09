from orionis.support.performance.contracts.counter import IPerformanceCounter

class PerformanceCounter(IPerformanceCounter):

    @classmethod
    async def init(cls) -> None:
        ...