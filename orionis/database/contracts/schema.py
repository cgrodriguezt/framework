from __future__ import annotations
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from orionis.database.schema.comment import Comment
    from orionis.database.schema.foreign import ForeignKey
    from orionis.database.schema.index import Index
    from orionis.database.schema.primary import PrimaryKey
    from orionis.database.schema.unique import Unique
    from orionis.orm.schema.column import ColumnDefinition

class ISchema(ABC):

    @abstractmethod
    def connection(self, name: str | None = None) -> Self:
        """Set the connection name for schema operations.

        Parameters
        ----------
        name : str | None, optional
            The connection name to use, by default None.

        Returns
        -------
        Self
            The current Schema instance for method chaining.

        Raises
        ------
        ValueError
            If connection name has already been defined.
        """
        ...

    @abstractmethod
    async def create(
        self,
        name: str,
        *definitions: type[
            ColumnDefinition
            | Comment
            | ForeignKey
            | Index
            | PrimaryKey
            | Unique
        ],
    ) -> bool:
        """Create a new table with the given definitions.

        Parameters
        ----------
        name : str
            The name of the table to create. If the table belongs to a
            non-default schema, use the ``schema.table`` format.
        *definitions : type[ColumnDefinition] | type[Comment] | ...
            Variable length argument list of schema definitions
            (columns, constraints, indexes, etc.).

        Returns
        -------
        bool
            ``True`` when the table is created without errors.
        """
        ...

    @abstractmethod
    async def drop(self, name: str) -> bool:
        """Drop an existing table.

        Parameters
        ----------
        name : str
            The name of the table to drop. If the table belongs to a
            non-default schema, use the ``schema.table`` format.

        Returns
        -------
        bool
            ``True`` when the table is dropped without errors.
        """
        ...
