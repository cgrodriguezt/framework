from orionis.orm import Model

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
