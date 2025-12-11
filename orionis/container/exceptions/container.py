class OrionisContainerAttributeError(AttributeError):
    """
    Raise for attribute errors in the Orionis container.

    This exception is used when accessing non-existent attributes or performing
    invalid attribute operations within the Orionis container system.

    Returns
    -------
    None
        This exception does not return a value.
    """


class OrionisContainerException(Exception):
    """
    Raise for general Orionis container errors.

    This is the base exception for all errors related to the Orionis container
    system, providing a common hierarchy for error handling.

    Returns
    -------
    None
        This exception does not return a value.
    """


class OrionisContainerTypeError(TypeError):
    """
    Raise for type errors in the Orionis container.

    This exception indicates type mismatches or invalid type operations within
    the Orionis container functionality.

    Returns
    -------
    None
        This exception does not return a value.
    """


class OrionisContainerValueError(ValueError):
    """
    Raise for value errors in the Orionis container.

    This exception is used for invalid configuration values, incorrect parameter
    types, or values that do not meet expected criteria in container operations.

    Returns
    -------
    None
        This exception does not return a value.
    """


class OrionisContainerCircularDependencyException(Exception):
    """
    Raise when a circular dependency is detected in the Orionis container.

    This exception signals a circular reference among services or components,
    preventing proper dependency resolution.

    Returns
    -------
    None
        This exception does not return a value.
    """
