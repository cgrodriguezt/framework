from __future__ import annotations
from abc import ABC, abstractmethod

class IWelcomeService(ABC):

    @abstractmethod
    async def greetUser(self, name: str = "Guest") -> str:
        """
        Output a personalized greeting message to the user.

        Constructs a greeting message with the provided name and displays
        it to the console with a character-by-character animation effect.

        Parameters
        ----------
        name : str, optional
            The user's name for personalization. Defaults to "Guest".

        Returns
        -------
        str
            The complete greeting message.
        """
