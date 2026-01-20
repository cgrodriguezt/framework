class DeferrableProvider:
    """Mark service providers that support deferred loading.

    This is a marker interface used to identify service providers that can
    defer their initialization until actually needed by the container.
    """

    def provides(self) -> list[type]:
        """Return the services provided by this provider.

        Returns
        -------
        list[type]
            A list of service types that this provider offers.

        Raises
        ------
        NotImplementedError
            When subclasses do not implement this method.
        """
        error_msg = "Subclasses must implement the provides method."
        raise NotImplementedError(error_msg)