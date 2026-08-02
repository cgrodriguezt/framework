from orionis.database import Migration
from orionis.database.schema import Column, Comment, Unique
from orionis.support.facades import Schema

class CreatePermissionsTable(Migration):

    async def up(self) -> None:
        """
        Create the ``permissions`` table used to store permission names.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        await Schema.create("permissions",
            Column.id().comment("Permission ID"),
            Column.string("name", 255).comment("Permission Name"),
            Column.string("guard_name", 255).comment("Guard Name"),
            Column.dateTime("created_at").nullable().comment("Created At"),
            Column.dateTime("updated_at").nullable().comment("Updated At"),
            Unique("name", "guard_name"),
            Comment("Table to store permissions."),
        )

    async def down(self) -> None:
        """
        Drop the ``permissions`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("permissions")
