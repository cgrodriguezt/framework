from __future__ import annotations
from abc import ABC, abstractmethod

class IFileBasedCache(ABC):

    @abstractmethod
    def get(
        self,
    ) -> dict | None:
        """
        Retrieve cached data if the cache is valid.

        Returns
        -------
        dict | None
            Cached data if valid and up-to-date, None if cache is invalid,
            missing, or outdated.
        """

    @abstractmethod
    def save(
        self,
        data: dict,
    ) -> tuple[int, str]:
        """
        Save the provided data to disk atomically.

        Parameters
        ----------
        data : dict
            Data to be cached.

        Returns
        -------
        tuple[int, str]
            Tuple containing the cache version and the sources hash.

        Raises
        ------
        TypeError
            If the provided data is not a dictionary.
        """

    @abstractmethod
    def clear(
        self,
    ) -> bool:
        """
        Remove the cache file from disk.

        Returns
        -------
        bool
            True if the cache file was successfully removed, False if it did
            not exist.
        """
