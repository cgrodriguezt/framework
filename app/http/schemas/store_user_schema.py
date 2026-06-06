from orionis.schemas.schema import Schema

class AddressSchema(Schema):
    street: str
    city: str
    state: str
    zip_code: str

class StoreUserSchema(Schema):
    name: str
    groups: set[str] | None = None
    email: str | None = None
    address: AddressSchema | None = None
