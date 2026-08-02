from orionis.database import Migration
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
        async with Schema.create("permissions") as table:
            table.id().comment("Permission ID")
            table.string("name", 255).comment("Permission Name")
            table.string("guard_name", 255).comment("Guard Name")
            table.dateTime("created_at").nullable().comment("Created At")
            table.dateTime("updated_at").nullable().comment("Updated At")
            table.unique("name", "guard_name")
            table.comment("Table to store permissions.")

    async def down(self) -> None:
        """
        Drop the ``permissions`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("permissions")
