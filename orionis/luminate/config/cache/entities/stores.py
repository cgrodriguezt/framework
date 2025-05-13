from dataclasses import dataclass, field
from typing import Any
from orionis.luminate.config.cache.entities.file import File
from orionis.luminate.services.paths.resolver import Resolver

@dataclass
class Stores:
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
        default_factory=lambda: File(
            path=Resolver().relativePath('storage/framework/cache/data').toString()
        ),
        metadata={
            "description": "An instance of `File` representing file-based cache storage.",
            "type": File,
        },
    )

    def __post_init__(self):
        """
        Post-initialization processing to ensure the stores are set correctly.
        """
        if not isinstance(self.file, File):
            raise TypeError("The file store must be an instance of File.")