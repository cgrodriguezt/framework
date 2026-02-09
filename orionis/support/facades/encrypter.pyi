from orionis.services.encrypter.contracts.encrypter import IEncrypter

class Crypt(IEncrypter):

    @classmethod
    async def init(cls) -> None:
        ...