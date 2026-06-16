from orionis.foundation.contracts.application import IApplication

class Storage:

    def __init__(
        self,
        app: IApplication,
    ) -> None:
        self._app = app
        self._filesystem_config = self._app.config("filesystems")
        print(self._filesystem_config)

    def put(
        self,
        nombre,
        contenido,
    ) -> None:
        print(f"Guardando archivo {nombre} con contenido: {contenido}")
