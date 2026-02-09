import pytest
import inspect
from typing import List, Optional, Dict, Any
from unittest.mock import Mock

from orionis.services.introspection.dependencies.reflection import ReflectDependencies
from orionis.services.introspection.dependencies.entities.argument import Argument
from orionis.services.introspection.dependencies.entities.signature import SignatureArguments
from orionis.services.introspection.exceptions import ReflectionValueError


# Test classes and functions for various scenarios
class MockServiceBasic:
    def __init__(self, name: str, age: int = 25):
        self.name = name
        self.age = age

class MockServiceComplex:
    def __init__(self, 
                 service_a: 'MockServiceBasic', 
                 required_builtin: str,
                 optional_builtin: int = 10,
                 optional_service: Optional['MockServiceBasic'] = None,
                 *, keyword_only_param: bool = True):
        pass

class MockServiceNoAnnotations:
    def __init__(self, param1, param2=None):
        pass

class MockServiceWithMethods:
    def __init__(self, service: MockServiceBasic):
        pass
    
    def method_with_deps(self, param1: str, service: MockServiceBasic, default_param: int = 5):
        pass
    
    def method_no_deps(self):
        pass
    
    @classmethod
    def class_method(cls, param: str):
        pass
    
    @staticmethod
    def static_method(param: str):
        pass

def standalone_function(param1: str, service: MockServiceBasic, default: int = 10):
    pass

def function_with_varargs(param1: str, *args, service: MockServiceBasic = None, **kwargs):
    pass

def function_no_params():
    pass

class TestReflectDependencies:

    def test_initialization_with_target(self):
        """Test that ReflectDependencies initializes correctly with a target."""
        target = MockServiceBasic
        reflector = ReflectDependencies(target)
        assert reflector._ReflectDependencies__target == target

    def test_initialization_without_target(self):
        """Test that ReflectDependencies initializes with None target."""
        reflector = ReflectDependencies()
        assert reflector._ReflectDependencies__target is None

    def test_constructor_signature_basic(self):
        """Test constructor signature analysis for basic class."""
        reflector = ReflectDependencies(MockServiceBasic)
        result = reflector.constructorSignature()
        
        assert isinstance(result, SignatureArguments)
        
        # Should have 'name' as unresolved (builtin without default)
        assert 'name' in result.unresolved
        assert result.unresolved['name'].resolved is False
        assert result.unresolved['name'].type == str
        
        # Should have 'age' as resolved (has default)
        assert 'age' in result.resolved
        assert result.resolved['age'].resolved is True
        assert result.resolved['age'].default == 25

    def test_constructor_signature_complex(self):
        """Test constructor signature analysis for complex class with various parameter types."""
        reflector = ReflectDependencies(MockServiceComplex)
        result = reflector.constructorSignature()
        
        # service_a: non-builtin type should be resolved
        assert 'service_a' in result.resolved
        assert result.resolved['service_a'].resolved is True
        assert result.resolved['service_a'].is_keyword_only is False
        
        # required_builtin: builtin without default should be unresolved
        assert 'required_builtin' in result.unresolved
        assert result.unresolved['required_builtin'].resolved is False
        assert result.unresolved['required_builtin'].type == str
        
        # optional_builtin: has default should be resolved
        assert 'optional_builtin' in result.resolved
        assert result.resolved['optional_builtin'].resolved is True
        assert result.resolved['optional_builtin'].default == 10
        
        # optional_service: has default (None) should be resolved
        assert 'optional_service' in result.resolved
        assert result.resolved['optional_service'].resolved is True
        assert result.resolved['optional_service'].default is None
        
        # keyword_only_param: should be marked as keyword-only
        assert 'keyword_only_param' in result.resolved
        assert result.resolved['keyword_only_param'].is_keyword_only is True
        assert result.resolved['keyword_only_param'].default is True

    def test_constructor_signature_no_annotations(self):
        """Test constructor signature analysis for class without type annotations."""
        reflector = ReflectDependencies(MockServiceNoAnnotations)
        result = reflector.constructorSignature()
        
        # param1: no annotation, no default should be unresolved
        assert 'param1' in result.unresolved
        assert result.unresolved['param1'].resolved is False
        
        # param2: no annotation but has default should be resolved
        assert 'param2' in result.resolved
        assert result.resolved['param2'].resolved is True
        assert result.resolved['param2'].default is None

    def test_method_signature_analysis(self):
        """Test method signature analysis."""
        reflector = ReflectDependencies(MockServiceWithMethods)
        result = reflector.methodSignature('method_with_deps')
        
        # Should skip 'self'
        assert 'self' not in result.resolved
        assert 'self' not in result.unresolved
        
        # param1: builtin without default should be unresolved
        assert 'param1' in result.unresolved
        assert result.unresolved['param1'].type == str
        
        # service: non-builtin should be resolved
        assert 'service' in result.resolved
        assert result.resolved['service'].resolved is True
        
        # default_param: has default should be resolved
        assert 'default_param' in result.resolved
        assert result.resolved['default_param'].default == 5

    def test_method_signature_no_deps(self):
        """Test method signature analysis for method with no dependencies."""
        reflector = ReflectDependencies(MockServiceWithMethods)
        result = reflector.methodSignature('method_no_deps')
        
        # Should have no dependencies (only self which is filtered)
        assert len(result.resolved) == 0
        assert len(result.unresolved) == 0
        assert len(result.ordered) == 0

    def test_class_method_signature(self):
        """Test class method signature analysis."""
        reflector = ReflectDependencies(MockServiceWithMethods)
        result = reflector.methodSignature('class_method')
        
        # Should skip 'cls'
        assert 'cls' not in result.resolved
        assert 'cls' not in result.unresolved
        
        # param should be unresolved (builtin without default)
        assert 'param' in result.unresolved

    def test_static_method_signature(self):
        """Test static method signature analysis."""
        reflector = ReflectDependencies(MockServiceWithMethods)
        result = reflector.methodSignature('static_method')
        
        # param should be unresolved (builtin without default)
        assert 'param' in result.unresolved

    def test_callable_signature_standalone_function(self):
        """Test callable signature analysis for standalone function."""
        reflector = ReflectDependencies(standalone_function)
        result = reflector.callableSignature()
        
        # param1: builtin without default should be unresolved
        assert 'param1' in result.unresolved
        
        # service: non-builtin should be resolved
        assert 'service' in result.resolved
        
        # default: has default should be resolved
        assert 'default' in result.resolved
        assert result.resolved['default'].default == 10

    def test_callable_signature_with_varargs(self):
        """Test callable signature analysis for function with *args and **kwargs."""
        reflector = ReflectDependencies(function_with_varargs)
        result = reflector.callableSignature()
        
        # Should skip *args and **kwargs
        assert 'args' not in result.resolved
        assert 'args' not in result.unresolved
        assert 'kwargs' not in result.resolved
        assert 'kwargs' not in result.unresolved
        
        # param1: builtin without default should be unresolved
        assert 'param1' in result.unresolved
        
        # service: has default should be resolved
        assert 'service' in result.resolved
        assert result.resolved['service'].default is None

    def test_callable_signature_no_params(self):
        """Test callable signature analysis for function with no parameters."""
        reflector = ReflectDependencies(function_no_params)
        result = reflector.callableSignature()
        
        # Should have no dependencies
        assert len(result.resolved) == 0
        assert len(result.unresolved) == 0
        assert len(result.ordered) == 0

    def test_param_skip_functionality(self):
        """Test parameter skipping logic."""
        reflector = ReflectDependencies(MockServiceBasic)
        
        # Mock parameters to test skipping logic
        mock_param_self = Mock()
        mock_param_self.kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert reflector._ReflectDependencies__paramSkip('self', mock_param_self) is True
        
        mock_param_cls = Mock()
        mock_param_cls.kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert reflector._ReflectDependencies__paramSkip('cls', mock_param_cls) is True
        
        # Test actual *args and **kwargs parameter kinds
        mock_param_args = Mock()
        mock_param_args.kind = inspect.Parameter.VAR_POSITIONAL
        assert reflector._ReflectDependencies__paramSkip('any_name_for_args', mock_param_args) is True
        
        mock_param_kwargs = Mock()
        mock_param_kwargs.kind = inspect.Parameter.VAR_KEYWORD
        assert reflector._ReflectDependencies__paramSkip('any_name_for_kwargs', mock_param_kwargs) is True
        
        mock_param_normal = Mock()
        mock_param_normal.kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert reflector._ReflectDependencies__paramSkip('normal_param', mock_param_normal) is False

    def test_inspect_signature_non_callable(self):
        """Test inspect signature with non-callable target."""
        non_callable = "not a function"
        reflector = ReflectDependencies(non_callable)
        
        with pytest.raises(ReflectionValueError, match="not callable"):
            reflector._ReflectDependencies__inspectSignature(non_callable)

    def test_inspect_signature_success(self):
        """Test successful signature inspection."""
        reflector = ReflectDependencies(MockServiceBasic)
        signature = reflector._ReflectDependencies__inspectSignature(MockServiceBasic.__init__)
        
        assert isinstance(signature, inspect.Signature)
        assert 'self' in signature.parameters
        assert 'name' in signature.parameters
        assert 'age' in signature.parameters

    def test_method_signature_nonexistent_method(self):
        """Test method signature analysis for non-existent method."""
        reflector = ReflectDependencies(MockServiceBasic)
        
        with pytest.raises(AttributeError):
            reflector.methodSignature('nonexistent_method')

    def test_constructor_signature_none_target(self):
        """Test constructor signature analysis with None target."""
        reflector = ReflectDependencies(None)
        
        # None.__init__ has signature (self, /, *args, **kwargs)
        # All parameters should be filtered out
        result = reflector.constructorSignature()
        assert len(result.resolved) == 0
        assert len(result.unresolved) == 0
        assert len(result.ordered) == 0

    def test_ordered_dependencies_preservation(self):
        """Test that ordered dependencies preserve parameter order."""
        reflector = ReflectDependencies(MockServiceComplex)
        result = reflector.constructorSignature()
        
        # Check that ordered dict maintains parameter order
        ordered_keys = list(result.ordered.keys())
        expected_order = ['service_a', 'required_builtin', 'optional_builtin', 'optional_service', 'keyword_only_param']
        assert ordered_keys == expected_order

    def test_full_class_path_generation(self):
        """Test that full class paths are generated correctly."""
        reflector = ReflectDependencies(MockServiceBasic)
        result = reflector.constructorSignature()
        
        # Check builtin type path
        name_arg = result.unresolved['name']
        assert name_arg.full_class_path == 'builtins.str'
        assert name_arg.module_name == 'builtins'
        assert name_arg.class_name == 'str'
        
        # Check default value type path
        age_arg = result.resolved['age']
        assert age_arg.full_class_path == 'builtins.int'

    def test_type_annotation_handling(self):
        """Test handling of different type annotations."""
        class MockGenericTypes:
            def __init__(self, 
                        basic_list: List[str],
                        optional_param: Optional[int],
                        dict_param: Dict[str, Any]):
                pass
        
        reflector = ReflectDependencies(MockGenericTypes)
        result = reflector.constructorSignature()
        
        # All non-builtin types should be resolved
        assert 'basic_list' in result.resolved
        assert 'optional_param' in result.resolved
        assert 'dict_param' in result.resolved
        
        # Check that typing module is handled correctly
        assert result.resolved['basic_list'].module_name == 'typing'

    def test_callable_signature_with_lambda(self):
        """Test callable signature analysis with lambda function."""
        lambda_func = lambda x, y=5: x + y
        reflector = ReflectDependencies(lambda_func)
        result = reflector.callableSignature()
        
        # x should be unresolved (no annotation, no default)
        assert 'x' in result.unresolved
        
        # y should be resolved (has default)
        assert 'y' in result.resolved
        assert result.resolved['y'].default == 5

    def test_error_handling_in_signature_inspection(self):
        """Test error handling in signature inspection."""
        def problematic_function():
            pass
        
        # Mock a scenario where inspect.signature raises an error
        reflector = ReflectDependencies(problematic_function)
        original_signature = inspect.signature
        
        def mock_signature_error(target):
            raise TypeError("Mocked signature error")
        
        inspect.signature = mock_signature_error
        
        try:
            with pytest.raises(ReflectionValueError, match="Unable to inspect signature"):
                reflector._ReflectDependencies__inspectSignature(problematic_function)
        finally:
            inspect.signature = original_signature

    def test_edge_case_empty_signature(self):
        """Test handling of functions with no parameters."""
        def empty_function():
            pass
        
        reflector = ReflectDependencies(empty_function)
        signature = reflector._ReflectDependencies__inspectSignature(empty_function)
        result = reflector._ReflectDependencies__getDependencies(signature)
        
        assert len(result.resolved) == 0
        assert len(result.unresolved) == 0
        assert len(result.ordered) == 0

    def test_builtin_types_categorization(self):
        """Test proper categorization of builtin vs non-builtin types."""
        class MockBuiltinTypes:
            def __init__(self, 
                        int_param: int,
                        bool_param: bool,
                        custom_service: MockServiceBasic,
                        str_param: str = "default",
                        float_param: float = 3.14):
                pass
        
        reflector = ReflectDependencies(MockBuiltinTypes)
        result = reflector.constructorSignature()
        
        # Builtin types without defaults should be unresolved
        assert 'int_param' in result.unresolved
        assert 'bool_param' in result.unresolved
        
        # Builtin types with defaults should be resolved
        assert 'str_param' in result.resolved
        assert 'float_param' in result.resolved
        
        # Non-builtin types should be resolved regardless of default
        assert 'custom_service' in result.resolved

    @pytest.mark.parametrize("param_name,should_skip", [
        ('self', True),
        ('cls', True),
        ('args', True),
        ('kwargs', True),
        ('normal_param', False),
        ('_private', False),
        ('__dunder__', False),
    ])
    def test_param_skip_edge_cases(self, param_name, should_skip):
        """Test parameter skipping with various parameter names."""
        reflector = ReflectDependencies(MockServiceBasic)
        mock_param = Mock()
        mock_param.kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
        
        result = reflector._ReflectDependencies__paramSkip(param_name, mock_param)
        assert result == should_skip

if __name__ == '__main__':
    pytest.main([__file__])