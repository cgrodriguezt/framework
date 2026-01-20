from orionis.test.cases.synchronous import SyncTestCase
from tests.support.entities.mock_dataclass import (
    Color, ExampleEntity, ComplexEntity,
    CustomPostInitEntity, EmptyEntity, NestedEntity,
)

class TestBaseEntity(SyncTestCase):

    def setUp(self):
        """
        Initialize test environment before each test method.

        Creates various entity instances for comprehensive testing of BaseEntity
        functionality across different scenarios and field types.

        Returns
        -------
        None
        """
        # Basic entity with custom values
        self.entity = ExampleEntity(id=42, name="test", color=Color.GREEN, tags=["a", "b"])

        # Entity with default values only
        self.defaultEntity = ExampleEntity()

        # Complex entity with advanced field types
        self.complexEntity = ComplexEntity(
            union_field=123,
            optional_field="optional_value",
            nested=NestedEntity(value="custom_nested", nested_color=Color.GREEN),
        )

        # Empty entity for minimal case testing
        self.emptyEntity = EmptyEntity()

        # Entity with custom post-init logic
        self.postInitEntity = CustomPostInitEntity(base_value="custom_base")

    def testToDictBasic(self):
        """
        Test the toDict method with basic field types and custom values.

        Verifies that toDict correctly converts a dataclass instance to a dictionary
        representation, preserving all field values and their correct types.

        Returns
        -------
        None
        """
        result = self.entity.toDict()
        self.assertIsInstance(result, dict)

        # Check individual field values
        self.assertEqual(result["id"], 42)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["color"], Color.GREEN)
        self.assertEqual(result["tags"], ["a", "b"])

    def testToDictWithDefaults(self):
        """
        Test the toDict method with an entity using only default values.

        Ensures that default values are properly included in the dictionary
        representation, including factory-generated defaults.

        Returns
        -------
        None
        """
        result = self.defaultEntity.toDict()
        self.assertIsInstance(result, dict)

        # Check default values
        self.assertEqual(result["id"], 0)
        self.assertEqual(result["name"], "default")
        self.assertEqual(result["color"], Color.RED)
        self.assertEqual(result["tags"], [])

    def testToDictWithNestedDataclass(self):
        """
        Test the toDict method with nested dataclass entities.

        Verifies that nested dataclass instances are properly converted to
        dictionaries recursively, maintaining the hierarchical structure.

        Returns
        -------
        None
        """
        result = self.complexEntity.toDict()
        self.assertIsInstance(result, dict)

        # Check nested dataclass conversion
        self.assertIsInstance(result["nested"], dict)
        self.assertEqual(result["nested"]["value"], "custom_nested")
        self.assertEqual(result["nested"]["nested_color"], Color.GREEN)

    def testToDictWithUnionTypes(self):
        """
        Test the toDict method with Union type fields.

        Ensures that fields with Union types are correctly represented
        in the dictionary output regardless of which type is active.

        Returns
        -------
        None
        """
        result = self.complexEntity.toDict()

        # Union field should be preserved as-is
        self.assertEqual(result["union_field"], 123)
        self.assertIsInstance(result["union_field"], int)

    def testToDictWithOptionalFields(self):
        """
        Test the toDict method with Optional (nullable) fields.

        Verifies proper handling of Optional fields, including None values
        and their representation in the resulting dictionary.

        Returns
        -------
        None
        """
        # Test with None value
        entity = ComplexEntity(optional_field=None)
        result = entity.toDict()
        self.assertIsNone(result["optional_field"])

        # Test with actual value
        entity_with_value = ComplexEntity(optional_field="has_value")
        result_with_value = entity_with_value.toDict()
        self.assertEqual(result_with_value["optional_field"], "has_value")

    def testToDictEmpty(self):
        """
        Test the toDict method with an empty entity (no fields).

        Ensures that entities without fields return an empty dictionary
        without raising exceptions.

        Returns
        -------
        None
        """
        result = self.emptyEntity.toDict()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)

    def testGetFieldsBasic(self):
        """
        Test the getFields method with basic field types.

        Verifies that getFields returns comprehensive field information including
        names, types, defaults, and metadata for all entity fields.

        Returns
        -------
        None
        """
        fields_info = self.entity.getFields()
        self.assertIsInstance(fields_info, list)
        self.assertEqual(len(fields_info), 4)

        # Extract field names for verification
        names = [f["name"] for f in fields_info]
        self.assertIn("id", names)
        self.assertIn("name", names)
        self.assertIn("color", names)
        self.assertIn("tags", names)

        # Check that each field info contains required keys
        for field_info in fields_info:
            self.assertIn("name", field_info)
            self.assertIn("types", field_info)
            self.assertIn("default", field_info)
            self.assertIn("metadata", field_info)
            self.assertIsInstance(field_info["types"], list)

    def testGetFieldsTypes(self):
        """
        Test the getFields method type resolution for various field types.

        Ensures that different field types (simple, Union, Optional) are
        correctly identified and represented as lists of type names.

        Returns
        -------
        None
        """
        fields_info = self.complexEntity.getFields()
        field_by_name = {f["name"]: f for f in fields_info}

        # Check simple type
        union_field = field_by_name["union_field"]
        self.assertIsInstance(union_field["types"], list)

        # Check nested dataclass type
        nested_field = field_by_name["nested"]
        self.assertIn("NestedEntity", nested_field["types"])

    def testGetFieldsDefaults(self):
        """
        Test the getFields method default value resolution.

        Verifies that various types of default values (direct, factory, callable,
        metadata) are correctly resolved and represented in field information.

        Returns
        -------
        None
        """
        fields_info = self.complexEntity.getFields()
        field_by_name = {f["name"]: f for f in fields_info}

        # Check callable default
        callable_field = field_by_name["callable_default"]
        self.assertEqual(callable_field["default"], "callback_result")

        # Check factory enum default
        factory_enum_field = field_by_name["factory_enum"]
        self.assertEqual(factory_enum_field["default"], "low")

        # Check metadata default override
        metadata_field = field_by_name["metadata_default"]
        self.assertEqual(metadata_field["metadata"]["default"], "metadata_override")

    def testGetFieldsMetadata(self):
        """
        Test the getFields method metadata handling.

        Ensures that field metadata is properly extracted and normalized,
        including custom default values defined in metadata.

        Returns
        -------
        None
        """
        fields_info = self.entity.getFields()
        field_by_name = {f["name"]: f for f in fields_info}

        # Check tags field metadata
        tags_field = field_by_name["tags"]
        self.assertIn("default", tags_field["metadata"])
        self.assertEqual(tags_field["metadata"]["default"], ["tag1", "tag2"])

    def testGetFieldsWithFactoryDefaults(self):
        """
        Test the getFields method with default_factory fields.

        Verifies that fields using default_factory are properly handled,
        including execution of factory functions and normalization of results.

        Returns
        -------
        None
        """
        fields_info = self.entity.getFields()
        field_by_name = {f["name"]: f for f in fields_info}

        # Tags field uses default_factory
        tags_field = field_by_name["tags"]
        self.assertEqual(tags_field["default"], [])  # Empty list from factory

    def testGetFieldsEnumHandling(self):
        """
        Test the getFields method handling of Enum types and values.

        Ensures that Enum fields have their values properly extracted and
        normalized to their underlying values rather than Enum instances.

        Returns
        -------
        None
        """
        fields_info = self.entity.getFields()
        field_by_name = {f["name"]: f for f in fields_info}

        # Color field is an Enum
        color_field = field_by_name["color"]
        self.assertEqual(color_field["default"], 1)  # Color.RED.value

    def testGetFieldsEmpty(self):
        """
        Test the getFields method with an empty entity.

        Verifies that entities without fields return an empty list
        without raising exceptions.

        Returns
        -------
        None
        """
        fields_info = self.emptyEntity.getFields()
        self.assertIsInstance(fields_info, list)
        self.assertEqual(len(fields_info), 0)

    def testPostInitHook(self):
        """
        Test the __post_init__ method functionality.

        This tests the hook mechanism that allows subclasses to perform
        custom initialization logic after dataclass initialization.

        Returns
        -------
        None
        """
        # Verify that custom post-init logic was executed
        self.assertEqual(self.postInitEntity.base_value, "custom_base")
        self.assertEqual(self.postInitEntity.computed_value, "computed_from_custom_base")

    def testPostInitDefault(self):
        """
        Test the default __post_init__ implementation.

        Verifies that the base __post_init__ method can be called without
        side effects and doesn't interfere with normal entity operation.

        Returns
        -------
        None
        """
        # Default post_init should not raise any exceptions
        entity = ExampleEntity()
        entity.__post_init__()

        # Entity should remain functional
        self.assertEqual(entity.name, "default")
        self.assertIsInstance(entity.toDict(), dict)

    def testInheritanceBehavior(self):
        """
        Test BaseEntity behavior when inherited by dataclass entities.

        Ensures that all BaseEntity methods work correctly when the class
        is used as a base class for dataclass-decorated entities.

        Returns
        -------
        None
        """
        # Test that inherited entity maintains all functionality
        result_dict = self.postInitEntity.toDict()
        self.assertIn("base_value", result_dict)
        self.assertIn("computed_value", result_dict)

        fields_info = self.postInitEntity.getFields()
        self.assertEqual(len(fields_info), 2)

    def testFieldOrderConsistency(self):
        """
        Test that getFields returns fields in consistent order.

        Verifies that field information is returned in a predictable order,
        typically matching the definition order in the dataclass.

        Returns
        -------
        None
        """
        fields_info = self.entity.getFields()
        field_names = [f["name"] for f in fields_info]

        # Should match the order in the dataclass definition
        expected_order = ["id", "name", "color", "tags"]
        self.assertEqual(field_names, expected_order)

    def testComplexTypeRepresentation(self):
        """
        Test representation of complex field types in getFields.

        Ensures that complex types like Union, Optional, and custom classes
        are properly represented in the types list returned by getFields.

        Returns
        -------
        None
        """
        fields_info = self.complexEntity.getFields()
        field_by_name = {f["name"]: f for f in fields_info}

        # Union field should have multiple types represented
        union_field = field_by_name["union_field"]
        self.assertIsInstance(union_field["types"], list)
        self.assertGreater(len(union_field["types"]), 0)
