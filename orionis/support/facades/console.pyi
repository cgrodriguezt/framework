from orionis.console.output.contracts.console import IConsole

class Console(IConsole):

    @classmethod
    async def init(cls) -> None:
        ...
