from dataclasses import dataclass, field
from typing import List, Optional
from orionis.foundation.config.cors.entities.cors import Cors

@dataclass
class BootstrapCors(Cors):

    # -------------------------------------------------------------------------
    # allow_origins : List[str]
    #     - List of allowed origins. Use ["*"] to allow all origins.
    #     - Defaults to ["*"] if not specified.
    # -------------------------------------------------------------------------
    allow_origins: List[str] = field(
        default_factory = lambda: ["*"]
    )

    # -------------------------------------------------------------------------
    # allow_origin_regex : Optional[str]
    #     - Regular expression to match allowed origins.
    #     - Defaults to None if not specified.
    # -------------------------------------------------------------------------
    allow_origin_regex: Optional[str] = None

    # -------------------------------------------------------------------------
    # allow_methods : List[str]
    #     - List of allowed HTTP methods. Use ["*"] to allow all methods.
    #     - Defaults to ["*"] if not specified.
    # -------------------------------------------------------------------------
    allow_methods: List[str] =  field(
        default_factory = lambda: ["*"]
    )

    # -------------------------------------------------------------------------
    # allow_headers : List[str]
    #     - List of allowed HTTP headers. Use ["*"] to allow all headers.
    #     - Defaults to ["*"] if not specified.
    # -------------------------------------------------------------------------
    allow_headers: List[str] =  field(
        default_factory = lambda: ["*"]
    )

    # -------------------------------------------------------------------------
    # expose_headers : List[str]
    #     - List of headers exposed to the browser.
    #     - Defaults to an empty list if not specified.
    # -------------------------------------------------------------------------
    expose_headers: List[str] =  field(
        default_factory = lambda: []
    )

    # -------------------------------------------------------------------------
    # allow_credentials : bool
    #     - Whether to allow credentials (cookies, authorization headers, etc.).
    #     - Defaults to False if not specified.
    # -------------------------------------------------------------------------
    allow_credentials: bool = False

    # -------------------------------------------------------------------------
    # max_age : Optional[int]
    #     - Maximum time (in seconds) for preflight request caching.
    #     - Defaults to 600 seconds if not specified.
    # -------------------------------------------------------------------------
    max_age: Optional[int] = 600