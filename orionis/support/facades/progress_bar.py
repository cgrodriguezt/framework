from orionis.container.facades.facade import Facade

class ProgressBar(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the progress bar.

        Returns
        -------
        str
            The string identifier for the progress bar contract.
        """
        # Provide the contract identifier for the progress bar facade
        return "x-orionis.console.contracts.progress_bar.IProgressBar"
