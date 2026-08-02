from orionis.database import Migration
from orionis.database.schema import Column, Comment, Index, PrimaryKey
from orionis.support.facades import Schema

class CreateModelHasRolesTable(Migration):

    async def up(self) -> None:
        """Create the ``model_has_roles`` table.

        Relates roles to any model through a polymorphic (morph) relation.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        await Schema.create("model_has_roles",
            Column.bigInteger("role_id").foreign("roles.id").comment("Role ID"),
            Column.string("model_type", 255).comment("Model Class Name"),
            Column.bigInteger("model_id").comment("Model ID"),
            PrimaryKey("role_id", "model_id", "model_type"),
            Index("model_id", "model_type"),
            Comment("Table to relate roles with any model (morph)."),
        )

    async def down(self) -> None:
        """
        Drop the ``model_has_roles`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("model_has_roles")
