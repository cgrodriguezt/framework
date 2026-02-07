from typing import Any
from orionis.console.contracts.command import ICommand
from orionis.console.contracts.reactor import IReactor

class Reactor(IReactor):

    @classmethod
    async def init(cls) -> None:
        ...

    @classmethod
    def command(cls, signature: str, handler: list[type[Any], str | None]) -> ICommand:
        ...

    @classmethod
    def call(cls, signature: str, args: list[str] | None = None) -> int:
        ...
