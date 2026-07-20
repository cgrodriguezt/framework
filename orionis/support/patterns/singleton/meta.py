from __future__ import annotations
import threading
import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar
    T = TypeVar("T")

# Sentinel object: distinguishes "not yet created" from any valid instance value,
# including None. Module-level allocation ensures a single identity comparison
# instead of a dict __contains__ call in the hot path.
_MISSING: object = object()

# Per-class synchronous locks: keyed by class object, populated in __init__.
# Isolating locks per class eliminates false contention between unrelated singletons
# that would otherwise share a single metaclass-level Lock.
# Storing here (not as cls._lock) avoids the naming collision that forced DotEnv
# to use the slower threading.RLock for reentrant acquisition.
_sync_locks: dict[type, threading.Lock] = {}

# Meta-lock used exclusively to safely initialise per-class async locks on first
# async call. It is never held while the singleton constructor runs.
_meta_lock: threading.Lock = threading.Lock()

# Per-class asynchronous locks: lazily populated on first __acall__ invocation.
# Lazy initialisation avoids creating asyncio.Lock objects for every singleton
# class, most of which will never be used from an async context.
_async_locks: dict[type, asyncio.Lock] = {}


class Singleton(type):
    """
    Enforce the singleton pattern for classes using this metaclass.

    Ensures that only one instance of a class is created, providing
    both thread-safe synchronous and async-safe asynchronous access.

    Performance design
    ------------------
    * Per-class sync locks (``_sync_locks``) eliminate cross-singleton
      contention that a single shared Lock would cause.
    * The singleton instance is stored directly on the class object as
      ``_singleton_instance``.  The hot path after first creation reduces
      to one attribute lookup plus an ``is not`` identity check — the
      cheapest possible guard in CPython.
    * Async locks (``_async_locks``) are initialised lazily to avoid
      allocating ``asyncio.Lock`` objects for classes that are never
      awaited.
    """

    def __init__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
    ) -> None:
        super().__init__(name, bases, namespace)

        # Initialise per-class singleton state at class-creation time so that
        # __call__ never needs a defensive check or lazy-init branch.
        # type.__setattr__ is used explicitly to bypass any __setattr__ override
        # that a subclass of Singleton might introduce.
        type.__setattr__(cls, "_singleton_instance", _MISSING)

        # One Lock per class: contention between distinct singletons is impossible.
        _sync_locks[cls] = threading.Lock()

    def __call__(
        cls,
        *args: object,
        **kwargs: object,
    ) -> object:
        """
        Create or retrieve the singleton instance in a thread-safe manner.

        Hot path (instance already exists)
        -----------------------------------
        Single ``type.__getattribute__`` call + ``is not`` identity check.
        No dict subscript, no MRO traversal beyond the class's own ``__dict__``.

        Cold path (first call)
        ----------------------
        Per-class lock acquisition followed by a double-checked read to handle
        races between threads that concurrently passed the first guard.

        Parameters
        ----------
        *args : object
            Positional arguments forwarded to the class constructor.
        **kwargs : object
            Keyword arguments forwarded to the class constructor.

        Returns
        -------
        object
            The singleton instance of the class.
        """
        # Hot path — O(1): one attribute read, one identity comparison.
        instance = cls._singleton_instance
        if instance is not _MISSING:
            return instance

        # Cold path — first call or concurrent race to create the instance.
        with _sync_locks[cls]:
            # Re-read after acquiring the lock (double-checked locking).
            # Local variable avoids a second attribute traversal.
            instance = cls._singleton_instance
            if instance is _MISSING:
                instance = super().__call__(*args, **kwargs)
                type.__setattr__(cls, "_singleton_instance", instance)

        return instance

    async def __acall__(
        cls,
        *args: object,
        **kwargs: object,
    ) -> object:
        """
        Retrieve or create the singleton instance asynchronously.

        The async lock for each class is created lazily on the first invocation
        to avoid allocating ``asyncio.Lock`` objects for singletons that are
        never used from an async context.

        Invoke explicitly as ``await MyClass.__acall__()``.

        Parameters
        ----------
        *args : object
            Positional arguments forwarded to the class constructor.
        **kwargs : object
            Keyword arguments forwarded to the class constructor.

        Returns
        -------
        object
            The singleton instance of the class.
        """
        # Hot path — same O(1) guard as the sync path.
        instance = cls._singleton_instance
        if instance is not _MISSING:
            return instance

        # Lazily initialise the per-class async lock using EAFP (faster than
        # an explicit `in` check when the lock already exists).
        try:
            async_lock = _async_locks[cls]
        except KeyError:
            with _meta_lock:
                if cls not in _async_locks:
                    _async_locks[cls] = asyncio.Lock()
                async_lock = _async_locks[cls]

        async with async_lock:
            instance = cls._singleton_instance
            if instance is _MISSING:
                instance = super().__call__(*args, **kwargs)
                type.__setattr__(cls, "_singleton_instance", instance)

        return instance
