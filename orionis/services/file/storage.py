from pathlib import Path
from orionis.foundation.contracts.application import IApplication

class Storage:

    def __init__(self, app:IApplication) -> None:
        self.__root = app.path('root')