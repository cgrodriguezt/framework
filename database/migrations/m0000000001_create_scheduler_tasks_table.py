from orionis.database import Migration
from orionis.database.schema import Column, Comment
from orionis.support.facades import Schema

class CreateSchedulerTasksTable(Migration):

    async def up(self) -> None:
        """
        Create the ``scheduler_tasks`` table used to persist scheduled jobs.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        await Schema.create("scheduler_tasks",
            Column.unicode("id", 191).primary().comment("Job ID"),
            Column.float("next_run_time").nullable().index().comment("Next Run Time"),
            Column.largeBinary("job_state").comment("Job State"),
            Comment("Table to store scheduled jobs (APScheduler)."),
        )

    async def down(self) -> None:
        """
        Drop the ``scheduler_tasks`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("scheduler_tasks")
