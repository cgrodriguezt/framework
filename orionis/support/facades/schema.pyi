from orionis.database.contracts.schema import ISchema
from orionis.database.schema.comment import Comment
from orionis.database.schema.foreign import ForeignKey
from orionis.database.schema.index import Index
from orionis.database.schema.primary import PrimaryKey
from orionis.database.schema.table_creation import TableCreation
from orionis.database.schema.unique import Unique
from orionis.orm.schema.column import ColumnDefinition

class Schema(ISchema):
    """Stub matching the class-level calling convention of the facade.

    ``ISchema`` declares instance methods, but the real facade is always
    called directly on the class (``Schema.create(...)``, never on an
    instance), so each method is redeclared here as a ``staticmethod``
    without ``self`` for accurate static typing.
    """

    @staticmethod
    def connection(name: str | None = None) -> type[Schema]: ...
    @staticmethod
    def create(
        name: str,
        *definitions: (
            ColumnDefinition
            | Comment
            | ForeignKey
            | Index
            | PrimaryKey
            | Unique
        ),
    ) -> TableCreation: ...
    @staticmethod
    async def drop(name: str) -> bool: ...
