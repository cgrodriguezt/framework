from abc import ABC, abstractmethod
from orionis.session.session import Session

class SessionDriver(ABC):

    @abstractmethod
    async def load(
        self,
        session_id: str | None,
        lifetime: int,
    ) -> Session:
        """
        Load an existing session or create a new one.
        """

    @abstractmethod
    async def save(
        self,
        session: Session,
    ) -> None:
        """
        Persist the session.
        """

    @abstractmethod
    async def destroy(
        self,
        session_id: str,
    ) -> None:
        """
        Remove a session permanently.
        """

    async def gc(self) -> None:
        """
        Perform garbage collection.
        """