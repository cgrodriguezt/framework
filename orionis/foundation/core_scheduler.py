from types import MappingProxyType
from orionis.console.base.scheduler import BaseScheduler

def get_core_scheduler_mapping() -> MappingProxyType:
    """
    Return an immutable mapping with core scheduler module and class information.

    Returns
    -------
    MappingProxyType
        Immutable mapping containing the 'module' and 'class' keys, referencing
        the BaseScheduler's module and class name.
    """
    # Build an immutable mapping for BaseScheduler's module and class info
    return MappingProxyType({
        "module": BaseScheduler.__module__,
        "class": BaseScheduler.__name__,
    })

CORE_SCHEDULER: MappingProxyType = get_core_scheduler_mapping()
