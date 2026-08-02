from orionis.database import Migration
from orionis.support.facades import Schema

class CreateSessionsTable(Migration):

    async def up(self) -> None:
        """
        Create the ``sessions`` table used to store session records.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        async with Schema.create("sessions") as table:
            table.string("id", 255).primary().comment("Session ID")
            table.text("payload").comment("Session Payload")
            table.bigInteger("expires_at").comment("Expiration")
            table.comment("Table to store session records.")

    async def down(self) -> None:
        """
        Drop the ``sessions`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("sessions")
