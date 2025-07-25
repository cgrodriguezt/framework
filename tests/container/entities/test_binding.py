from orionis.container.entities.binding import Binding
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions.type import OrionisContainerTypeError
from orionis.test.cases.asynchronous import AsyncTestCase

class TestBinding(AsyncTestCase):

    async def testBindingInitialization(self):
        """
        Test that a Binding can be initialized with default values.

        Raises
        ------
        AssertionError
            If the Binding initialization fails or default values are incorrect.
        """
        binding: Binding = Binding()
        self.assertIsNone(binding.contract)
        self.assertIsNone(binding.concrete)
        self.assertIsNone(binding.instance)
        self.assertIsNone(binding.function)
        self.assertEqual(binding.lifetime, Lifetime.TRANSIENT)
        self.assertFalse(binding.enforce_decoupling)
        self.assertIsNone(binding.alias)

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

        self.assertIs(binding.contract, TestContract)
        self.assertIs(binding.concrete, TestConcrete)
        self.assertIs(binding.instance, instance)
        self.assertIs(binding.function, factory_func)
        self.assertEqual(binding.lifetime, Lifetime.SINGLETON)
        self.assertTrue(binding.enforce_decoupling)
        self.assertEqual(binding.alias, "test_binding")

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

        self.assertIsInstance(result, dict)
        self.assertIs(result["contract"], TestContract)
        self.assertIs(result["concrete"], TestConcrete)
        self.assertIsNone(result["instance"])
        self.assertIsNone(result["function"])
        self.assertEqual(result["lifetime"], Lifetime.SINGLETON)
        self.assertTrue(result["enforce_decoupling"])
        self.assertEqual(result["alias"], "test_binding")

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

        self.assertIsInstance(fields_info, list)
        self.assertEqual(len(fields_info), 7)

        field_names = [field["name"] for field in fields_info]
        expected_names = ["contract", "concrete", "instance", "function","lifetime", "enforce_decoupling", "alias"]
        self.assertTrue(all(name in field_names for name in expected_names))

        # Test specific field information
        lifetime_field = next(field for field in fields_info if field["name"] == "lifetime")
        self.assertEqual(lifetime_field["default"], Lifetime.TRANSIENT.value)
        self.assertIn("description", lifetime_field["metadata"])