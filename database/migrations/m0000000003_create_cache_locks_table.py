from orionis.database import Migration
from orionis.database.schema import Column, Comment
from orionis.support.facades import Schema

class CreateCacheLocksTable(Migration):

    async def up(self) -> None:
        """
        Create the ``cache_locks`` table used to store atomic cache locks.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        await Schema.create("cache_locks",
            Column.string("cache_key", 255).primary().comment("Lock Key"),
            Column.string("owner", 255).nullable().comment("Lock Owner"),
            Column.bigInteger("expiration").nullable().comment("Expiration"),
            Comment("Table to store atomic cache locks."),
        )

    async def down(self) -> None:
        """
        Drop the ``cache_locks`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("cache_locks")
