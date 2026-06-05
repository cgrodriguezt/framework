from __future__ import annotations
from typing import TYPE_CHECKING, Self
from orionis.http.payload.contracts.form_data import IFormData

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType
    from orionis.http.payload.uploaded_file import UploadedFile

class FormData(IFormData):
    """
    Hold parsed multipart form fields and uploaded files as an ordered sequence.

    Supports multiple values under the same field name (e.g. multi-select
    or repeated ``<input>`` elements with the same ``name`` attribute).
    Implements the context-manager protocol to guarantee that all open file
    handles are released when the block exits.
    """

    __slots__ = ("_items",)

    def __init__(
        self,
        items: list[tuple[str, str | UploadedFile]],
    ) -> None:
        """
        Initialize FormData from an ordered list of ``(name, value)`` pairs.

        Parameters
        ----------
        items : list[tuple[str, str | UploadedFile]]
            Ordered sequence of ``(field_name, value)`` pairs as produced
            by the multipart stream parser.  Multiple pairs with the same
            name are preserved in insertion order.

        Returns
        -------
        None
        """
        self._items: list[tuple[str, str | UploadedFile]] = list(items)

    # ---- Backward-compatible grouped views ----

    @property
    def fields(self) -> dict[str, list[str]]:
        """
        Return all text field values grouped by name.

        Returns
        -------
        dict[str, list[str]]
            Mapping of field names to all their string values in insertion order.
        """
        result: dict[str, list[str]] = {}
        for k, v in self._items:
            if isinstance(v, str):
                result.setdefault(k, []).append(v)
        return result

    @property
    def files(self) -> dict[str, list[UploadedFile]]:
        """
        Return all uploaded file values grouped by name.

        Returns
        -------
        dict[str, list[UploadedFile]]
            Mapping of field names to all their ``UploadedFile`` instances
            in insertion order.
        """
        result: dict[str, list[UploadedFile]] = {}
        for k, v in self._items:
            if not isinstance(v, str):
                result.setdefault(k, []).append(v)  # type: ignore[arg-type]
        return result

    # ---- Retrieval ----

    def get(self, key: str, default: object | None = None) -> object | None:
        """
        Return the last value for *key*, or *default*.

        Scanning in reverse means the most-recently-appended value for a
        repeated field name is returned, which mirrors HTML form semantics.

        Parameters
        ----------
        key : str
            Field name to look up.
        default : object | None, optional
            Fallback when *key* is absent.  Defaults to ``None``.

        Returns
        -------
        object | None
            Last ``str`` or ``UploadedFile`` value for *key*, or *default*.
        """
        for k, v in reversed(self._items):
            if k == key:
                return v
        return default

    def getAll(self, key: str) -> list[str | UploadedFile]:
        """
        Return every value for *key* in insertion order.

        Parameters
        ----------
        key : str
            Field name to look up.

        Returns
        -------
        list[str | UploadedFile]
            All values associated with *key*, or an empty list if absent.
        """
        return [v for k, v in self._items if k == key]

    def multiItems(self) -> list[tuple[str, str | UploadedFile]]:
        """
        Return all ``(name, value)`` pairs in insertion order.

        Returns
        -------
        list[tuple[str, str | UploadedFile]]
            A copy of the underlying item sequence.
        """
        return list(self._items)

    # ---- Mapping protocol ----

    def __getitem__(self, key: str) -> object:
        """
        Return the last value for *key* using subscript notation.

        Parameters
        ----------
        key : str
            Field name to retrieve.

        Returns
        -------
        object
            Last value for *key*, or ``None`` if absent.
        """
        return self.get(key)

    def __contains__(self, key: str) -> bool:
        """
        Return ``True`` if at least one item with *key* exists.

        Parameters
        ----------
        key : str
            Field name to check.

        Returns
        -------
        bool
        """
        return any(k == key for k, _ in self._items)

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over unique field names in first-seen insertion order.

        Returns
        -------
        Iterator[str]
            Each unique field name exactly once.
        """
        seen: set[str] = set()
        for k, _ in self._items:
            if k not in seen:
                seen.add(k)
                yield k

    def __len__(self) -> int:
        """
        Return the number of unique field names.

        Returns
        -------
        int
            Count of distinct keys, not total item count.
        """
        return len({k for k, _ in self._items})

    def __repr__(self) -> str:
        """
        Return the canonical string representation.

        Returns
        -------
        str
        """
        return f"FormData({self._items!r})"

    # ---- Resource management ----

    def close(self) -> None:
        """
        Close all uploaded file handles to release resources.

        Returns
        -------
        None
        """
        for _, v in self._items:
            if not isinstance(v, str) and hasattr(v, "close"):
                v.close()

    def __enter__(self) -> Self:
        """
        Enter the context manager and return this instance.

        Returns
        -------
        Self
            The ``FormData`` instance itself.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit the context manager and close all uploaded file handles.

        Parameters
        ----------
        exc_type : type[BaseException] | None
            Exception class if one was raised, otherwise ``None``.
        exc_val : BaseException | None
            Exception instance if one was raised, otherwise ``None``.
        exc_tb : TracebackType | None
            Traceback if an exception was raised, otherwise ``None``.

        Returns
        -------
        None
        """
        self.close()
