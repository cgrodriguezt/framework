from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Callable

# Synchronous callable that receives raw bytes and returns a parsed object.
BodyParser = Callable[[bytes], object]

class IMediaTypeRegistry(ABC):
    """
    Define the contract for a media-type-to-parser registry.

    Implementations map lowercased media-type strings to synchronous
    ``BodyParser`` callables and support non-destructive extension.
    """

    @abstractmethod
    def register(self, media_type: str, parser: BodyParser) -> None:
        """Add or replace the parser for *media_type* in place."""

    @abstractmethod
    def get(self, media_type: str) -> BodyParser | None:
        """Return the parser registered for *media_type*, or ``None``."""

    @abstractmethod
    def extend(self, parsers: dict[str, BodyParser]) -> IMediaTypeRegistry:
        """Return a new registry that merges *parsers* over a copy of self."""
