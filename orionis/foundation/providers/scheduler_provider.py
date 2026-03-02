from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.console.contracts.schedule import ISchedule
from orionis.console.tasks.schedule import Schedule

class ScheduleProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the Scheduler as a singleton service in the application container.

        Binds the `ISchedule` interface to the `Schedule` implementation, ensuring a
        single instance throughout the application's lifecycle. Also provides an alias
        for convenient access.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs registration as a side effect and returns None.
        """
        self.app.singleton(
            abstract=ISchedule,
            concrete=Schedule,
            alias="x-orionis.console.contracts.schedule.ISchedule",
        )

    def provides(self) -> list[type]:
        """
        Specify the services provided by this provider.

        Returns a list of services that this provider is responsible for, indicating
        that it offers the `ISchedule` service.

        Parameters
        ----------
        None

        Returns
        -------
        list of type
            A list containing the `ISchedule` service provided by this provider.
        """
        return [ISchedule]
