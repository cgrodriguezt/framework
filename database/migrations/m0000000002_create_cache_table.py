from orionis.database import Migration
from orionis.database.schema import Column, Comment
from orionis.support.facades import Schema

class CreateCacheTable(Migration):

    async def up(self) -> None:
        """
        Create the ``cache`` table used to store cache entries.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        await Schema.create("cache",
            Column.string("cache_key", 255).primary().comment("Cache Key"),
            Column.text("cache_value").nullable().comment("Cache Value"),
            Column.bigInteger("expiration").nullable().comment("Expiration"),
            Comment("Table to store cache entries."),
        )

    async def down(self) -> None:
        """
        Drop the ``cache`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("cache")
