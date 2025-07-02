from orionis.container.entities.binding import Binding
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions.type_error_exception import OrionisContainerTypeError
from orionis.test.cases.test_case import TestCase

class TestBinding(TestCase):
    """
    Test cases for the Binding class in orionis.container.entities.binding.

    Notes
    -----
    This test suite validates the initialization, validation, and utility methods
    of the Binding class, which is used to configure dependency injections.
    """

    async def testBindingInitialization(self):
        """
        Test that a Binding can be initialized with default values.

        Raises
        ------
        AssertionError
            If the Binding initialization fails or default values are incorrect.
        """
        binding: Binding = Binding()
        assert binding.contract is None
        assert binding.concrete is None
        assert binding.instance is None
        assert binding.function is None
        assert binding.lifetime == Lifetime.TRANSIENT
        assert binding.enforce_decoupling is False
        assert binding.alias is None

    async def testBindingCustomValues(self):
        """
        Test that a Binding can be initialized with custom values.

        Raises
        ------
        AssertionError
            If the Binding initialization fails or custom values are not set correctly.
        """
        class TestContract: pass
        class TestConcrete: pass

        instance = TestConcrete()
        factory_func = lambda: TestConcrete()

        binding = Binding(
            contract=TestContract,
            concrete=TestConcrete,
            instance=instance,
            function=factory_func,
            lifetime=Lifetime.SINGLETON,
            enforce_decoupling=True,
            alias="test_binding"
        )

        assert binding.contract is TestContract
        assert binding.concrete is TestConcrete
        assert binding.instance is instance
        assert binding.function is factory_func
        assert binding.lifetime == Lifetime.SINGLETON
        assert binding.enforce_decoupling is True
        assert binding.alias == "test_binding"

    async def testBindingPostInitValidation(self):
        """
        Test that __post_init__ validation works correctly.

        Raises
        ------
        AssertionError
            If validation errors are not raised appropriately.
        """
        # Test invalid lifetime
        with self.assertRaises(OrionisContainerTypeError):
            Binding(lifetime="not_a_lifetime")

        # Test invalid enforce_decoupling
        with self.assertRaises(OrionisContainerTypeError):
            Binding(enforce_decoupling="not_a_bool")

        # Test invalid alias
        with self.assertRaises(OrionisContainerTypeError):
            Binding(alias=123)

    async def testToDictMethod(self):
        """
        Test that toDict method returns a correct dictionary representation.

        Raises
        ------
        AssertionError
            If the dictionary representation is incorrect.
        """
        class TestContract: pass
        class TestConcrete: pass

        binding = Binding(
            contract=TestContract,
            concrete=TestConcrete,
            lifetime=Lifetime.SINGLETON,
            enforce_decoupling=True,
            alias="test_binding"
        )

        result = binding.toDict()

        assert isinstance(result, dict)
        assert result["contract"] == TestContract
        assert result["concrete"] == TestConcrete
        assert result["instance"] is None
        assert result["function"] is None
        assert result["lifetime"] == Lifetime.SINGLETON
        assert result["enforce_decoupling"] is True
        assert result["alias"] == "test_binding"

    async def testGetFieldsMethod(self):
        """
        Test that getFields method returns correct field information.

        Raises
        ------
        AssertionError
            If the field information is incorrect.
        """
        binding = Binding()
        fields_info = binding.getFields()

        assert isinstance(fields_info, list)
        assert len(fields_info) == 7  # Number of fields in the class

        field_names = [field["name"] for field in fields_info]
        expected_names = ["contract", "concrete", "instance", "function", 
                          "lifetime", "enforce_decoupling", "alias"]
        assert all(name in field_names for name in expected_names)

        # Test specific field information
        lifetime_field = next(field for field in fields_info if field["name"] == "lifetime")
        assert lifetime_field["type"] == "Lifetime"
        assert lifetime_field["default"] == Lifetime.TRANSIENT
        assert "description" in lifetime_field["metadata"]