from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

class IMigrator(ABC):
    """
    Contract for the database migration runner.

    Implementations discover migration files under the application's
    ``database/migrations`` directory, track which ones have already been
    applied, and apply or revert them in chronological order.
    """

    __slots__ = ()

    @abstractmethod
    async def migrate(
        self,
        *,
        on_start: Callable[[str], None] | None = None,
        on_success: Callable[[str, float], None] | None = None,
        on_error: Callable[[str, float], None] | None = None,
    ) -> list[str]:
        """
        Apply every migration that has not been run yet.

        Parameters
        ----------
        on_start : callable, optional
            Invoked with the migration name right before it runs.
        on_success : callable, optional
            Invoked with the migration name and elapsed seconds after it
            applies successfully.
        on_error : callable, optional
            Invoked with the migration name and elapsed seconds when its
            ``up`` method raises, right before the exception propagates.

        Returns
        -------
        list of str
            Names of the migrations applied, in the order they ran. Empty
            when there is nothing pending.

        Raises
        ------
        Exception
            Any exception raised by a migration's ``up`` method aborts
            the run and propagates to the caller.
        """
        ...

    @abstractmethod
    async def rollback(
        self,
        steps: int = 1,
        *,
        on_start: Callable[[str], None] | None = None,
        on_success: Callable[[str, float], None] | None = None,
        on_error: Callable[[str, float], None] | None = None,
    ) -> list[str]:
        """
        Revert the most recently applied migration batches.

        Parameters
        ----------
        steps : int, optional
            Number of batches to roll back, starting from the most
            recent one. Defaults to ``1``.
        on_start : callable, optional
            Invoked with the migration name right before it is reverted.
        on_success : callable, optional
            Invoked with the migration name and elapsed seconds after it
            reverts successfully.
        on_error : callable, optional
            Invoked with the migration name and elapsed seconds when its
            ``down`` method raises, right before the exception propagates.

        Returns
        -------
        list of str
            Names of the migrations reverted, in the order they were
            rolled back. Empty when there is nothing to revert.

        Raises
        ------
        ValueError
            If ``steps`` is not a positive integer.
        MigrationNotFoundException
            If a recorded migration has no matching migration file.
        Exception
            Any exception raised by a migration's ``down`` method aborts
            the rollback and propagates to the caller.
        """
        ...
