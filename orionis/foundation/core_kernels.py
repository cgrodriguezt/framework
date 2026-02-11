from types import MappingProxyType
from orionis.console.kernel import KernelCLI
from orionis.http.kernel import KernelHTTP

def get_core_kernels_mapping() -> MappingProxyType:
    """
    Return an immutable mapping of core kernel class metadata.

    Create and return a MappingProxyType containing metadata for each core
    kernel class. The mapping includes the module and class name for each
    kernel.

    Returns
    -------
    MappingProxyType
        Immutable mapping with kernel type as key and a dictionary containing
        'module' and 'class' as values.
    """
    # Initialize empty dictionary to store kernel metadata
    kernels = {}

    # Define core kernel classes mapping
    kernel_mapping = {
        "KernelCLI": KernelCLI,
        "KernelHTTP": KernelHTTP,
    }

    # Extract metadata for each core kernel class
    for _type, instance in kernel_mapping.items():
        # Store module and class name for each kernel
        kernels[_type] = {
            "module": instance.__module__,
            "class": instance.__name__,
        }

    # Return an immutable mapping of the kernel metadata
    return MappingProxyType(kernels)

CORE_KERNELS: MappingProxyType = get_core_kernels_mapping()
