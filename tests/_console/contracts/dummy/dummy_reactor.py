from orionis.console.contracts.reactor import IReactor
from unittest.mock import MagicMock

class DummyCommand:
    def __init__(self):
        self.called = False
        self.args = None

    def handle(self, *args, **kwargs):
        """
        Handles the command execution.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the command.
        **kwargs : dict
            Keyword arguments passed to the command.

        Returns
        -------
        str
            Returns the string "handled" after setting the called flag and storing the arguments.
        """
        self.called = True
        self.args = args
        return "handled"

class DummyReactor(IReactor):
    def __init__(self):
        # Stores command signatures mapped to their handler objects
        self._commands = {}

    def command(self, signature, handler):
        """
        Registers a command handler with a given signature.

        Parameters
        ----------
        signature : str
            The unique identifier for the command.
        handler : object
            The handler object that processes the command.

        Returns
        -------
        unittest.mock.MagicMock
            Returns a MagicMock instance simulating the ICommand interface.
        """
        self._commands[signature] = handler
        return MagicMock()  # Simulates ICommand

    def info(self):
        """
        Retrieves information about all registered commands.

        Returns
        -------
        list of dict
            A list of dictionaries, each containing the signature, description, and timestamps flag for a command.
        """
        return [{"signature": k, "description": "desc", "timestamps": False} for k in self._commands]

    def call(self, signature, args=None):
        """
        Calls the handler for the given command signature synchronously.

        Parameters
        ----------
        signature : str
            The signature of the command to call.
        args : list or None, optional
            Arguments to pass to the handler (default is None).

        Returns
        -------
        object or None
            The result of the handler's handle method if the signature exists, otherwise None.
        """
        handler = self._commands.get(signature)
        if handler:
            return handler.handle(*(args or []))
        return None

    async def callAsync(self, signature, args=None):
        """
        Calls the handler for the given command signature asynchronously.

        Parameters
        ----------
        signature : str
            The signature of the command to call.
        args : list or None, optional
            Arguments to pass to the handler (default is None).

        Returns
        -------
        object or None
            The result of the handler's handle method if the signature exists, otherwise None.
        """
        handler = self._commands.get(signature)
        if handler:
            return handler.handle(*(args or []))
        return None
