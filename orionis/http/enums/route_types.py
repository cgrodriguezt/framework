from enum import StrEnum

class RouteTypes(StrEnum):
    """
    Define the types of routes available in the framework.

    Attributes
    ----------
    CONTROLLER_METHOD : RouteTypes
        Route that requires a controller and a method.
    CONTROLLER_CALL : RouteTypes
        Route that invokes the controller's __call__ method.
    FUNCTION : RouteTypes
        Route that is a function (not a lambda).

    Returns
    -------
    RouteTypes
        An enumeration member representing the route type.
    """

    # Default route type when no specific type is provided
    DEFAULT = "default"

    # Route requiring a controller and method
    CONTROLLER_METHOD = "controller_method"

    # Route invoking the controller's __call__ method
    CONTROLLER_CALL = "controller_call"

    # Route that is a function (not a lambda)
    FUNCTION = "function"
