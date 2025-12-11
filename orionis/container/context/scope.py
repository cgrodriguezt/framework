from __future__ import annotations
import contextvars

class ScopedContext:


    _active_scope = contextvars.ContextVar(
        "x-orionis-container-context-scope",
        default=None,
    )

    @classmethod
    def getCurrentScope(cls) -> object:
        """
        Retrieve the currently active scope for the current context.

        Returns
        -------
        object or None
            The currently active scope object, or None if no scope is set.
        """
        return cls._active_scope.get()

    @classmethod
    def setCurrentScope(cls, scope: object) -> None:
        """
        Set the active scope for the current context.

        Parameters
        ----------
        scope : object
            The scope object to be set as the active scope for the current context.
        """
        cls._active_scope.set(scope)

    @classmethod
    def clear(cls) -> None:
        """
        Clear the active scope for the current context.

        Resets the active scope to None.
        """
        cls._active_scope.set(None)
