class DummyConcrete:
    """
    DummyConcrete is a simple class that demonstrates basic method structure.

    Methods
    -------
    handle()
        Executes the main logic for the command and returns a status string.
    custom()
        Returns a string indicating a custom action.
    """

    def handle(self):
        """
        Executes the main logic for the command.

        Returns
        -------
        str
            The string "handled", indicating that the handle action was performed successfully.
        """

        # Perform the main handling logic and return a status string
        return "handled"

    def custom(self):
        """
        Returns a string indicating a custom action.

        Returns
        -------
        str
            The string "custom", indicating that a custom action was performed.
        """

        # Return a string to indicate a custom action
        return "custom"