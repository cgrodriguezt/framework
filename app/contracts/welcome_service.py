from __future__ import annotations
from abc import ABC, abstractmethod

class IWelcomeService(ABC):

    @abstractmethod
    async def greetUser(self) -> str:
        """
        Output a personalized greeting message for the user.

        Retrieves the 'name' argument from the CLI request. If not provided,
        defaults to 'Guest'. Outputs the greeting using the console interface
        and returns the greeting message.

        Parameters
        ----------
        self : WelcomeService
            Instance of WelcomeService.

        Returns
        -------
        str
            Greeting message addressed to the user.
        """
