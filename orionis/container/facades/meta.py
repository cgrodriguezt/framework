from typing import Any

class FacadeMeta(type):

    # ruff: noqa: ANN401

    @classmethod
    def _getServiceInstance(cls) -> Any:
        """
        Raise NotImplementedError for missing _getServiceInstance implementation.

        This method must be implemented by subclasses to provide the service
        instance retrieval logic.

        Parameters
        ----------
        cls : type
            The class object.

        Returns
        -------
        Any
            This method does not return; it always raises NotImplementedError.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in the subclass.
        """
        error_msg = (
            f"Class {cls.__name__} must implement the _getServiceInstance method"
        )
        raise NotImplementedError(error_msg)

    def __getattr__(cls, name: str) -> Any:
        """
        Redirect attribute access to the underlying service.

        Parameters
        ----------
        name : str
            The attribute or method name to access on the service.

        Returns
        -------
        Any
            The attribute or method from the underlying service.

        Raises
        ------
        AttributeError
            If the underlying service does not have the requested attribute.
        """
        # Retrieve the cached service instance
        service = cls._getServiceInstance()
        if not hasattr(service, name):
            error_msg = (
                f"'{cls.__name__}' facade's service has no attribute '{name}'"
            )
            raise AttributeError(error_msg)
        return getattr(service, name)
