from orionis.services.inspirational.contracts.inspire import IInspire

class Inspire(IInspire):

    @classmethod
    async def init(cls) -> None:
        ...