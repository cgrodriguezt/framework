from abc import ABC, abstractmethod

class IKernelHTTP(ABC):
    """
    Interface for implementing the HTTP kernel.

    The HTTP kernel is responsible for handling incoming HTTP requests,
    as well as WebSocket requests. It also determines whether to start
    an ASGI or RSGI server and manages the pipelines and middlewares
    required to process HTTP requests.

    Methods
    -------
    handle(*args)
        Handles incoming requests for ASGI or RSGI servers.

    Returns
    -------
    None
        This method does not return any value.
    """

    @abstractmethod
    async def handle(self, *args) -> None:
        """
        Handles incoming requests for ASGI or RSGI servers.

        The *args parameter is used to accommodate the different signatures
        required by ASGI and RSGI server handlers. For example, ASGI uses
        (async def app(scope, receive, send):) while RSGI uses
        (async def app(scope, proto):).

        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        NotImplementedError
            If the method is not overridden by a subclass.
        """
        # This method must be implemented by subclasses.
        raise NotImplementedError("This method should be overridden by subclasses.")
