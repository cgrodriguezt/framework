from orionis.schemas.constraints import MinLength, StrongPassword
from orionis.schemas.fields import Field
from orionis.schemas.metadata import Message
from orionis.schemas.schema import Schema
from app.http.schemas.constraints.zipcode import ZipCode

class AddressSchema(Schema):
    street: Field[
        str,
        Message("`street` must be a string."),
        MinLength(10, message="Street must be at least 10 characters long."),
    ]
    city: Field[
        str,
        Message("City must be a string."),
        MinLength(2, message="City must be at least 2 characters long."),
    ]
    state: Field[
        str,
        Message("State must be a string."),
        MinLength(2, message="State must be at least 2 characters long."),
    ]
    zip_code: Field[
        str,
        Message("ZIP code must be a string."),
        ZipCode(
            message="ZIP code must be exactly 5 digits and between 00501 and 99950.",
        ),
    ]

class StoreUserSchema(Schema):
    name: Field[
        str,
        Message("Name must be a string."),
        MinLength(8, message="Name must be at least 8 characters long."),
    ]
    groups: Field[
        list[str],
        Message("The user must belong to at least one group."),
        MinLength(1, message="The user must belong to at least one group."),
    ]
    email: Field[
        str,
        Message("Email must be a string."),
    ]
    password: Field[
        str,
        Message("Password must be a string."),
        StrongPassword(message="Min 8 chars with uppercase, lowercase, and a digit."),
    ]
    address: AddressSchema
