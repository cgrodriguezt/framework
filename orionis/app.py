from orionis.foundation.config.startup import Configuration
from orionis.foundation.skeletom.startup import SkeletomConfiguration

class Orionis:

    def __init__(
        self,
        skeletom: SkeletomConfiguration = None,
        config: Configuration = None
    ):
        """
        Initializes the Orionis instance with optional configuration objects.

        Args:
            skeletom (SkeletomConfiguration, optional): Custom Skeletom configuration.
            config (Configuration, optional): Custom application configuration.
        """
        self.__skeletom = skeletom or SkeletomConfiguration()
        self.__config = config or Configuration()