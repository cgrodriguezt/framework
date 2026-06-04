from __future__ import annotations
from typing import TYPE_CHECKING
from urllib.parse import parse_qsl
import msgspec.json as _msgspec_json
import msgspec.msgpack as _msgspec_msgpack
from defusedxml.ElementTree import fromstring as _xml_fromstring

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element as XMLElement

def parse_content_type(header: str) -> tuple[str, dict[str, str]]:
    """
    Parse a ``Content-Type`` header into a media-type and parameter dict.

    Parameters
    ----------
    header : str
        Raw ``Content-Type`` value, e.g.
        ``"multipart/form-data; boundary=----WebKit"``.

    Returns
    -------
    tuple[str, dict[str, str]]
        ``(media_type, params)`` where *media_type* is lowercase and
        *params* maps lowercase parameter names to unquoted values.
    """
    parts = header.split(";")
    media_type = parts[0].strip().lower()
    params: dict[str, str] = {}
    for part in parts[1:]:
        if "=" in part:
            key, _, value = part.strip().partition("=")
            params[key.strip().lower()] = value.strip().strip('"')
    return media_type, params


def parse_json(raw: bytes) -> object:
    """
    Decode a JSON payload using ``msgspec``.

    Parameters
    ----------
    raw : bytes
        Raw JSON bytes.

    Returns
    -------
    object
        Decoded Python object (dict, list, str, int, float, bool, or None).

    Raises
    ------
    msgspec.DecodeError
        If *raw* is not valid JSON.
    """
    return _msgspec_json.decode(raw)


def parse_msgpack(raw: bytes) -> object:
    """
    Decode a MessagePack payload.

    Parameters
    ----------
    raw : bytes
        Raw MessagePack bytes.

    Returns
    -------
    object
        Decoded Python object.

    Raises
    ------
    msgspec.DecodeError
        If *raw* is not valid MessagePack.
    """
    return _msgspec_msgpack.decode(raw)


def parse_urlencoded(raw: bytes) -> dict[str, str]:
    """
    Decode an ``application/x-www-form-urlencoded`` payload.

    Parameters
    ----------
    raw : bytes
        URL-encoded bytes.

    Returns
    -------
    dict[str, str]
        Parsed key-value pairs with blank values preserved.
    """
    return dict(parse_qsl(raw.decode("utf-8"), keep_blank_values=True))


def parse_xml(raw: bytes) -> XMLElement:
    """
    Parse an XML payload using ``defusedxml`` to prevent XXE / DTD attacks.

    Parameters
    ----------
    raw : bytes
        Raw XML bytes.

    Returns
    -------
    xml.etree.ElementTree.Element
        Root element of the parsed document.

    Raises
    ------
    xml.etree.ElementTree.ParseError
        If *raw* is malformed or contains forbidden constructs.
    """
    return _xml_fromstring(raw)


def parse_text(raw: bytes) -> str:
    """
    Decode a UTF-8 text payload.

    Parameters
    ----------
    raw : bytes
        Raw body bytes.

    Returns
    -------
    str
        UTF-8 decoded string.
    """
    return raw.decode("utf-8")


def parse_binary(raw: bytes) -> bytes:
    """
    Return a binary payload unchanged.

    Parameters
    ----------
    raw : bytes
        Raw body bytes.

    Returns
    -------
    bytes
        The same bytes object, unmodified.
    """
    return raw
