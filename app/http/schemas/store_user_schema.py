from orionis.schemas.metadata import Message
from orionis.schemas.constraints import MinLength
from orionis.schemas.schema import Schema
from orionis.schemas.field import Field

class AddressSchema(Schema):
    street: Field[
        str,
        Message("La calle debe tener al menos 10 caracteres."),
        MinLength(10, message="La calle debe tener al menos 10 caracteres."),
    ]
    city: Field[
        str,
        Message("La ciudad debe tener al menos 2 caracteres."),
        MinLength(2, message="La ciudad debe tener al menos 2 caracteres."),
    ]
    state: Field[
        str,
        Message("El estado debe tener 2 caracteres."),
        MinLength(2, message="El estado debe tener 2 caracteres."),
    ]
    zip_code: Field[
        str,
        Message("El código postal debe tener 5 caracteres."),
        MinLength(5, message="El código postal debe tener 5 caracteres."),
    ]

class StoreUserSchema(Schema):
    name: Field[
        str,
        Message("El nombre debe tener al menos 8 caracteres."),
        MinLength(8, message="El nombre debe tener al menos 8 caracteres."),
    ]
    groups: Field[
        list[str],
        Message("El usuario debe pertenecer a al menos un grupo."),
        MinLength(1, message="El usuario debe pertenecer a al menos un grupo."),
    ]
    email: Field[
        str,
        Message("El correo electrónico debe ser válido."),
    ]
    address: AddressSchema
