from app.contracts.welcome_service import IWelcomeService
from orionis.container.contracts import IFacade

class Welcome(IWelcomeService, IFacade):
    ...
