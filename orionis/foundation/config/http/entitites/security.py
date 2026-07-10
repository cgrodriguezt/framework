from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class HTTPSecurity(BaseEntity):

    allowed_hosts: list[str] | Literal["*"] = field(
        default="*",
        metadata={
            "description": (
                "List of allowed host names or '*' to allow all hosts. "
                "Entries may use a leading wildcard to match subdomains "
                "(e.g. '*.example.com')."
            ),
        },
    )

    def __post_init__(self) -> None:
        """Validate security-related fields.

        Raises
        ------
        TypeError
            If any field has an unexpected type.

        Returns
        -------
        None
        """
        super().__post_init__()
        self.__validateAllowedHosts()

    def __validateAllowedHosts(self) -> None:
        """Validate the ``allowed_hosts`` field.

        Raises
        ------
        TypeError
            If the value is not a list of strings or the literal '*'.

        Returns
        -------
        None
        """
        if self.allowed_hosts == "*":
            return

        if not isinstance(self.allowed_hosts, list):
            error_msg = (
                "Invalid type for 'allowed_hosts': expected a list of strings or '*'."
            )
            raise TypeError(error_msg)

        if not all(
            isinstance(h, str)
            for h in self.allowed_hosts
        ):
            error_msg = (
                "Invalid type for 'allowed_hosts': all items must be strings."
            )
            raise TypeError(error_msg)
