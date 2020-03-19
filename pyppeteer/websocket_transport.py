import asyncio
from typing import Iterable, Union, AsyncIterable, Callable, Any, Optional

from websockets import connect, WebSocketClientProtocol, Data


class WebsocketTransport:
    def __init__(self, ws: WebSocketClientProtocol):
        self.onmessage: Optional[Callable[[str], Any]] = None
        self.onclose: Optional[Callable[[], Any]] = None
        self.ws = ws

    @classmethod
    async def create(cls, uri: str, loop: asyncio.AbstractEventLoop = None) -> 'WebsocketTransport':
        return cls(
            await connect(
                uri=uri,
                # chrome doesn't respond to pings
                # waiting on websockets to release new version where ping_interval is typed correctly
                ping_interval=None,  # type: ignore
                max_size=256 * 1024 * 1024,  # 256Mb
                loop=loop,
                close_timeout=5,
                # todo check if speed is affected
                # note: seems to work w/ compression
                compression=None,
            )
        )

    async def send(self, message: Union[Data, Iterable[Data], AsyncIterable[Data]]) -> None:
        await self.ws.send(message)

    async def close(self, code: int = 1000, reason: str = '') -> None:
        await self.ws.close(code=code, reason=reason)
        if self.onclose:
            await self.onclose()

    async def recv(self) -> Data:
        data = await self.ws.recv()
        if self.onmessage and data:
            await self.onmessage(data)
        return data
