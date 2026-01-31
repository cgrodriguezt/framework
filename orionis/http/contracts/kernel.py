from __future__ import annotations
from abc import ABC, abstractmethod
from orionis.container.context import scope

class IKernelHTTP(ABC):

    @abstractmethod
    async def handleRSGI(
        self,
        scope: scope,
        protocol: object,
    ) -> object:
        """
        Handle an RSGI HTTP request and print request details.

        Parameters
        ----------
        scope : Scope
            The RSGI scope object containing request information.
        protocol : object
            The protocol instance for the RSGI server.

        Returns
        -------
        object
            The result of the RSGI gateway handling the request.
        """

    @abstractmethod
    async def handleASGI(
        self,
        scope: object,
        receive: object,
        send: object,
    ) -> object:
        """
        Handle an ASGI HTTP request and print request details.

        Parameters
        ----------
        scope : object
            The ASGI scope dictionary containing request information.
        receive : object
            The receive callable for the ASGI server.
        send : object
            The send callable for the ASGI server.

        Returns
        -------
        object
            The result of the ASGI gateway handling the request.
        """
