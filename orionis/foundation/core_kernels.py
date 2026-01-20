from types import MappingProxyType
from orionis.console.kernel import KernelCLI
from orionis.http.kernel import KernelHTTP
from orionis.test.kernel import TestKernel

def get_core_kernels_mapping() -> MappingProxyType:
    """
    Return an immutable mapping of core kernel class metadata.

    This function initializes a dictionary containing metadata for each core
    kernel class. The dictionary is wrapped in a MappingProxyType to ensure
    immutability.

    Returns
    -------
    MappingProxyType
        An immutable mapping containing dictionaries with 'module' and
        'class' keys for each core kernel.
    """
    # Initialize empty dictionary to store kernel metadata
    kernels = {}

    # Define core kernel classes mapping
    kernel_mapping = {
        "KernelCLI": KernelCLI,
        "KernelHTTP": KernelHTTP,
        "TestKernel": TestKernel,
    }

    # Extract metadata for each core kernel class
    for _type, instance in kernel_mapping.items():
        kernels[_type] = {
            "module": instance.__module__,
            "class": instance.__name__,
        }

    # Return an immutable mapping of the kernel metadata
    return MappingProxyType(kernels)

CORE_KERNELS: MappingProxyType = get_core_kernels_mapping()
