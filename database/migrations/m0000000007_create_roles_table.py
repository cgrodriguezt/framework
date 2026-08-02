from orionis.database import Migration
from orionis.support.facades import Schema

class CreateRolesTable(Migration):

    async def up(self) -> None:
        """
        Create the ``roles`` table used to store role names.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        async with Schema.create("roles") as table:
            table.id().comment("Role ID")
            table.string("name", 255).comment("Role Name")
            table.string("guard_name", 255).comment("Guard Name")
            table.dateTime("created_at").nullable().comment("Created At")
            table.dateTime("updated_at").nullable().comment("Updated At")
            table.unique("name", "guard_name")
            table.comment("Table to store roles.")

    async def down(self) -> None:
        """
        Drop the ``roles`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("roles")
