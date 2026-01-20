import pendulum
from pendulum.datetime import DateTime as PendulumDateTime
from orionis.foundation.contracts.application import IApplication
from orionis.support.time.contracts.datetime import IDateTime

class DateTime(IDateTime):

    def __init__(self, app: IApplication):
        """
        Initialize DateTime with application's timezone configuration.

        Parameters
        ----------
        app : IApplication
            Application instance providing configuration access.

        Sets
        ----
        self.__timezone : str
            Timezone from application's configuration, defaults to 'UTC'
            if not specified.

        Returns
        -------
        None
        """
        # Retrieve timezone from application config, default to 'UTC'
        self.__timezone = app.config("app.timezone") or "UTC"

    def now(self) -> PendulumDateTime:
        """
        Get current date and time in configured timezone.

        Uses pendulum to obtain current datetime object based on
        instance's timezone.

        Returns
        -------
        datetime
            Current datetime in the specified timezone.
        """
        # Return current datetime in the configured timezone
        return pendulum.now(self.__timezone)
