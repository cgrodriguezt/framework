from orionis.container.facades.facade import Facade

class Directory(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the directory service.

        Returns
        -------
        str
            The string identifier for the directory service contract.
        """
        # Return the service contract identifier for the directory facade
        return "x-orionis.services.file.contracts.directory.IDirectory"
