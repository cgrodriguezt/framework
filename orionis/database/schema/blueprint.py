from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.database.schema.column import Column

if TYPE_CHECKING:
    from collections.abc import Callable
    from orionis.orm.schema.column import ColumnDefinition

class Blueprint:
    """Fluent collector of column definitions for a single table.

    Instances are yielded by ``Schema.create(name)`` when used as an
    async context manager (``async with schema.create(name) as table:``),
    allowing columns to be declared one call at a time instead of passing
    every definition up front.
    """

    __slots__ = ("__columns", "__factory_cache")

    def __init__(self) -> None:
        """Initialize the blueprint with no columns declared yet.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__columns: list[ColumnDefinition] = []
        self.__factory_cache: dict[str, Callable[..., ColumnDefinition]] = {}

    def __getattr__(self, name: str) -> Callable[..., ColumnDefinition]:
        """Proxy a column-factory call to :class:`Column`, recording it.

        This is what powers calls such as ``table.string("username")`` or
        ``table.boolean("is_admin")``: any factory exposed by
        :class:`Column` becomes available on the blueprint, and the
        resulting column is appended to this table automatically.

        Parameters
        ----------
        name : str
            Name of the ``Column`` factory method being invoked.

        Returns
        -------
        Callable[..., ColumnDefinition]
            Wrapper that builds the column and appends it to this table.

        Raises
        ------
        AttributeError
            If ``name`` does not match a known ``Column`` factory method.
        """
        # Reuse a previously resolved factory for this column-type name.
        cached = self.__factory_cache.get(name)
        if cached is not None:
            return cached

        factory = getattr(Column, name, None)
        if factory is None or not callable(factory):
            error_msg = f"'{type(self).__name__}' object has no attribute {name!r}."
            raise AttributeError(error_msg)

        def _build(*args: object, **kwargs: object) -> ColumnDefinition:
            """Build the column via ``Column`` and register it on the table."""
            column = factory(*args, **kwargs)
            self.__columns.append(column)
            return column

        self.__factory_cache[name] = _build
        return _build

    def timestamps(self, *, timezone: bool = False) -> None:
        """Add nullable ``created_at`` and ``updated_at`` columns.

        Parameters
        ----------
        timezone : bool, optional
            Whether the timestamp columns should be timezone-aware.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.dateTime("created_at", timezone=timezone).nullable()
        self.dateTime("updated_at", timezone=timezone).nullable()

    def columns(self) -> tuple[ColumnDefinition, ...]:
        """Return the columns declared so far, in declaration order.

        Returns
        -------
        tuple of ColumnDefinition
            Snapshot of every column recorded on this blueprint.
        """
        return tuple(self.__columns)
