from __future__ import annotations
from dataclasses import dataclass, field
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Cors(BaseEntity):
    """
    Represent a CORS configuration compatible with Starlette CORSMiddleware.

    Attributes
    ----------
    allow_origins : list[str]
        List of allowed origins. Use ["*"] to allow all origins.
    allow_origin_regex : str | None
        Regular expression to match allowed origins.
    allow_methods : list[str]
        List of allowed HTTP methods. Use ["*"] to allow all methods.
    allow_headers : list[str]
        List of allowed HTTP headers. Use ["*"] to allow all headers.
    expose_headers : list[str]
        List of headers exposed to the browser.
    allow_credentials : bool
        Whether to allow credentials (cookies, authorization headers, etc.).
    max_age : int | None
        Maximum time (in seconds) for the preflight request to be cached.
    """

    allow_origins: list[str] = field(
        default_factory=lambda: ["*"],
        metadata={
            "description": 'List of allowed origins. Use ["*"] to allow all origins.',
            "deafault": ["*"],
        },
    )

    allow_origin_regex: str | None = field(
        default=None,
        metadata={
            "description": "Regular expression pattern to match allowed origins.",
            "default": None,
        },
    )

    allow_methods: list[str] = field(
        default_factory=lambda: ["*"],
        metadata={
            "description": (
                'List of allowed HTTP methods. Use ["*"] to allow all methods.'
            ),
            "default": ["*"],
        },
    )

    allow_headers: list[str] = field(
        default_factory=lambda: ["*"],
        metadata={
            "description": (
                'List of allowed HTTP headers. Use ["*"] to allow all headers.'
            ),
            "default": ["*"],
        },
    )

    expose_headers: list[str] = field(
        default_factory=list,
        metadata={
            "description": "List of headers exposed to the browser.",
            "default": [],
        },
    )

    allow_credentials: bool = field(
        default=False,
        metadata={
            "description": (
                "Whether to allow credentials (cookies, authorization headers, etc.)."
            ),
            "default": False,
        },
    )

    max_age: int | None = field(
        default=600,
        metadata={
            "description": "Maximum time (in seconds) for preflight request caching.",
            "default": 600,
        },
    )

    def __validateAllowMethods(self) -> None:
        """
        Validate that all items in 'allow_methods' are valid HTTP methods or a wildcard.

        Checks that each entry in 'allow_methods' is a string and matches a valid HTTP
        method or is the wildcard '*'. Raises a TypeError or ValueError if invalid.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If any item in 'allow_methods' is not a string.
        ValueError
            If any item is not a valid HTTP method or the wildcard.
        """
        # Define the set of allowed HTTP methods
        allowed_http_methods = {"GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"}

        # Validate each method in allow_methods unless wildcard is used
        if self.allow_methods != ["*"]:
            for method in self.allow_methods:
                if not isinstance(method, str):
                    error_msg = (
                        f"Invalid type in 'allow_methods': {method!r} is not a string."
                    )
                    raise TypeError(error_msg)
                if method.upper() not in allowed_http_methods:
                    error_msg = (
                        f"Invalid HTTP method in 'allow_methods': {method!r}. "
                        f"Allowed methods are {sorted(allowed_http_methods)}."
                    )
                    raise ValueError(error_msg)

    def __post_init__(self) -> None:
        """
        Validate CORS configuration attributes after initialization.

        Ensure the types and values of the CORS configuration attributes conform to
        expected types and constraints. Raises a TypeError if any attribute is invalid.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        TypeError
            If any attribute does not match the expected type.
        ValueError
            If any attribute contains an invalid value.
        """
        # Call the superclass's __post_init__ method
        super().__post_init__()

        # Validate `allow_origins` attribute
        if not isinstance(self.allow_origins, list):
            error_msg = (
                "Invalid type for 'allow_origins': expected a list of strings."
            )
            raise TypeError(error_msg)

        # Validate `allow_origin_regex` attribute
        if self.allow_origin_regex is not None and not isinstance(
            self.allow_origin_regex, str,
        ):
            error_msg = (
                "Invalid type for 'allow_origin_regex': expected a string or None."
            )
            raise TypeError(error_msg)

        # Validate `allow_methods` attribute
        if not isinstance(self.allow_methods, list):
            error_msg = (
                "Invalid type for 'allow_methods': expected a list of strings."
            )
            raise TypeError(error_msg)

        # Validate the contents of `allow_methods`
        self.__validateAllowMethods()

        # Validate `allow_headers` attribute
        if not isinstance(self.allow_headers, list):
            error_msg = (
                "Invalid type for 'allow_headers': expected a list of strings."
            )
            raise TypeError(error_msg)

        # Validate `expose_headers` attribute
        if not isinstance(self.expose_headers, list):
            error_msg = (
                "Invalid type for 'expose_headers': expected a list of strings."
            )
            raise TypeError(error_msg)

        # Validate `allow_credentials` attribute
        if not isinstance(self.allow_credentials, bool):
            error_msg = (
                "Invalid type for 'allow_credentials': expected a boolean."
            )
            raise TypeError(error_msg)

        # Validate `max_age` attribute
        if self.max_age is not None and not isinstance(self.max_age, int):
            error_msg = (
                "Invalid type for 'max_age': expected an integer or None."
            )
            raise TypeError(error_msg)
