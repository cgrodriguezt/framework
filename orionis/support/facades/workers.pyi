from orionis.services.system.contracts.workers import IWorkers

class Workers(IWorkers):

    @classmethod
    async def init(cls) -> None:
        ...