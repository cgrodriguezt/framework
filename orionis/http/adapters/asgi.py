import asyncio
from typing import Callable, Awaitable
from orionis.http.response import Response

class ASGIResponseAdapter:
    """
    Adapt Orionis Response objects to ASGI protocol messages.

    Attributes
    ----------
    RESPONSE_START : str
        ASGI message type for starting HTTP response.
    RESPONSE_BODY : str
        ASGI message type for sending HTTP response body.
    DISCONNECT : str
        ASGI message type for client disconnect.
    """

    RESPONSE_START = "http.response.start"
    RESPONSE_BODY = "http.response.body"
    DISCONNECT = "http.disconnect"

    async def send(
        self,
        response: Response,
        scope: dict,
        receive: Callable[..., Awaitable[dict]],
        send: Callable[..., Awaitable[None]],
    ) -> None:
        """
        Send an Orionis Response as ASGI messages.

        Parameters
        ----------
        response : Response
            The Orionis Response object to send.
        scope : dict
            The ASGI connection scope.
        receive : Callable[..., Awaitable[dict]]
            Awaitable callable to receive ASGI messages.
        send : Callable[..., Awaitable[None]]
            Awaitable callable to send ASGI messages.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set the Server header to identify the server software.
        response.setHeader("server", "Orionis ASGI")

        status: int = response.status_code
        headers: list = response.getRawHeaders()
        is_head: bool = scope["method"] == "HEAD"

        # Send the initial response start message
        await send({
            "type": self.RESPONSE_START,
            "status": status,
            "headers": headers,
        })

        # Handle streaming responses, including file responses
        if response.hasStream():
            if is_head:
                await self._sendFinal(send)
                await response.runBackground()
                return

            disconnect_task = asyncio.create_task(
                self._listenDisconnect(receive)
            )

            try:
                async for chunk in response.getStream():
                    if disconnect_task.done():
                        break
                    await send({
                        "type": self.RESPONSE_BODY,
                        "body": chunk,
                        "more_body": True,
                    })
            finally:
                disconnect_task.cancel()

            await self._sendFinal(send)
            await response.runBackground()
            return

        # Handle regular (non-streaming) response bodies
        body: bytes = response.getBody() or b""
        if is_head:
            body = b""

        await send({
            "type": self.RESPONSE_BODY,
            "body": body,
            "more_body": False,
        })

        await response.runBackground()

    async def _sendFinal(
        self,
        send: Callable[..., Awaitable[None]],
    ) -> None:
        """
        Send the final empty ASGI response body message.

        Parameters
        ----------
        send : Callable[..., Awaitable[None]]
            Awaitable callable to send ASGI messages.

        Returns
        -------
        None
            This method does not return a value.
        """
        await send({
            "type": self.RESPONSE_BODY,
            "body": b"",
            "more_body": False,
        })

    async def _listenDisconnect(
        self,
        receive: Callable[..., Awaitable[dict]],
    ) -> None:
        """
        Listen for ASGI disconnect messages.

        Parameters
        ----------
        receive : Callable[..., Awaitable[dict]]
            Awaitable callable to receive ASGI messages.

        Returns
        -------
        None
            This method does not return a value.
        """
        while True:
            message: dict = await receive()
            if message["type"] == self.DISCONNECT:
                return