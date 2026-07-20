from types import MappingProxyType
from orionis.failure.base.handler import BaseExceptionHandler

def get_core_exception_handler_mapping() -> MappingProxyType:
    """
    Return an immutable mapping for the default exception handler.

    Returns
    -------
    MappingProxyType
        An immutable mapping containing the 'module' and 'class' keys, referencing
        the default exception handler's module and class name.
    """
    # Build an immutable mapping for the default exception handler's module and class
    return MappingProxyType({
        "module": BaseExceptionHandler.__module__,
        "class": BaseExceptionHandler.__name__,
    })

CORE_EXCEPTION_HANDLER: MappingProxyType = get_core_exception_handler_mapping()
