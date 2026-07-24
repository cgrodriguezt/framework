from orionis.container.contracts.facade import IFacade
from orionis.database.contracts.manager import IConnectionManager

class DB(IConnectionManager, IFacade):
    ...
