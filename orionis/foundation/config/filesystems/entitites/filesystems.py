from __future__ import annotations
from dataclasses import dataclass, field, fields
from orionis.foundation.config.filesystems.entitites.disks import Disks
from orionis.services.environment.env import Env
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Filesystems(BaseEntity):
    """
    Represent the filesystems configuration.

    Attributes
    ----------
    default : str
        The default filesystem disk to use.
    disks : Disks | dict
        A collection of available filesystem disks.
    """

    default: str = field(
        default_factory=lambda: Env.get("FILESYSTEM_DISK", "local"),
        metadata={
            "description": "The default filesystem disk to use.",
            "default": lambda: Env.get("FILESYSTEM_DISK", "local"),
        },
    )

    disks: Disks | dict = field(
        default_factory=lambda: Disks(),
        metadata={
            "description": "A collection of available filesystem disks.",
            "default": lambda: Disks().toDict(),
        },
    )

    def __post_init__(self) -> None:
        """
        Validate the types of attributes after initialization.

        Parameters
        ----------
        self : Filesystems
            The instance of the Filesystems class.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__post_init__()

        # Validate the 'default' property against available disk options.
        options = [f.name for f in fields(Disks)]
        if not isinstance(self.default, str) or self.default not in options:
            error_msg = (
                f"The 'default' property must be a string and match one of the "
                f"available options ({options})."
            )
            raise ValueError(error_msg)

        # Ensure 'disks' is either a Disks instance or a dictionary.
        if not isinstance(self.disks, (Disks, dict)):
            error_msg = (
                "The 'disks' property must be an instance of Disks or a dictionary."
            )
            raise TypeError(error_msg)
        # Convert dict to Disks instance if necessary.
        if isinstance(self.disks, dict):
            object.__setattr__(self, "disks", Disks(**self.disks))
