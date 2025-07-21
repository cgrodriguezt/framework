from dataclasses import dataclass, field
from orionis.foundation.config.cache.entities.file import File
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.support.entities.base import BaseEntity

@dataclass(unsafe_hash=True, kw_only=True)
class Stores(BaseEntity):
    """
    Represents a collection of cache storage backends for the application.

    Attributes:
        file (File): An instance of `File` representing file-based cache storage.
            The default path is set to 'storage/framework/cache/data', resolved
            relative to the application's root directory.

    Methods:
        __post_init__():
            Ensures that the 'file' attribute is properly initialized as an instance of `File`.
            Raises a TypeError if the type check fails.
    """

    file: File = field(
        default_factory = lambda: File(),
        metadata = {
            "description": "An instance of `File` representing file-based cache storage.",
            "default": lambda: File().toDict()
        },
    )

    def __post_init__(self):
        """
        Post-initialization method to validate the 'file' attribute.

        Ensures that the 'file' attribute is an instance of the File class.

        Raises:
            OrionisIntegrityException: If 'file' is not an instance of File, with a descriptive error message.
        """
        if not isinstance(self.file, File):
            raise OrionisIntegrityException(
                f"The 'file' attribute must be an instance of File, but got {type(self.file).__name__}."
            )