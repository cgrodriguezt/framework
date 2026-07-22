from __future__ import annotations
import markdown
import msgspec
import msgspec.json as msgspec_json
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

# ruff: noqa: ANN401

def _jsonify(value: Any, indent: int | None = None) -> str:
    """
    Serialise a value to a JSON string.

    Parameters
    ----------
    value : Any
        Value to serialise.  Must be JSON-serialisable.
    indent : int | None, optional
        If provided, pretty-prints the output with the given indentation.

    Returns
    -------
    str
        JSON-encoded string.
    """
    try:
        encoded = msgspec_json.encode(value)
        if indent is not None:
            encoded = msgspec_json.format(encoded, indent=indent)
        return encoded.decode()
    except (TypeError, ValueError, msgspec.EncodeError):
        return str(value)

def _markdown(value: Any) -> str:
    """
    Render a Markdown string to HTML.

    Requires the ``markdown`` package.  When the package is not installed
    the original string is returned unchanged.

    Parameters
    ----------
    value : Any
        Markdown-formatted string to convert.

    Returns
    -------
    str
        HTML-rendered string, or the original string when ``markdown``
        is unavailable.
    """
    return markdown.markdown(
        str(value),
        extensions=["extra", "codehilite", "toc"],
    )

def buildViewFilters() -> dict[str, Callable[..., Any]]:
    """
    Build and return the mapping of template filter names to callables.

    Returns
    -------
    dict[str, Callable[..., Any]]
        Mapping of filter names to their callable implementations.
    """
    return {
        "json": _jsonify,
        "markdown": _markdown,
    }
