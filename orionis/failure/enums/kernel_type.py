from enum import Enum, auto

class KernelType(Enum):
    """
    Define available kernel types in the system.

    Attributes
    ----------
    CONSOLE : KernelType
        Kernel for command-line or console execution.
    HTTP : KernelType
        Kernel for HTTP environments, such as web servers.

    Returns
    -------
    KernelType
        An instance of the KernelType enumeration.
    """

    # Kernel for command-line or console execution
    CONSOLE = auto()

    # Kernel for HTTP environments, such as web servers
    HTTP = auto()
