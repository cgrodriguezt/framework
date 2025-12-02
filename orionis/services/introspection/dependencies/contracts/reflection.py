from abc import ABC, abstractmethod
from orionis.services.introspection.dependencies.entities.signature import SignatureArguments

class IReflectDependencies(ABC):
    """
    Abstract interface for reflecting on class and method dependencies.

    This interface defines methods for retrieving dependency information from
    the constructor and methods of a class, distinguishing between resolved and
    unresolved dependencies.
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

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
        pass