from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.cache.entities.file import File
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Stores(BaseEntity):
    """
    Represent a collection of cache storage backends for the application.

    Attributes
    ----------
    file : File | dict
        An instance of `File` representing file-based cache storage. The default
        path is set to 'storage/framework/cache/data', resolved relative to the
        application's root directory.
    """

    file: File | dict = field(
        default_factory=lambda: File(),
        metadata={
            "description": "An instance of `File` representing file-based cache "
            "storage.",
            "default": lambda: File().toDict(),
        },
    )

    def __post_init__(self: Stores) -> None:
        """
        Validate and initialize the 'file' attribute after object creation.

        Ensure that the 'file' attribute is an instance of File or dict. If a dict
        is provided, convert it to a File instance.

        Parameters
        ----------
        self : Stores
            The instance of the Stores class.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If 'file' is not an instance of File or dict.
        """
        # Call the superclass post-initialization method
        super().__post_init__()

        # Validate and convert the 'file' attribute
        if not isinstance(self.file, (File, dict)):
            error_msg = (
                "The 'file' attribute must be an instance of File or a dict, "
                f"but got {type(self.file).__name__}."
            )
            raise TypeError(error_msg)

        # Convert dict to File instance if necessary
        if isinstance(self.file, dict):
            object.__setattr__(self, "file", File(**self.file))
