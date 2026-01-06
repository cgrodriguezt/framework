from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.filesystems.entitites.aws import S3
from orionis.foundation.config.filesystems.entitites.local import Local
from orionis.foundation.config.filesystems.entitites.public import Public
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Disks(BaseEntity):
    """
    Represent the configuration for different filesystem disks.

    Attributes
    ----------
    local : Local | dict
        The disk configuration for local file storage.
    public : Public | dict
        The disk configuration for public file storage.
    aws : S3 | dict
        The configuration for AWS S3 storage.
    """

    local: Local | dict = field(
        default_factory=lambda: Local(),
        metadata={
            "description": (
                "The absolute or relative path where local files are stored."
            ),
            "default": lambda: Local().toDict(),
        },
    )

    public: Public | dict = field(
        default_factory=lambda: Public(),
        metadata={
            "description": (
                "The absolute or relative path where public files are stored."
            ),
            "default": lambda: Public().toDict(),
        },
    )

    aws: S3 | dict = field(
        default_factory=lambda: S3(),
        metadata={
            "description": "The configuration for AWS S3 storage.",
            "default": lambda: S3().toDict(),
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and convert disk attributes after initialization.

        Ensures that 'local', 'public', and 'aws' attributes are instances of
        their respective classes. Converts from dict if necessary.

        Parameters
        ----------
        self : Disks
            The instance of the Disks class.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Call the superclass post-init method
        super().__post_init__()

        # Validate and convert the 'local' attribute if needed
        if not isinstance(self.local, (Local, dict)):
            error_msg = (
                "The 'local' attribute must be a Local object or a dictionary."
            )
            raise TypeError(error_msg)
        if isinstance(self.local, dict):
            object.__setattr__(self, "local", Local(**self.local))

        # Validate and convert the 'public' attribute if needed
        if not isinstance(self.public, (Public, dict)):
            error_msg = (
                "The 'public' attribute must be a Public object or a dictionary."
            )
            raise TypeError(error_msg)
        if isinstance(self.public, dict):
            object.__setattr__(self, "public", Public(**self.public))

        # Validate and convert the 'aws' attribute if needed
        if not isinstance(self.aws, (S3, dict)):
            error_msg = (
                "The 'aws' attribute must be an S3 object or a dictionary."
            )
            raise TypeError(error_msg)
        if isinstance(self.aws, dict):
            object.__setattr__(self, "aws", S3(**self.aws))
