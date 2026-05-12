import time
import os

class RouteID:
    """Generate unique route identifiers."""

    _counter = 0

    @classmethod
    def next(cls, method: str, path: str) -> str:
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
        cls._counter += 1
        return f"{method}:{path}:{os.getpid()}:{time.time_ns()}:{cls._counter}"
