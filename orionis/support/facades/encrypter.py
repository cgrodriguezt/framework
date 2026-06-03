from orionis.container.facades.facade import Facade
from orionis.services.encrypter.contracts.encrypter import IEncrypter

class Crypt(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> type:
        """
        Return the facade accessor type for the encrypter service.

        Returns
        -------
        type
            The type of the service that this facade provides access to, which is IEncrypter
        """
        return IEncrypter
