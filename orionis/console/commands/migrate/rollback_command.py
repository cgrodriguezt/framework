from typing import ClassVar
from orionis.console.args.argument import Argument
from orionis.console.base.command import BaseCommand
from orionis.console.output.executor import Executor
from orionis.database.migrations.migrator import Migrator

class MigrateRollbackCommand(BaseCommand):

    # ruff: noqa: TC001

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = True

    # Command signature and description
    signature: str = "migrate:rollback"

    # Command description
    description: str = "Reverts the last batch(es) of database migrations."

    # List of Argument instances defining command-line options and arguments
    arguments: ClassVar[list[Argument]] = [
        Argument(
            name_or_flags=["--step", "-s"],
            type_=int,
            required=False,
            help=(
                "Number of migration batches to roll back. Defaults to 1 "
                "(the most recent batch)."
            ),
            dest="step",
        ),
    ]

    async def handle(self, migrator: Migrator) -> None:
        """
        Revert the most recently applied migration batches.

        Parameters
        ----------
        migrator : Migrator
            Service that discovers and reverts applied migrations.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.newLine()

        # One RUNNING/DONE (or FAIL) line per table, Laravel-style, instead
        # of a summary printed after every migration has already reverted.
        executor = Executor()
        steps = self.getArgument("step") or 1
        reverted = await migrator.rollback(
            steps=int(steps),
            on_start=executor.running,
            on_success=lambda name, elapsed: executor.done(name, f"{elapsed:.2f}s"),
            on_error=lambda name, elapsed: executor.fail(name, f"{elapsed:.2f}s"),
        )

        if not reverted:
            self.info("Nothing to roll back.")
