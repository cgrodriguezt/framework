from orionis.console.contracts.cli_request import ICLIRequest

class DummyCLIRequest(ICLIRequest):
    """
    Dummy implementation of the ICLIRequest interface for CLI command handling.
    Parameters
    ----------
    command : str
        The command name or identifier.
    args : dict, optional
        Dictionary of command arguments (default is None).
    Attributes
    ----------
    _command : str
        Stores the command name.
    _args : dict
        Stores the command arguments.
    Methods
    -------
    command() -> str
        Returns the command name.
    all() -> dict
        Returns all command arguments as a dictionary.
    argument(name: str, default=None)
        Retrieves the value of a specific argument by name, or returns the default if not found.
    getCWD() -> str
        Returns the current working directory.
    getPID() -> int
        Returns the current process ID.
    getParentPID() -> int
        Returns the parent process ID.
    getExecutable() -> str
        Returns the path to the Python executable.
    getPlatform() -> str
        Returns the name of the operating system platform.
    """

    def __init__(self, command, args=None):
        self._command = command
        self._args = args or {}

    def command(self) -> str:
        return self._command

    def all(self) -> dict:
        return self._args

    def argument(self, name: str, default=None):
        return self._args.get(name, default)

    def getCWD(self) -> str:
        import os
        return os.getcwd()

    def getPID(self) -> int:
        import os
        return os.getpid()

    def getParentPID(self) -> int:
        import os
        return os.getppid()

    def getExecutable(self) -> str:
        import sys
        return sys.executable

    def getPlatform(self) -> str:
        import platform
        return platform.system()