from orionis.services.log.contracts.log_service import ILogger

class DummyLogger(ILogger):

    def __init__(self):
        """
        Initializes the DummyLogger instance.

        This constructor creates an empty list to store log messages that are
        received by the logger. The list is used internally to keep track of
        all messages logged through the various logging methods.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value.
        """
        # Initialize an empty list to store log messages
        self.logs = []

    def debug(self, msg):
        """
        Logs a debug message.

        Appends the provided debug message to the internal logs list for later
        inspection or testing purposes.

        Parameters
        ----------
        msg : str
            The debug message to be logged.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Add the debug message to the logs list
        self.logs.append(msg)

    def info(self, msg):
        """
        Logs an informational message.

        Appends the provided informational message to the internal logs list.

        Parameters
        ----------
        msg : str
            The informational message to log.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Add the informational message to the logs list
        self.logs.append(msg)

    def warning(self, msg):
        """
        Logs a warning message.

        Appends the provided warning message to the internal logs list.

        Parameters
        ----------
        msg : str
            The warning message to be logged.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Add the warning message to the logs list
        self.logs.append(msg)

    def error(self, msg):
        """
        Logs an error message.

        Appends the provided error message to the internal logs list.

        Parameters
        ----------
        msg : str
            The error message to log.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Add the error message to the logs list
        self.logs.append(msg)