from orionis.services.log.contracts.log_service import ILogger

class Log(ILogger):

    @classmethod
    async def init(cls) -> None:
        ...