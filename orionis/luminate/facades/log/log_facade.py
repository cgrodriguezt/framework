from orionis.luminate.contracts.facades.facade import Facade
from orionis.luminate.contracts.services.log.log_service import ILogguerService

class Log(Facade):
    _service = ILogguerService