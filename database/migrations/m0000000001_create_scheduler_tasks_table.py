from orionis.database import Migration
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
        async with Schema.create("scheduler_tasks") as table:
            table.unicode("id", 191).primary().comment("Job ID")
            table.float("next_run_time").nullable().index().comment("Next Run Time")
            table.largeBinary("job_state").comment("Job State")

            table.comment("Table to store scheduled jobs (tasks).")

    async def down(self) -> None:
        """
        Drop the ``scheduler_tasks`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("scheduler_tasks")
