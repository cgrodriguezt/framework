from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
from orionis.services.environment.env import Env
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class HTTPRequest(BaseEntity):
    """Configure HTTP request body and method handling."""

    # ----------------------------------------------------------
    # Content-Type Precheck
    # ----------------------------------------------------------

    allowed_content_types: list[str] | Literal["*"] = field(
        default="*",
        metadata={
            "description": (
                "List of allowed Content-Type headers or '*' to allow all."
            ),
        },
    )

    # ----------------------------------------------------------
    # Request Size Guard
    # ----------------------------------------------------------

    max_content_length: int | None = field(
        default_factory=lambda: int(
            Env.get(
                "MAX_CONTENT_LENGTH", 10 * 1024 * 1024,
            ),
        ),
        metadata={
            "description": (
                "Maximum allowed request body size in bytes. Defaults to 10 MB."
            ),
        },
    )

    # ----------------------------------------------------------
    # Method Override
    # ----------------------------------------------------------

    enable_method_override: bool = field(
        default_factory=lambda: Env.get(
            "METHOD_OVERRIDE", True,
        ),
        metadata={
            "description": (
                "Enable or disable HTTP method override support."
            ),
        },
    )

    method_override_header: str = field(
        default="x-http-method-override",
        metadata={
            "description": (
                "Header name used for HTTP method override."
            ),
        },
    )

    def __post_init__(self) -> None:
        """Validate request-handling fields.

        Raises
        ------
        TypeError
            If any field has an unexpected type.
        ValueError
            If any field is outside its allowed domain.

        Returns
        -------
        None
        """
        super().__post_init__()
        self.__validateContentTypes()
        self.__validateRequestSize()
        self.__validateMethodOverride()

    def __validateContentTypes(self) -> None:
        """Validate the ``allowed_content_types`` field.

        Accept a list of strings or the literal ``"*"``.

        Raises
        ------
        TypeError
            If the value is neither a string list
            nor ``"*"``.

        Returns
        -------
        None
        """
        if not (
            isinstance(self.allowed_content_types, list)
            or self.allowed_content_types == "*"
        ):
            error_msg = (
                "Invalid type for 'allowed_content_types': "
                "expected a list of strings or '*'."
            )
            raise TypeError(error_msg)

        if isinstance(
            self.allowed_content_types, list,
        ) and not all(
            isinstance(ct, str)
            for ct in self.allowed_content_types
        ):
            error_msg = (
                "Invalid type for 'allowed_content_types': all items must be strings."
            )
            raise TypeError(error_msg)

    def __validateRequestSize(self) -> None:
        """Validate the ``max_content_length`` field.

        Accept a positive integer or ``None``.

        Raises
        ------
        TypeError
            If the value is not an integer or ``None``.
        ValueError
            If the integer is not positive.

        Returns
        -------
        None
        """
        if self.max_content_length is not None and (
            not isinstance(self.max_content_length, int)
            or isinstance(self.max_content_length, bool)
        ):
            error_msg = (
                "Invalid type for 'max_content_length': expected an integer or None."
            )
            raise TypeError(error_msg)

        if (
            self.max_content_length is not None
            and self.max_content_length <= 0
        ):
            error_msg = (
                "Invalid value for 'max_content_length': must be a positive integer."
            )
            raise ValueError(error_msg)

    def __validateMethodOverride(self) -> None:
        """Validate method-override fields.

        Check ``enable_method_override`` and
        ``method_override_header``.

        Raises
        ------
        TypeError
            If any field has an unexpected type.

        Returns
        -------
        None
        """
        if not isinstance(self.enable_method_override, bool):
            error_msg = (
                "Invalid type for 'enable_method_override': expected a boolean."
            )
            raise TypeError(error_msg)

        if not isinstance(self.method_override_header, str):
            error_msg = (
                "Invalid type for 'method_override_header': expected a string."
            )
            raise TypeError(error_msg)
