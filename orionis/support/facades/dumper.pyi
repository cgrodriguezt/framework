from orionis.console.debug.contracts.dumper import IDumper

class Dumper(IDumper):

    @classmethod
    async def init(cls) -> None:
        ...
