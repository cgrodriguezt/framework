from __future__ import annotations
import inspect
from typing import Any
from orionis.services.introspection.dependencies.contracts.reflection import (
    IReflectDependencies,
)
from orionis.services.introspection.dependencies.entities.argument import Argument
from orionis.services.introspection.dependencies.entities.signature import (
    SignatureArguments,
)

class ReflectDependencies(IReflectDependencies):

    # ruff: noqa: SLF001, ANN401, PLR0912

    def __init__(self, target: Any | None = None) -> None:
        """
        Initialize the ReflectDependencies instance.

        Parameters
        ----------
        target : Any or None
            The object whose dependencies are to be reflected.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__target = target

    def __paramSkip(self, param_name: str, param: inspect.Parameter) -> bool:
        """
        Determine if a parameter should be skipped during dependency inspection.

        Parameters
        ----------
        param_name : str
            Name of the parameter.
        param : inspect.Parameter
            Parameter object to inspect.

        Returns
        -------
        bool
            True if the parameter should be skipped; otherwise, False.
        """
        # Skip common parameters and special argument names.
        if param_name in {"self", "cls", "args", "kwargs"}:
            return True

        # Skip *args and **kwargs parameters.
        kw_args = {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}
        return param.kind in kw_args

    def __inspectSignature(self, target: Any) -> inspect.Signature:
        """
        Retrieve the signature of a callable target.

        Parameters
        ----------
        target : Any
            The callable object (function, method, or class) to inspect.

        Returns
        -------
        inspect.Signature
            The signature object representing the callable's parameters.

        Raises
        ------
        ValueError
            If the target is not callable or its signature cannot be inspected.
        """
        # Ensure the target is callable before inspecting its signature.
        if not callable(target):
            error_msg = (
                f"Target {target} is not callable and cannot have a signature."
            )
            raise TypeError(error_msg)

        try:
            return inspect.signature(target)
        except (ValueError, TypeError) as e:
            error_msg = (
                f"Unable to inspect signature of {target}: {e!s}"
            )
            raise ValueError(error_msg) from e

    def __getDependencies( # NOSONAR
        self, signature: inspect.Signature,
    ) -> SignatureArguments:
        """
        Categorize function signature parameters as resolved or unresolved dependencies.

        Parameters
        ----------
        signature : inspect.Signature
            The function signature to analyze.

        Returns
        -------
        SignatureArguments
            Contains dictionaries of resolved, unresolved, and ordered dependencies.
        """
        # Store categorized dependencies
        resolved_dependencies: dict[str, Argument] = {}
        unresolved_dependencies: dict[str, Argument] = {}
        ordered_dependencies: dict[str, Argument] = {}

        # Analyze each parameter in the signature
        for param_name, param in signature.parameters.items():
            is_keyword_only: bool = param.kind == inspect.Parameter.KEYWORD_ONLY

            # Skip irrelevant parameters (self, cls, *args, **kwargs)
            if self.__paramSkip(param_name, param):
                continue

            # Parameters without annotation and default are unresolved
            if param.annotation is param.empty and param.default is param.empty:
                unresolved_dependencies[param_name] = Argument(
                    name=param_name,
                    resolved=False,
                    module_name=Any.__module__,
                    class_name=Any.__name__,
                    type=type(Any),
                    full_class_path=str(Any),
                    is_keyword_only=is_keyword_only,
                )
                ordered_dependencies[param_name] = unresolved_dependencies[param_name]
                continue

            # Parameters with default values are resolved
            if param.default is not param.empty:
                resolved_dependencies[param_name] = Argument(
                    name=param_name,
                    resolved=True,
                    module_name=type(param.default).__module__,
                    class_name=type(param.default).__name__,
                    type=type(param.default),
                    full_class_path=f"{type(param.default).__module__}."
                    f"{type(param.default).__name__}",
                    is_keyword_only=is_keyword_only,
                    default=param.default,
                )
                ordered_dependencies[param_name] = resolved_dependencies[param_name]
                continue

            # Parameters with type annotations
            if param.annotation is not param.empty:
                # Handle forward references (string annotations)
                annotation_module: str | None = None
                if isinstance(param.annotation, str):
                    annotation_module = "typing"
                else:
                    annotation_module = getattr(
                        param.annotation,
                        "__module__",
                        "typing",
                    )

                # Builtin types without defaults are unresolved
                if annotation_module == "builtins" and param.default is param.empty:
                    if isinstance(param.annotation, str):
                        annotation_name = param.annotation
                        annotation_type = str
                    else:
                        annotation_name = getattr(
                            param.annotation, "__name__", str(param.annotation),
                        )
                        annotation_type = param.annotation

                    unresolved_dependencies[param_name] = Argument(
                        name=param_name,
                        resolved=False,
                        module_name=annotation_module,
                        class_name=annotation_name,
                        type=annotation_type,
                        is_keyword_only=is_keyword_only,
                        full_class_path=f"{annotation_module}.{annotation_name}",
                    )
                    ordered_dependencies[param_name] = (
                        unresolved_dependencies[param_name]
                    )
                else:
                    # Non-builtin types with annotations are resolved
                    if isinstance(param.annotation, str):
                        annotation_name = param.annotation
                        annotation_type = str
                    else:
                        annotation_name = getattr(
                            param.annotation, "__name__", str(param.annotation),
                        )
                        annotation_type = param.annotation

                    resolved_dependencies[param_name] = Argument(
                        name=param_name,
                        resolved=True,
                        module_name=annotation_module,
                        class_name=annotation_name,
                        type=annotation_type,
                        is_keyword_only=is_keyword_only,
                        full_class_path=f"{annotation_module}.{annotation_name}",
                        default=inspect._empty,
                    )
                    ordered_dependencies[param_name] = resolved_dependencies[param_name]

        return SignatureArguments(
            resolved=resolved_dependencies,
            unresolved=unresolved_dependencies,
            ordered=ordered_dependencies,
        )

    def constructorSignature(self) -> SignatureArguments:
        """
        Inspect the constructor (__init__) method and categorize parameter dependencies.

        Returns
        -------
        SignatureArguments
            Contains resolved and unresolved parameter dependencies.

        Raises
        ------
        ValueError
            If the constructor signature cannot be inspected.
        """
        # Get the constructor signature from the target class.
        return self.__getDependencies(self.__inspectSignature(self.__target.__init__))

    def methodSignature(self, method_name: str) -> SignatureArguments:
        """
        Inspect the signature of a specified method and categorize its dependencies.

        Parameters
        ----------
        method_name : str
            Name of the method to inspect.

        Returns
        -------
        SignatureArguments
            Categorized resolved and unresolved parameter dependencies.

        Raises
        ------
        ValueError
            If the method does not exist or its signature cannot be inspected.
        """
        # Retrieve the method from the target and inspect its signature.
        return self.__getDependencies(
            self.__inspectSignature(getattr(self.__target, method_name)),
        )

    def callableSignature(self) -> SignatureArguments:
        """
        Inspect the callable target and categorize its parameter dependencies.

        Returns
        -------
        SignatureArguments
            Contains resolved and unresolved parameter dependencies.

        Raises
        ------
        ValueError
            If the target is not callable or its signature cannot be inspected.
        """
        # Extract the callable signature from the target object.
        return self.__getDependencies(inspect.signature(self.__target))
