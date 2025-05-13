from dataclasses import dataclass, field
from orionis.luminate.services.paths import Resolver

@dataclass
class File:
    """
    Represents a file storage path.

    Attributes
    ----------
    path : str
        The file path used for caching.
    """
    path: str = field(
        default_factory=lambda:Resolver().relativePath('storage/framework/cache/data').toString(),
        metadata={
            "description": "The file path used for caching.",
            "type": str,
        },
    )

    def __post_init__(self):
        """
        Post-initialization processing to ensure the path is set correctly.
        """
        if not self.path:
            raise ValueError("The file path cannot be empty.")
        if not isinstance(self.path, str):
            raise TypeError("The file path must be a string.")