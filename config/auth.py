from __future__ import annotations
from dataclasses import dataclass
from orionis.foundation.config.auth.entities.auth import Auth

@dataclass(frozen=True, kw_only=True)
class BootstrapAppAuth(Auth):
    pass
