from abc import ABC, abstractmethod
from orionis.services.introspection.dependencies.entities.signature import (
    SignatureArguments,
)

class IReflectDependencies(ABC):

    @abstractmethod
    def constructorSignature(self) -> SignatureArguments:
        """
        Inspect the constructor (__init__) method and categorize parameter dependencies.

        Returns
        -------
        SignatureArguments
            Contains resolved and unresolved parameter dependencies.

        Raises
        ------
        ReflectionValueError
            If the constructor signature cannot be inspected.
        """

    @abstractmethod
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
        ReflectionValueError
            If the method does not exist or its signature cannot be inspected.
        """

    @abstractmethod
    def callableSignature(self) -> SignatureArguments:
        """
        Inspect the callable target and categorize its parameter dependencies.

        Returns
        -------
        SignatureArguments
            Contains resolved and unresolved parameter dependencies.

        Raises
        ------
        ReflectionValueError
            If the target is not callable or its signature cannot be inspected.
        """
