import inspect
import sys
from typing import Any, Dict, get_type_hints
from orionis.services.introspection.dependencies.contracts.reflection import IReflectDependencies
from orionis.services.introspection.dependencies.entities.argument import Argument
from orionis.services.introspection.dependencies.entities.signature import SignatureArguments
from orionis.services.introspection.dependencies.type_checking_resolver import TypeCheckingResolver
from orionis.services.introspection.exceptions import ReflectionValueError

class ReflectDependencies(IReflectDependencies):

    def __init__(self, target = None):
        """
        Initializes the ReflectDependencies instance with the given object.

        Parameters
        ----------
        target : Any
            The object whose dependencies are to be reflected.
        """
        self.__target = target
        self.__type_checking_resolved: dict[str, Any] = {}

    def __paramSkip(self, param_name: str, param: inspect.Parameter) -> bool:
        """
        Determines whether a parameter should be skipped during dependency inspection.

        Parameters
        ----------
        param_name : str
            The name of the parameter.
        param : inspect.Parameter
            The parameter object to inspect.

        Returns
        -------
        bool
            True if the parameter should be skipped, False otherwise.
        """
        # Skip common parameters like 'self', 'cls', or special argument names
        if param_name in {'self', 'cls', 'args', 'kwargs'}:
            return True

        # Skip 'self' in class methods or instance methods
        if param_name == 'self' and isinstance(self.__target, type):
            return True

        # Skip special parameters like *args and **kwargs
        if param.kind in {param.VAR_POSITIONAL, param.VAR_KEYWORD}:
            return True

        return False

    def __typeCheckingResolver(self, module_name: str) -> dict[str, Any]:
        """
        Resolve type checking imports for a given module.

        Parameters
        ----------
        module_name : str
            Name of the module to resolve type checking imports for.

        Returns
        -------
        Dict[str, Any]
            Dictionary mapping symbol names to imported objects.
        """
        # Cache resolved type checking imports for efficiency
        if module_name not in self.__type_checking_resolved:
            self.__type_checking_resolved = TypeCheckingResolver.fromModule(module_name)
        return self.__type_checking_resolved

    def __inspectSignature(self, target) -> inspect.Signature:
        """
        Safely retrieves the signature of a given target.

        Parameters
        ----------
        target : Any
            The target object (function, method, or callable) to inspect.

        Returns
        -------
        inspect.Signature
            The signature of the target.

        Raises
        ------
        ReflectionValueError
            If the signature cannot be inspected.
        """
        if not callable(target):
            raise ReflectionValueError(f"Target {target} is not callable and cannot have a signature.")

        try:
            return inspect.signature(target)
        except (ReflectionValueError, TypeError) as e:
            raise ReflectionValueError(f"Unable to inspect signature of {target}: {str(e)}")

    def __getDependencies(self, signature: inspect.Signature) -> SignatureArguments:
        """
        Categorizes function signature parameters as resolved or unresolved dependencies.

        Parameters
        ----------
        signature : inspect.Signature
            The function signature to analyze.

        Returns
        -------
        SignatureArguments
            Contains resolved and unresolved parameter dependencies.
        """

        # Initialize dictionaries to store categorized dependencies
        resolved_dependencies: Dict[str, Argument] = {}
        unresolved_dependencies: Dict[str, Argument] = {}
        ordered_dependencies: Dict[str, Argument] = {}

        # Iterate through all parameters in the signature
        for param_name, param in signature.parameters.items():

            # Check if the parameter is keyword-only (appears after '*')
            is_keyword_only = param.kind == inspect.Parameter.KEYWORD_ONLY

            # Skip parameters that are not relevant for dependency resolution
            # (self, cls, *args, **kwargs, etc.)
            if self.__paramSkip(param_name, param):
                continue

            # Handle string-based type annotations using TYPE_CHECKING imports
            if (
                param.annotation is not inspect._empty
                and isinstance(param.annotation, str)
            ):
                type_checking = self.__typeCheckingResolver(self.__target.__module__)
                type_ = type_checking.get(param.annotation, None)
                if type_ is not None:
                    resolved_dependencies[param_name] = Argument(
                        name=param_name,
                        resolved=True,
                        module_name=type_.__module__,
                        class_name=type_.__name__,
                        type=type_,
                        full_class_path=f"{type_.__module__}.{type_.__name__}",
                        is_keyword_only=is_keyword_only
                    )
                    ordered_dependencies[param_name] = resolved_dependencies[param_name]
                    continue

            # Case 1: Parameters with no annotation and no default value
            # These cannot be resolved automatically and require manual provision
            if param.annotation is param.empty and param.default is param.empty:
                unresolved_dependencies[param_name] = Argument(
                    name=param_name,
                    resolved=False,
                    module_name=Any.__module__,
                    class_name=Any.__name__,
                    type=type(Any),
                    full_class_path=str(Any),
                    is_keyword_only=is_keyword_only
                )
                ordered_dependencies[param_name] = unresolved_dependencies[param_name]
                continue

            # Case 2: Parameters with default values
            # These are always considered resolved since they have fallback values
            if param.default is not param.empty:
                resolved_dependencies[param_name] = Argument(
                    name=param_name,
                    resolved=True,
                    module_name=type(param.default).__module__,
                    class_name=type(param.default).__name__,
                    type=type(param.default),
                    full_class_path=f"{type(param.default).__module__}.{type(param.default).__name__}",
                    is_keyword_only=is_keyword_only,
                    default=param.default
                )
                ordered_dependencies[param_name] = resolved_dependencies[param_name]
                continue

            # Case 3: Parameters with type annotations
            if param.annotation is not param.empty:
                # Special handling for builtin types without defaults
                # Builtin types (int, str, bool, etc.) are considered unresolved
                # when they lack default values, as they typically need explicit values
                if isinstance(param.annotation, str) or (param.annotation.__module__ == 'builtins' and param.default is param.empty):
                    module_name = param.annotation.__module__ if not isinstance(param.annotation, str) else 'builtins'
                    class_name = param.annotation.__name__ if not isinstance(param.annotation, str) else param.annotation
                    unresolved_dependencies[param_name] = Argument(
                        name=param_name,
                        resolved=False,
                        module_name=module_name,
                        class_name=class_name,
                        type=param.annotation,
                        is_keyword_only=is_keyword_only,
                        full_class_path=f"{module_name}.{class_name}"
                    )
                    ordered_dependencies[param_name] = unresolved_dependencies[param_name]
                else:
                    # Non-builtin types with annotations are considered resolved
                    # as they can be instantiated by the dependency injection system
                    resolved_dependencies[param_name] = Argument(
                        name=param_name,
                        resolved=True,
                        module_name=param.annotation.__module__,
                        class_name=param.annotation.__name__,
                        type=param.annotation,
                        is_keyword_only=is_keyword_only,
                        full_class_path=f"{param.annotation.__module__}.{param.annotation.__name__}"
                    )
                    ordered_dependencies[param_name] = resolved_dependencies[param_name]

        # Return the categorized dependencies
        return SignatureArguments(
            resolved=resolved_dependencies,
            unresolved=unresolved_dependencies,
            ordered=ordered_dependencies
        )

    def constructorSignature(self) -> SignatureArguments:
        """
        Inspects the constructor (__init__) method to categorize parameter dependencies.

        Returns
        -------
        SignatureArguments
            Object containing resolved and unresolved parameter dependencies.

        Raises
        ------
        ReflectionValueError
            If the constructor signature cannot be inspected.
        """

        # Extract the constructor signature from the target class
        return self.__getDependencies(self.__inspectSignature(self.__target.__init__))

    def methodSignature(self, method_name: str) -> SignatureArguments:
        """
        Inspects a specific method's signature to categorize its parameter dependencies.

        Parameters
        ----------
        method_name : str
            The name of the method to inspect.

        Returns
        -------
        SignatureArguments
            Object containing resolved and unresolved parameter dependencies.

        Raises
        ------
        ReflectionValueError
            If the method doesn't exist or signature cannot be inspected.
        """

        # Extract the method signature from the target class
        return self.__getDependencies(self.__inspectSignature(getattr(self.__target, method_name)))

    def callableSignature(self) -> SignatureArguments:
        """
        Inspects a callable target to identify and categorize its parameter dependencies.

        Returns
        -------
        SignatureArguments
            Object containing resolved and unresolved parameter dependencies.

        Raises
        ------
        ReflectionValueError
            If the target is not callable or signature cannot be inspected.
        """

        # Extract the callable signature from the target object
        return self.__getDependencies(inspect.signature(self.__target))