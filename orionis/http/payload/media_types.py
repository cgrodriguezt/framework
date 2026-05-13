from __future__ import annotations
from collections.abc import Callable
from orionis.http.payload.parsers import (
    parse_binary,
    parse_json,
    parse_msgpack,
    parse_text,
    parse_urlencoded,
    parse_xml,
)
from orionis.http.payload.contracts.media_types import IMediaTypeRegistry

# Synchronous callable that receives raw bytes and returns a parsed object.
BodyParser = Callable[[bytes], object]

class MediaTypeRegistry(IMediaTypeRegistry):
    """
    Map lowercased media-type strings to synchronous ``BodyParser`` callables.

    ``multipart/form-data`` is intentionally absent: multipart parsing
    requires a *streaming* body rather than pre-buffered ``bytes``.
    ``Request.payload()`` handles that case explicitly before consulting
    this registry.

    Parameters
    ----------
    parsers : dict[str, BodyParser] | None
        Initial mapping of media types to parsers.  Keys are lowercased
        automatically.  Defaults to an empty mapping.
    """

    __slots__ = ("_parsers",)

    def __init__(self, parsers: dict[str, BodyParser] | None = None) -> None:
        """
        Initialize the registry with an optional mapping of media types.

        Parameters
        ----------
        parsers : dict[str, BodyParser] | None
            Initial media-type-to-parser mapping.  Keys are lowercased
            on ingestion.  Pass ``None`` to start with an empty registry.

        Returns
        -------
        None
        """
        self._parsers: dict[str, BodyParser] = (
            {k.lower(): v for k, v in parsers.items()} if parsers else {}
        )

    def register(self, media_type: str, parser: BodyParser) -> None:
        """
        Add or replace the parser for *media_type* in place.

        Parameters
        ----------
        media_type : str
            Case-insensitive media-type string, e.g. ``"application/json"``.
        parser : BodyParser
            Synchronous callable ``(bytes) -> object``.

        Returns
        -------
        None
        """
        self._parsers[media_type.lower()] = parser

    def get(self, media_type: str) -> BodyParser | None:
        """
        Return the parser registered for *media_type*, or ``None``.

        Parameters
        ----------
        media_type : str
            Case-insensitive media-type string.

        Returns
        -------
        BodyParser | None
            The registered ``(bytes) -> object`` callable, or ``None``
            when *media_type* has no registered parser.
        """
        return self._parsers.get(media_type.lower())

    def extend(self, parsers: dict[str, BodyParser]) -> MediaTypeRegistry:
        """Return a new registry that merges *parsers* over a copy of self.

        The original registry is not mutated.  Use this pattern for
        middleware or provider-level overrides.

        Parameters
        ----------
        parsers : dict[str, BodyParser]
            Additional or replacement media-type-to-parser entries.

        Returns
        -------
        MediaTypeRegistry
            New registry containing all entries from self plus *parsers*.
        """
        merged = {
            **self._parsers,
            **{k.lower(): v for k, v in parsers.items()},
        }
        return MediaTypeRegistry(merged)


# ---------------------------------------------------------------------------
# Default registry (module-level singleton)
# ---------------------------------------------------------------------------

DEFAULT_MEDIA_TYPES: MediaTypeRegistry = MediaTypeRegistry(
    {
        "application/json": parse_json,
        "application/x-www-form-urlencoded": parse_urlencoded,
        "application/msgpack": parse_msgpack,
        "application/xml": parse_xml,
        "text/xml": parse_xml,
        "text/html": parse_text,
        "text/plain": parse_text,
        "application/javascript": parse_text,
        "text/javascript": parse_text,
        "application/octet-stream": parse_binary,
    },
)
