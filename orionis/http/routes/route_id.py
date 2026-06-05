import itertools
import os
import time

# avoids time.__dict__ lookup each call
_time_ns = time.time_ns

# C-level counter; faster than cls._counter += 1
_next_id = itertools.count(1).__next__

# pre-converted; f-string skips int→str
_pid = str(os.getpid())

class RouteID:
    """Generate unique route identifiers."""
    __slots__ = ()

    @staticmethod
    def next(method: str, path: str) -> str:
        """Generate a unique route identifier.

        Parameters
        ----------
        method : str
            HTTP method (e.g., GET, POST, PUT, DELETE).
        path : str
            Route path.

        Returns
        -------
        str
            Unique route identifier combining method, path, timestamp,
            and counter.
        """
        return f"{method}:{path}:{_pid}:{_time_ns()}:{_next_id()}"
