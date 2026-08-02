from typing import TYPE_CHECKING
from orionis.database.schema.blueprint import Blueprint

if TYPE_CHECKING:
    from types import TracebackType
    from orionis.database.schema.definitions import SchemaDefinition
    from orionis.database.schema.schema import Schema

class TableCreation:
    """Awaitable and async context manager returned by ``Schema.create``.

    - ``await schema.create(name, *definitions)`` awaits this object
      directly, creating the table from the definitions given up front.
    - ``async with schema.create(name) as table:`` enters this object,
      yielding a :class:`~orionis.database.schema.blueprint.Blueprint`
      so columns can be declared inside the block; the table is created
      on exit, unless the block raised an exception.
    """

    __slots__ = ("__blueprint", "__definitions", "__name", "__schema")

    def __init__(
        self,
        schema: "Schema",
        name: str,
        definitions: tuple["SchemaDefinition", ...],
    ) -> None:
        """Store the pending table creation request.

        Parameters
        ----------
        schema : Schema
            The schema instance that will perform the creation.
        name : str
            The name of the table to create.
        definitions : tuple
            Schema definitions supplied to ``Schema.create``, if any.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__schema = schema
        self.__name = name
        self.__definitions = definitions
        self.__blueprint: Blueprint | None = None

    def __await__(self):
        """Create the table from the definitions given to ``create``.

        Returns
        -------
        Generator
            Iterator driving the underlying table creation coroutine.
        """
        return self.__schema._createTable(  # noqa: SLF001
            self.__name,
            self.__definitions,
        ).__await__()

    async def __aenter__(self) -> Blueprint:
        """Start a fluent, per-table column declaration block.

        Returns
        -------
        Blueprint
            Collector used to declare columns via method calls.
        """
        self.__blueprint = Blueprint()
        return self.__blueprint

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: "TracebackType | None",
    ) -> bool:
        """Create the table with the collected columns, unless it raised.

        Parameters
        ----------
        exc_type : type[BaseException] or None
            The exception type raised inside the block, if any.
        exc : BaseException or None
            The exception instance raised inside the block, if any.
        traceback : TracebackType or None
            The traceback for the raised exception, if any.

        Returns
        -------
        bool
            ``False`` to always propagate exceptions raised in the block.
        """
        if exc_type is None and self.__blueprint is not None:
            combined = (*self.__definitions, *self.__blueprint.columns())
            await self.__schema._createTable(self.__name, combined)  # noqa: SLF001
        return False
