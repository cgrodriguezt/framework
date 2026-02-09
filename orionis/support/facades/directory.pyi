from orionis.services.file.contracts.directory import IDirectory

class Directory(IDirectory):

    @classmethod
    async def init(cls) -> None:
        ...
