import asyncio

class BaseFakeClass:
    pass

class FakeClass(BaseFakeClass):
    """
    FakeClass is a test double for inspection and reflection scenarios.
    Attributes:
        class_attr (str): A class-level attribute with a default value "class_value".
    Instance Attributes:
        public_attr (int): A public instance attribute initialized to 42.
        _protected_attr (str): A protected instance attribute initialized to "protected".
        __private_attr (str): A private instance attribute initialized to "private".
        dynamic_attr: An instance attribute initialized to None.
        __dd__ (str): A dunder-named attribute initialized to "dunder_value".
    Methods:
        instanceMethod(x: int, y: int) -> int:
            Adds two numbers and returns the result.
        computed_property -> str:
            A computed property that returns a string based on public_attr.
        classMethod() -> str:
            Class method returning a string representation of the class attribute.
        _classMethodProte() -> str:
            Protected class method returning a string representation of the class attribute.
        __classMethodPP() -> str:
            Private class method returning a string representation of the class attribute.
        staticMethod(text: str) -> str:
            Static method that returns the uppercase version of the input text.
        __staticMethodPP(text: str) -> str:
            Private static method that returns the uppercase version of the input text.
        staticAsyncMethod(text: str) -> Awaitable[str]:
            Asynchronous static method that returns the uppercase version of the input text after a delay.
        __privateMethod() -> str:
            Private instance method returning a string indicating it is private.
        _protectedMethod() -> str:
            Protected instance method returning a string indicating it is protected.
        asyncMethod() -> Awaitable[str]:
            Asynchronous instance method returning a string indicating it is async.
        __str__() -> Awaitable[str]:
            Asynchronous string representation of the instance.
    """

    class_attr: str = "class_value"

    def __init__(self) -> None:
        self.public_attr = 42
        self._protected_attr = "protected"
        self.__private_attr = "private"
        self.dynamic_attr = None
        self.__dd__ = "dunder_value"

    def instanceMethod(self, x: int, y: int) -> int:
        """Adds two numbers."""
        return x + y

    @property
    def computed_property(self) -> str:
        """A computed property."""
        return f"public"

    @property
    def _computed_property_protected(self) -> str:
        """A computed property."""
        return f"protected"

    @property
    def __computed_property_private(self) -> str:
        """A computed property."""
        return f"private"

    @classmethod
    def classMethod(cls) -> str:
        """A class method."""
        return f"Class attr: {cls.class_attr}"

    @classmethod
    async def classMethodAsync(cls) -> str:
        """A class method."""
        return f"Class attr: {cls.class_attr}"

    @classmethod
    def _classMethodProte(cls) -> str:
        """A class method."""
        return f"Class attr: {cls.class_attr}"

    @classmethod
    async def _classMethodProteAsync(cls) -> str:
        """A class method."""
        return f"Class attr: {cls.class_attr}"

    @classmethod
    def __classMethodPP(cls) -> str:
        """A class method."""
        return f"Class attr: {cls.class_attr}"

    @classmethod
    async def __classMethodPPAsync(cls) -> str:
        """A class method."""
        return f"Class attr: {cls.class_attr}"

    @staticmethod
    def staticMethod(text: str) -> str:
        """A static method."""
        return text.upper()

    @staticmethod
    def __staticMethodSYNC(text: str) -> str:
        """A static method. Ejemplo de método privado."""
        return text.upper()

    @staticmethod
    async def staticAsyncMethod(text: str) -> str:
        """An asynchronous static method."""
        await asyncio.sleep(0.1)
        return text.upper()

    @staticmethod
    def _staticMethodPro(text: str) -> str:
        """A static method."""
        return text.upper()

    @staticmethod
    async def _staticMethodProAsync(text: str) -> str:
        """A static method."""
        return text.upper()

    @staticmethod
    async def __staticMethodPrivateAsync(text: str) -> str:
        """A static method."""
        return text.upper()

    def __privateMethod(self) -> str:
        """A 'private' method."""
        return "This is private"

    def _protectedMethod(self) -> str:
        """A 'protected' method."""
        return "This is protected"

    async def asyncMethod(self) -> str:
        """An async method."""
        return "This is async"

    async def __str__(self):
        return super().__str__()