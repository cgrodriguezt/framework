from orionis.orm import Boolean, Integer, Model, String, Timestamp

class User(Model):

    # Attribute type casting applied when reading/hydrating model values.
    casts: dict[str, str] = {
        "active": "bool",
        "email_verified_at": "datetime",
    }

    # Attributes excluded from the serialized output (toDict()/JSON).
    hidden: list[str] = ["password", "remember_token"]

    # Attributes allowed for mass assignment.
    fillable: list[str] = ["name", "email", "password"]

    # Table columns definition.
    id = Integer().primary().autoIncrement()
    name = String()
    email = String(150).unique().index()
    email_verified_at = Timestamp().nullable()
    password = String()
    remember_token = String(100).nullable()
    active = Boolean().default(True)
    created_at = Timestamp().nullable()
    updated_at = Timestamp().nullable()
