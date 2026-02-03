from orionis.container.facades.facade import Facade

class CLIRequest(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """Get the facade accessor string for the CLI request service.

        Returns
        -------
        str
            The facade accessor identifier for the CLI request service.
        """
        return "x-orionis.console.contracts.cli_request.ICLIRequest"
