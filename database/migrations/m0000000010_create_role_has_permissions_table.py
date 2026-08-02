from orionis.database import Migration
from orionis.database.schema import Column, Comment, PrimaryKey
from orionis.support.facades import Schema

class CreateRoleHasPermissionsTable(Migration):

    async def up(self) -> None:
        """Create the ``role_has_permissions`` table.

        Relates roles with permissions.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        await Schema.create("role_has_permissions",
            Column.bigInteger("permission_id").foreign("permissions.id").comment("Permission ID"),
            Column.bigInteger("role_id").foreign("roles.id").comment("Role ID"),
            PrimaryKey("permission_id", "role_id"),
            Comment("Table to relate roles with permissions."),
        )

    async def down(self) -> None:
        """Drop the ``role_has_permissions`` table.

        Reverts the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("role_has_permissions")
