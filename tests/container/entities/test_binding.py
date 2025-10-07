from orionis.container.entities.binding import Binding
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions import OrionisContainerTypeError
from orionis.test.cases.synchronous import SyncTestCase

class TestEntities(SyncTestCase):

    def testBindingInitialization(self):
        """
        Test initialization of a Binding object with default values.

        This test verifies that when a Binding instance is created without any arguments,
        all attributes are set to their expected default values.

        Parameters
        ----------
        self : TestBinding
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate behavior.

        Raises
        ------
        AssertionError
            If any of the default values are incorrect or the Binding initialization fails.
        """

        # Create a Binding instance with default parameters
        binding: Binding = Binding()

        # Assert that all attributes are set to their default values
        self.assertIsNone(binding.contract)                         # Default contract should be None
        self.assertIsNone(binding.concrete)                         # Default concrete should be None
        self.assertIsNone(binding.instance)                         # Default instance should be None
        self.assertIsNone(binding.function)                         # Default function should be None
        self.assertEqual(binding.lifetime, Lifetime.TRANSIENT)      # Default lifetime should be TRANSIENT
        self.assertFalse(binding.enforce_decoupling)                # Default enforce_decoupling should be False
        self.assertIsNone(binding.alias)                            # Default alias should be None

    def testBindingCustomValues(self):
        """
        Test initialization of a Binding object with custom values.

        This test verifies that when a Binding instance is created with explicit arguments,
        all attributes are set to the provided custom values, and the object reflects the intended configuration.

        Parameters
        ----------
        self : TestBinding
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate correct attribute assignment.

        Raises
        ------
        AssertionError
            If the Binding initialization fails or custom values are not set correctly.
        """

        # Define dummy contract and concrete classes for testing
        class TestContract:
            pass
        class TestConcrete:
            pass

        # Create an instance for the 'instance' attribute
        instance = TestConcrete()

        # Define a factory function for the 'function' attribute
        def factory_func():
            return TestConcrete()

        # Initialize Binding with custom values
        binding = Binding(
            contract=TestContract,
            concrete=TestConcrete,
            instance=instance,
            function=factory_func,
            lifetime=Lifetime.SINGLETON,
            enforce_decoupling=True,
            alias="test_binding"
        )

        # Assert that all attributes are set to the provided custom values
        self.assertIs(binding.contract, TestContract)
        self.assertIs(binding.concrete, TestConcrete)
        self.assertIs(binding.instance, instance)
        self.assertIs(binding.function, factory_func)
        self.assertEqual(binding.lifetime, Lifetime.SINGLETON)
        self.assertTrue(binding.enforce_decoupling)
        self.assertEqual(binding.alias, "test_binding")

    def testBindingPostInitValidation(self):
        """
        Validates that the `__post_init__` method of the `Binding` class raises appropriate
        exceptions when invalid types are provided for certain attributes.

        This test ensures that type validation is enforced for the `lifetime`, `enforce_decoupling`,
        and `alias` attributes during initialization. If an invalid type is passed, the
        `OrionisContainerTypeError` should be raised.

        Parameters
        ----------
        self : TestBinding
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate that
            exceptions are raised for invalid input types.

        Raises
        ------
        AssertionError
            If the expected `OrionisContainerTypeError` is not raised when invalid types
            are provided for the attributes.
        """

        # Attempt to initialize Binding with an invalid lifetime type (should raise exception)
        with self.assertRaises(OrionisContainerTypeError):
            Binding(lifetime="not_a_lifetime")

        # Attempt to initialize Binding with an invalid enforce_decoupling type (should raise exception)
        with self.assertRaises(OrionisContainerTypeError):
            Binding(enforce_decoupling="not_a_bool")

        # Attempt to initialize Binding with an invalid alias type (should raise exception)
        with self.assertRaises(OrionisContainerTypeError):
            Binding(alias=123)

    def testToDictMethod(self):
        """
        Tests the `toDict` method of the `Binding` class to ensure it returns a correct dictionary representation
        of the binding's attributes.

        This test verifies that the dictionary contains all expected keys and that their values match the attributes
        set during initialization. It also checks that the types and values are correctly preserved.

        Parameters
        ----------
        self : TestBinding
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate the correctness of the dictionary representation.

        Raises
        ------
        AssertionError
            If the dictionary representation is incorrect or any attribute does not match the expected value.
        """

        # Define dummy contract and concrete classes for testing
        class TestContract:
            pass
        class TestConcrete:
            pass

        # Create a Binding instance with custom values
        binding = Binding(
            contract=TestContract,
            concrete=TestConcrete,
            lifetime=Lifetime.SINGLETON,
            enforce_decoupling=True,
            alias="test_binding"
        )

        # Get the dictionary representation of the binding
        result = binding.toDict()

        # Assert that the result is a dictionary
        self.assertIsInstance(result, dict)

        # Assert that contract and concrete are correctly set
        self.assertIs(result["contract"], TestContract)
        self.assertIs(result["concrete"], TestConcrete)

        # Assert that instance and function are None by default
        self.assertIsNone(result["instance"])
        self.assertIsNone(result["function"])

        # Assert that lifetime, enforce_decoupling, and alias are correctly set
        self.assertEqual(result["lifetime"], Lifetime.SINGLETON)
        self.assertTrue(result["enforce_decoupling"])
        self.assertEqual(result["alias"], "test_binding")

    def testGetFieldsMethod(self):
        """
        Tests the `getFields` method of the `Binding` class to ensure it returns accurate field metadata.

        This test verifies that the returned list contains the expected number of fields, that all expected
        field names are present, and that specific field metadata (such as default values and descriptions)
        are correctly provided for the `lifetime` field.

        Parameters
        ----------
        self : TestBinding
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate the correctness of the
            field metadata returned by `getFields`.

        Raises
        ------
        AssertionError
            If the field information is incorrect, such as missing fields, incorrect defaults, or missing metadata.
        """

        # Create a Binding instance with default parameters
        binding = Binding()

        # Retrieve field metadata using getFields
        fields_info = binding.getFields()

        # Assert that the returned value is a list
        self.assertIsInstance(fields_info, list)

        # Assert that there are exactly 7 fields
        self.assertEqual(len(fields_info), 7)

        # Extract field names from the metadata
        field_names = [field["name"] for field in fields_info]
        expected_names = ["contract", "concrete", "instance", "function", "lifetime", "enforce_decoupling", "alias"]

        # Assert that all expected field names are present
        self.assertTrue(all(name in field_names for name in expected_names))

        # Find the metadata for the 'lifetime' field
        lifetime_field = next(field for field in fields_info if field["name"] == "lifetime")

        # Assert that the default value for 'lifetime' is correct
        self.assertEqual(lifetime_field["default"], Lifetime.TRANSIENT.value)

        # Assert that the 'lifetime' field contains a description in its metadata
        self.assertIn("description", lifetime_field["metadata"])

    def testBindingEqualityAndHash(self):
        """
        Tests the equality and hash behavior of `Binding` instances.

        This test verifies that two `Binding` objects with identical attribute values are considered equal
        and have the same hash value. It also checks that `Binding` objects with different attribute values
        are not equal and have different hash values.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate equality and hash behavior.

        Raises
        ------
        AssertionError
            If the equality or hash behavior does not match the expected outcome.
        """
        class Contract:
            pass

        class Concrete:
            pass

        # Create two bindings with identical values
        b1 = Binding(contract=Contract, concrete=Concrete, alias="a")
        b2 = Binding(contract=Contract, concrete=Concrete, alias="a")
        # Create a binding with a different alias
        b3 = Binding(contract=Contract, concrete=Concrete, alias="b")

        # Assert that b1 and b2 are equal and have the same hash
        self.assertEqual(b1, b2)
        self.assertEqual(hash(b1), hash(b2))
        # Assert that b1 and b3 are not equal and have different hashes
        self.assertNotEqual(b1, b3)
        self.assertNotEqual(hash(b1), hash(b3))

    def testBindingWithNoneValues(self):
        """
        Tests that `Binding` accepts `None` for contract, concrete, instance, function, and alias attributes.

        This test ensures that the `Binding` class can be initialized with `None` values for its optional attributes
        and that these attributes are correctly set to `None`.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate attribute values.

        Raises
        ------
        AssertionError
            If any attribute is not set to `None` as expected.
        """
        # Initialize Binding with None for all optional attributes
        binding = Binding(contract=None, concrete=None, instance=None, function=None, alias=None)
        self.assertIsNone(binding.contract)
        self.assertIsNone(binding.concrete)
        self.assertIsNone(binding.instance)
        self.assertIsNone(binding.function)
        self.assertIsNone(binding.alias)

    def testBindingFunctionCallable(self):
        """
        Tests that the `function` attribute can be set to a callable and is preserved.

        This test verifies that a callable assigned to the `function` attribute of a `Binding` instance
        is stored and can be invoked as expected.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate callable behavior.

        Raises
        ------
        AssertionError
            If the function attribute is not set or does not behave as expected.
        """
        # Define a dummy function
        def dummy_func(): return 42
        # Assign the function to the binding
        binding = Binding(function=dummy_func)
        self.assertIs(binding.function, dummy_func)
        # Assert that the function returns the expected value
        self.assertEqual(binding.function(), 42)

    def testBindingWithFalseyAlias(self):
        """
        Tests that the `alias` attribute can be set to an empty string and is validated as a string.

        This test ensures that an empty string is accepted as a valid value for the `alias` attribute.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate the alias value.

        Raises
        ------
        AssertionError
            If the alias is not set to an empty string as expected.
        """
        # Set alias to an empty string
        binding = Binding(alias="")
        self.assertEqual(binding.alias, "")

    def testBindingWithFalseyLifetime(self):
        """
        Tests that lifetime validation raises an error if a falsy but invalid value (such as None) is provided.

        This test ensures that the `Binding` class enforces type validation for the `lifetime` attribute
        and raises an exception when an invalid value is used.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate exception raising.

        Raises
        ------
        AssertionError
            If the expected exception is not raised for an invalid lifetime value.
        """
        # Attempt to initialize Binding with None as lifetime (should raise exception)
        with self.assertRaises(OrionisContainerTypeError):
            Binding(lifetime='singleton')  # Invalid string instead of Lifetime enum

    def testBindingWithFalseyEnforceDecoupling(self):
        """
        Tests that the `enforce_decoupling` attribute can be set to False and is validated as a boolean.

        This test verifies that setting `enforce_decoupling` to False is accepted and correctly stored.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate the attribute value.

        Raises
        ------
        AssertionError
            If the enforce_decoupling attribute is not set to False as expected.
        """
        # Set enforce_decoupling to False
        binding = Binding(enforce_decoupling=False)
        self.assertFalse(binding.enforce_decoupling)

    def testBindingWithNonCallableFunction(self):
        """
        Tests that the `function` attribute can be set to a non-callable value without raising an error at initialization.

        This test ensures that the `Binding` class does not enforce callability of the `function` attribute at initialization.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate attribute assignment.

        Raises
        ------
        AssertionError
            If the function attribute is not set to the non-callable value as expected.
        """
        # Assign a non-callable value to function
        binding = Binding(function=123)
        self.assertEqual(binding.function, 123)

    def testBindingToDictIncludesAllFields(self):
        """
        Tests that the `toDict` method returns all expected fields, even if their values are None.

        This test verifies that the dictionary representation of a `Binding` instance includes all
        defined fields, regardless of whether they are set to None.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate dictionary keys.

        Raises
        ------
        AssertionError
            If any expected field is missing from the dictionary.
        """
        # Create a binding with default values
        binding = Binding()
        d = binding.toDict()
        # List of expected keys in the dictionary
        expected_keys = ["contract", "concrete", "instance", "function", "lifetime", "enforce_decoupling", "alias"]
        # Assert all expected keys are present
        self.assertTrue(all(key in d for key in expected_keys))

    def testBindingGetFieldsMetadata(self):
        """
        Tests that the `getFields` method returns metadata for each field, including description and default value.

        This test ensures that the metadata for each field includes the field name, default value, and a description.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate field metadata.

        Raises
        ------
        AssertionError
            If any required metadata is missing from the field information.
        """
        # Retrieve field metadata from a binding instance
        binding = Binding()
        fields = binding.getFields()
        for field in fields:
            self.assertIn("name", field)
            self.assertIn("default", field)
            self.assertIn("metadata", field)
            # Assert that description is present in metadata
            self.assertIn("description", field["metadata"])

    def testBindingWithCustomInstance(self):
        """
        Tests that the `instance` attribute can be set to a custom object and retrieved correctly.

        This test verifies that assigning a custom object to the `instance` attribute of a `Binding`
        instance is preserved and accessible.

        Parameters
        ----------
        self : TestEntities
            The test case instance.

        Returns
        -------
        None
            This method does not return anything. Assertions are used to validate attribute assignment.

        Raises
        ------
        AssertionError
            If the instance attribute is not set to the custom object as expected.
        """
        # Define a dummy class and create an instance
        class Dummy:
            pass

        obj = Dummy()

        # Assign the custom object to the instance attribute
        binding = Binding(instance=obj)
        self.assertIs(binding.instance, obj)
