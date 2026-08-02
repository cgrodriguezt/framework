from orionis.database import Migration
from orionis.database.schema import Column, Comment, Unique
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
        await Schema.create("roles",
            Column.id().comment("Role ID"),
            Column.string("name", 255).comment("Role Name"),
            Column.string("guard_name", 255).comment("Guard Name"),
            Column.dateTime("created_at").nullable().comment("Created At"),
            Column.dateTime("updated_at").nullable().comment("Updated At"),
            Unique("name", "guard_name"),
            Comment("Table to store roles."),
        )

    async def down(self) -> None:
        """
        Drop the ``roles`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("roles")
