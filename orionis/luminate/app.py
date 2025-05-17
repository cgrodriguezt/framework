from orionis.luminate.foundation.config.configuration import Configuration

class Orionis:

    def __init__(self, config:Configuration = None):
        """
        Initializes the instance with the provided configuration.

        Args:
            config (Configuration, optional): An optional Configuration object. If not provided, a default Configuration is created and used.
        """
        self.__config = config if config else Configuration()