from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType
    from orionis.http.payload.uploaded_file import UploadedFile

class IFormData(ABC):
    """
    Define the contract for parsed multipart form data.

    Implementations hold ordered ``(name, value)`` pairs from a multipart
    body, support multiple values under the same field name (e.g. multi-select
    or repeated ``<input>`` elements with the same ``name`` attribute), and
    release open file handles via the context-manager protocol.
    """

    @property
    @abstractmethod
    def fields(self) -> dict[str, list[str]]:
        """
        Return all text field values grouped by name.

        Returns
        -------
        dict[str, list[str]]
            Mapping of field names to all their string values in insertion order.
        """

    @property
    @abstractmethod
    def files(self) -> dict[str, list[UploadedFile]]:
        """
        Return all uploaded file values grouped by name.

        Returns
        -------
        dict[str, list[UploadedFile]]
            Mapping of field names to all their ``UploadedFile`` instances
            in insertion order.
        """

    @property
    @abstractmethod
    def allItems(self) -> list[tuple[str, str | UploadedFile]]:
        """
        Return all ``(name, value)`` pairs in insertion order without copying.

        Exposes the internal list directly — callers must not mutate it.

        Returns
        -------
        list[tuple[str, str | UploadedFile]]
            The underlying item sequence.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def multiItems(self) -> list[tuple[str, str | UploadedFile]]:
        """
        Return all ``(name, value)`` pairs in insertion order.

        Returns
        -------
        list[tuple[str, str | UploadedFile]]
            A copy of the underlying item sequence.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Close all uploaded file handles to release resources.

        Returns
        -------
        None
        """

    @abstractmethod
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

    @abstractmethod
    def __contains__(self, key: object) -> bool:
        """
        Return ``True`` if at least one item with *key* exists.

        Parameters
        ----------
        key : object
            Field name to check.

        Returns
        -------
        bool
        """

    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        """
        Iterate over unique field names in first-seen insertion order.

        Returns
        -------
        Iterator[str]
            Each unique field name exactly once.
        """

    @abstractmethod
    def __len__(self) -> int:
        """
        Return the number of unique field names.

        Returns
        -------
        int
            Count of distinct keys, not total item count.
        """

    @abstractmethod
    def __repr__(self) -> str:
        """
        Return the canonical string representation.

        Returns
        -------
        str
        """

    @abstractmethod
    def __enter__(self) -> Self:
        """
        Enter the context manager and return this instance.

        Returns
        -------
        Self
            The ``FormData`` instance itself.
        """

    @abstractmethod
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
