from dataclasses import asdict, dataclass, field
from pathlib import Path
from orionis.luminate.foundation.skeletom.exceptions.integrity import SkeletomIntegrityException

@dataclass(frozen=True, kw_only=True)
class RootConsole:
    """
    Root configuration for the console kernel and command registration paths.

    Attributes
    ----------
    path_kernel : str
        Path to the console kernel file. This file defines scheduled tasks and command bindings.
    path_commands : str
        Path to the directory containing custom command definitions.
    """

    path_kernel: str = field(
        default='app/console/kernel.py',
        metadata={
            'description': 'Path to the console kernel file. This file defines scheduled tasks and command bindings.'
        }
    )

    path_commands: str = field(
        default='app/console/commands',
        metadata={
            'description': 'Path to the directory containing custom command definitions.'
        }
    )

    def __post_init__(self):
        """
        Validates the initialization of RootConsole fields.

        Ensures that `path_kernel` is a string pointing to a Python file,
        and `path_commands` is a string pointing to an existing directory.

        Raises:
            SkeletomIntegrityException: If any validation fails.
        """
        if not isinstance(self.path_kernel, str):
            raise SkeletomIntegrityException("path_kernel must be a string.")
        if not isinstance(self.path_commands, str):
            raise SkeletomIntegrityException("path_commands must be a string.")

        kernel_path = Path(self.path_kernel)
        commands_path = Path(self.path_commands)

        if kernel_path.suffix != '.py':
            raise SkeletomIntegrityException(
                f"path_kernel must be a Python file with '.py' extension (got: {self.path_kernel})"
            )

        if not commands_path.exists() or not commands_path.is_dir():
            raise SkeletomIntegrityException(
                f"path_commands must exist and be a directory (got: {self.path_commands})"
            )

    def getKernelPath(self) -> Path:
        """
        Returns the filesystem path to the kernel directory.
        Returns:
            Path: The path object representing the kernel directory.
        """
        return Path(self.path_kernel)

    def getCommandsPath(self) -> Path:
        """
        Returns the path to the commands directory as a Path object.

        Returns:
            Path: The path to the commands directory.
        """
        return Path(self.path_commands)

    def toDict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        Returns:
            dict: A dictionary representation of the Dataclass object.
        """
        return asdict(self)