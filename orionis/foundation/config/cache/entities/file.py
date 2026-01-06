from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class File(BaseEntity):
    """
    Represent the configuration entity for a file-based cache store.

    Attributes
    ----------
    path : str
        The file system path where cache data will be stored. Defaults to
        'storage/framework/cache/data'.
    """

    path: str = field(
        default="storage/framework/cache/data",
        metadata={
            "description": (
                "The configuration for available cache stores. Defaults to a file "
                "store at the specified path."
            ),
            "default": "storage/framework/cache/data",
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and initialize the 'path' attribute after dataclass initialization.

        Ensure that the 'path' attribute is a non-empty string and create the
        directory if it does not exist.

        Parameters
        ----------
        self : File
            Instance of the File entity being initialized.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__post_init__()

        # Ensure 'path' is not empty
        if not self.path:
            error_msg = (
                "File cache configuration error: 'path' cannot be empty. "
                "Please provide a valid file path."
            )
            raise ValueError(error_msg)

        # Ensure 'path' is a string
        if not isinstance(self.path, str):
            error_msg = (
                "File cache configuration error: 'path' must be a string, "
                f"got {type(self.path).__name__}."
            )
            raise TypeError(error_msg)

        # Create the directory if it does not exist
        Path(self.path).mkdir(parents=True, exist_ok=True)
