from orionis.failure.contracts.catch import ICatch

class Catch(ICatch):

    @classmethod
    async def init(cls) -> None:
        ...

