from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class HTTPSecurity(BaseEntity):
    """Configure HTTP security header validation."""

    # ----------------------------------------------------------
    # Security Headers (Request Validation)
    # ----------------------------------------------------------

    validate_headers: bool = field(
        default=True,
        metadata={
            "description": (
                "Whether to validate incoming HTTP headers for security (CRLF "
                "injection prevention, header duplication checks)."
            ),
        },
    )

    max_header_size: int = field(
        default=8192,
        metadata={
            "description": (
                "Maximum allowed size for individual HTTP headers in bytes. Default is "
                "8192 bytes (8 KB). Applies to each header field separately, not total "
                "size."
            ),
        },
    )

    block_multiple_host_headers: bool = field(
        default=True,
        metadata={
            "description": (
                "Whether to block requests with multiple Host headers, which can "
                "pose a security risk."
            ),
        },
    )

    # ----------------------------------------------------------
    # Host Validation
    # ----------------------------------------------------------

    allowed_hosts: list[str] | Literal["*"] = field(
        default="*",
        metadata={
            "description": (
                "List of allowed host names or '*' to allow all hosts."
            ),
        },
    )

    def __post_init__(self) -> None:
        """Validate security-related fields.

        Raises
        ------
        TypeError
            If any field has an unexpected type.
        ValueError
            If ``max_header_size`` is not positive.

        Returns
        -------
        None
        """
        super().__post_init__()
        self.__validateSecurityHeaders()
        self.__validateAllowedHosts()

    def __validateSecurityHeaders(self) -> None:
        """Validate security-header fields.

        Check ``validate_headers``, ``max_header_size``,
        and ``block_multiple_host_headers``.

        Raises
        ------
        TypeError
            If any field has an unexpected type.
        ValueError
            If ``max_header_size`` is not positive.

        Returns
        -------
        None
        """
        if not isinstance(self.validate_headers, bool):
            error_msg = (
                "Invalid type for 'validate_headers': expected a boolean."
            )
            raise TypeError(error_msg)

        if (
            not isinstance(self.max_header_size, int)
            or isinstance(self.max_header_size, bool)
        ):
            error_msg = (
                "Invalid type for 'max_header_size': expected an integer."
            )
            raise TypeError(error_msg)

        if self.max_header_size <= 0:
            error_msg = (
                "Invalid value for 'max_header_size': must be a positive integer."
            )
            raise ValueError(error_msg)

        if not isinstance(
            self.block_multiple_host_headers, bool,
        ):
            error_msg = (
                "Invalid type for 'block_multiple_host_headers': expected a boolean."
            )
            raise TypeError(error_msg)

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
                "Invalid type for 'allowed_hosts':  all items must be strings."
            )
            raise TypeError(error_msg)
