# ruff: noqa: N815 (camelCase attributes are an Orionis convention)
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class InsertResult:
    """
    Outcome of an INSERT statement executed through a connection.

    Attributes
    ----------
    lastInsertId : Any
        Primary key generated for the inserted row, or ``None`` when the
        driver cannot report it (for example on multi-row inserts).
    rowCount : int
        Number of rows affected by the statement.
    """

    lastInsertId: Any  # NOSONAR
    rowCount: int  # NOSONAR
