from orionis.services.environment.enums.cast_type import EnvCastType

class SerializerValue:

    def __init__(self, value):
        pass

    def to(self, type_hint: str | EnvCastType = None):
        pass

    def get(self):
        pass


class SerializerFrom:

    def __init__(self, key: str):
        pass

    def get(self):
        pass