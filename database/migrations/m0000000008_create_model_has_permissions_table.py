from orionis.database import Migration
from orionis.database.schema import Column, Comment, Index, PrimaryKey
from orionis.support.facades import Schema

class CreateModelHasPermissionsTable(Migration):

    async def up(self) -> None:
        """Create the ``model_has_permissions`` table.

        Relates permissions to any model through a polymorphic (morph)
        relation.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        await Schema.create("model_has_permissions",
            Column.bigInteger("permission_id").foreign("permissions.id").comment("Permission ID"),
            Column.string("model_type", 255).comment("Model Class Name"),
            Column.bigInteger("model_id").comment("Model ID"),
            PrimaryKey("permission_id", "model_id", "model_type"),
            Index("model_id", "model_type"),
            Comment("Table to relate permissions with any model (morph)."),
        )

    async def down(self) -> None:
        """Drop the ``model_has_permissions`` table.

        Reverts the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("model_has_permissions")
