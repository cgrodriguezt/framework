from orionis.foundation.config.http.entitites.security import HTTPSecurity
from granian.rsgi import Scope

from orionis.http.adapters.transport import RSGITransportAdapter, TransportAdapter
from orionis.http.response import Response

class ProxiesMiddleware:
    """
    """

    def __init__(
        self,
        config: dict,
    ) -> None:
        self.__config = HTTPSecurity(**config)
        self.__validate_headers = self.__config.validate_headers
        self.__max_header_size = self.__config.max_header_size
        self.__block_multiple_host_headers = self.__config.block_multiple_host_headers

        if isinstance(self.__config.allowed_hosts, list):
            self.__allowed_hosts = set(self.__config.allowed_hosts)
        elif self.__config.allowed_hosts == '*':
            self.__allowed_hosts = None
        else:
            raise ValueError("Invalid value for allowed_hosts. Must be a list or '*'")

    def handleRSGI(self, scope: Scope) -> Scope | Response:

        # Si no se deben validar los headers, retornar el scope sin modificar
        if not  self.__validate_headers:
            return scope

        # Crear un adapter de transporte para acceder a los headers de la request de forma más cómoda.
        adapter: TransportAdapter = RSGITransportAdapter(scope)

        # Bloquear múltiples headers Host si la configuración lo indica,
        # para evitar ataques de HTTP Host header injection.
        if self.__block_multiple_host_headers and len(adapter.getAllHeaders("host")) > 1:
            return self.__response(
                400,
                "Bad Request: Multiple Host headers are not allowed.",
                json_response=adapter.wantsJson(),
            )



    def __response(self, status_code: int, message: str, *, json_response:bool =False) -> Response:
        return Response(
            status_code=status_code,
            content=message,
            headers={"Content-Type": "text/plain"},
        )