from orionis.container.facades.facade import Facade

class Directory(Facade):

    @classmethod
    def getFacadeAccessor(cls):
        """
        Returns the unique binding key for the directory service in the container.

        Returns
        -------
        str
            The binding key for the IDateTime contract.
        """

        # Return the unique binding key for the directory service in the container
        return "x-orionis.support.time.contracts.datetime.IDateTime"