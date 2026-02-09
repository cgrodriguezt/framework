from orionis.console.request.contracts.cli_request import ICLIRequest

class CLIRequest(ICLIRequest):

    @classmethod
    async def init(cls) -> None:
        ...
