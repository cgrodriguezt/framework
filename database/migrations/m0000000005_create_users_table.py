from orionis.database import Migration
from orionis.database.schema import Column, Comment
from orionis.support.facades import Schema

class CreateUsersTable(Migration):

    async def up(self) -> None:
        """
        Create the ``users`` table used to store application users.

        Returns
        -------
        None
            The table is created as a side effect.
        """
        await Schema.create("users",
            Column.id().comment("User ID"),
            Column.string("name", 255).comment("Full Name"),
            Column.string("email", 255).unique().comment("Email Address"),
            Column.dateTime("email_verified_at").nullable().comment("Email Verification Timestamp"),
            Column.string("password", 255).comment("Hashed Password"),
            Column.string("remember_token", 100).nullable().comment("Remember Me Token"),
            Column.dateTime("created_at").nullable().comment("Created At"),
            Column.dateTime("updated_at").nullable().comment("Updated At"),
            Comment("Table to store application users."),
        )

    async def down(self) -> None:
        """
        Drop the ``users`` table, reverting the ``up`` migration.

        Returns
        -------
        None
            The table is dropped as a side effect.
        """
        await Schema.drop("users")
