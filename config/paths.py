from dataclasses import dataclass, field
from pathlib import Path
from orionis.foundation.config.roots.paths import Paths

@dataclass(frozen=True, kw_only=True)
class BootstrapPaths(Paths):
    pass