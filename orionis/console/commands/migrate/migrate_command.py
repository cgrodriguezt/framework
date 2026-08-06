from typing import ClassVar
from orionis.console.args.argument import Argument
from orionis.console.base.command import BaseCommand
from orionis.console.output.executor import Executor
from orionis.database.migrations.migrator import Migrator

class MigrateCommand(BaseCommand):

    # ruff: noqa: TC001

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = True

    # Command signature and description
    signature: str = "migrate"

    # Command description
    description: str = "Runs all pending database migrations."

    # No CLI arguments are required to run pending migrations
    arguments: ClassVar[list[Argument]] = []

    async def handle(self, migrator: Migrator) -> None:
        """
        Apply every migration that has not been run yet.

        Parameters
        ----------
        migrator : Migrator
            Service that discovers and applies pending migrations.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.newLine()

        # One RUNNING/DONE (or FAIL) line per table, Laravel-style, instead
        # of a summary printed after every migration has already finished.
        executor = Executor()
        applied = await migrator.migrate(
            on_start=executor.running,
            on_success=lambda name, elapsed: executor.done(name, f"{elapsed:.2f}s"),
            on_error=lambda name, elapsed: executor.fail(name, f"{elapsed:.2f}s"),
        )

        if not applied:
            self.info("Nothing to migrate. Database is already up to date.")
            self.newLine()
