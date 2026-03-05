from orionis.container.facades.facade import Facade

class Crypt(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the encrypter service.

        Returns
        -------
        str
            The string identifier for the encrypter service contract.
        """
        return "x-orionis-IEncrypter"
