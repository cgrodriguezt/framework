from orionis.console.contracts.schedule import ISchedule
from orionis.container.facades.facade import Facade

class Schedule(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> type:
        """
        Return the facade accessor type for the schedule contract.

        Returns
        -------
        type
            Type identifier for the schedule contract.
        """
        return ISchedule
