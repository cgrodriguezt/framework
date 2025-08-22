from orionis.foundation.application import Application, IApplication

def Orionis() -> IApplication:
    """
    Creates and returns the main Orionis application instance.

    This function initializes the core application object that implements the `IApplication` interface.
    It serves as the primary entry point for creating and accessing the main application instance,
    ensuring that the application is properly set up before use.

    Returns
    -------
    IApplication
        An instance of `Application` that implements the `IApplication` interface, representing
        the main Orionis application.
    """

    # Instantiate the main application object implementing IApplication
    return Application()
