from orionis.container.contracts.facade import IFacade
from orionis.database.contracts.manager import IConnectionManager
from orionis.orm.query.raw_builder import RawQueryBuilder

class DB(IConnectionManager, IFacade):
    @classmethod
    def table(
        cls,
        name: str,
        *,
        alias: str | None = None,
        connection: str | None = None,
    ) -> RawQueryBuilder: ...

