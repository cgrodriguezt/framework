from orionis.database import Migration
from orionis.database.schema import Column, Comment
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
        await Schema.create("sessions",
            Column.string("id", 255).primary().comment("Session ID"),
            Column.text("payload").comment("Session Payload"),
            Column.bigInteger("expires_at").comment("Expiration"),
            Comment("Table to store session records."),
        )

    async def down(self) -> None:
        """
        Drop the ``sessions`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("sessions")
