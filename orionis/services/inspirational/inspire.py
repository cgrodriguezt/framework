from __future__ import annotations
from orionis.services.inspirational.contracts.inspire import IInspire
from orionis.services.inspirational.quotes import INSPIRATIONAL_QUOTES
import secrets

class Inspire(IInspire):

    def __init__(self, quotes: list[dict] | None = None) -> None:
        """
        Initialize the Inspire service with a list of inspirational quotes.

        Parameters
        ----------
        quotes : list[dict] | None, optional
            List of dictionaries, each containing 'quote' (str) and 'author' (str).
            If None or empty, defaults to INSPIRATIONAL_QUOTES.

        Returns
        -------
        None
            This method initializes the internal state of the Inspire service.

        Raises
        ------
        ValueError
            If any item is not a dict, or missing 'quote'/'author' keys.
        """
        # Use default quotes if none provided or list is empty
        if quotes is None or not quotes:
            self.__quotes = INSPIRATIONAL_QUOTES
        else:
            # Validate each quote dictionary
            for row in quotes:
                if not isinstance(row, dict):
                    error_msg = (
                        "Quotes must be provided as a list of dictionaries."
                    )
                    raise TypeError(error_msg)
                if "quote" not in row or "author" not in row:
                    error_msg = (
                        "Each quote dictionary must contain 'quote' and 'author' keys."
                    )
                    raise ValueError(error_msg)
            self.__quotes = quotes

    def random(self) -> dict:
        """
        Return a random inspirational quote from the available list.

        Select a random quote from the internal list of inspirational quotes.
        If the list is empty, return a fallback quote to ensure a valid response.

        Returns
        -------
        dict
            Dictionary with 'quote' (str) and 'author' (str) keys. If no quotes
            are available, returns a fallback quote.
        """
        # Get the number of available quotes
        count: int = len(self.__quotes)

        # Return fallback if no quotes are available
        if count == 0:
            return self.__fallback()

        # Select a random quote index using a cryptographically secure generator
        num_random: int = secrets.randbelow(count)

        # Return the selected quote or fallback if None
        return self.__quotes[num_random] or self.__fallback()

    def __fallback(self) -> dict:
        """
        Provide a default inspirational quote if none are available.

        Returns
        -------
        dict
            Dictionary with 'quote' (str) and 'author' (str) keys representing
            the fallback inspirational quote and its author.
        """
        # Return a hardcoded fallback quote and author
        return {
            "quote": (
                "Greatness is not measured by what you build, "
                "but by what you inspire others to create."
            ),
            "author": "Raul M. Uñate",
        }
