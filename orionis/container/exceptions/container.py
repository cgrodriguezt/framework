class OrionisContainerAttributeError(AttributeError):
    """
    Custom AttributeError exception for Orionis container operations.

    This exception is raised when there are attribute-related errors specific to
    the Orionis container system, such as accessing non-existent attributes or
    improper attribute operations within the container framework.

    Inherits from:
        AttributeError: The built-in Python AttributeError exception.
    """
    pass

class OrionisContainerException(Exception):
    """
    Base exception class for all Orionis container-related errors.

    This exception serves as the parent class for all exceptions that can occur
    within the Orionis container system, providing a common base for error handling
    and exception hierarchy management.

    Raises:
        OrionisContainerException: When a general container-related error occurs.
    """
    pass

class OrionisContainerTypeError(TypeError):
    """
    Exception raised when there is a type-related error in the Orionis container system.

    This exception is a specialized TypeError that indicates type mismatches or invalid
    type operations within the Orionis framework's container functionality.

    Inherits from:
        TypeError: The built-in Python exception for type-related errors.

    Example:
        >>> raise OrionisContainerTypeError("Invalid container type provided")
        OrionisContainerTypeError: Invalid container type provided
    """
    pass

class OrionisContainerValueError(ValueError):
    """
    Custom ValueError exception for Orionis container operations.

    This exception is raised when a value-related error occurs during container
    operations, such as invalid configuration values, incorrect parameter types,
    or values that don't meet the expected criteria for container functionality.

    Inherits from:
        ValueError: Built-in exception for inappropriate argument values.

    Example:
        raise OrionisContainerValueError("Invalid service configuration provided")
    """
    pass

class OrionisContainerCircularDependencyException(Exception):
    """
    Exception raised when a circular dependency is detected in the Orionis container.

    This exception indicates that a circular reference has been found among
    services or components managed by the Orionis container, preventing proper
    resolution and instantiation of dependencies.

    Inherits from:
        Exception: The base class for all built-in exceptions in Python.
    Example:
        >>> raise OrionisContainerCircularDependencyException("Circular dependency detected")
        OrionisContainerCircularDependencyException: Circular dependency detected
    """
    pass