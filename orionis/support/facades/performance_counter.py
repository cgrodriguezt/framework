from orionis.container.facades.facade import Facade

class PerformanceCounter(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the performance counter.

        Returns
        -------
        str
            The string identifier for the performance counter facade accessor.
        """
        # Return the contract string for the performance counter
        return "x-orionis.support.performance.contracts.counter.IPerformanceCounter"
