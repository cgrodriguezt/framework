from orionis.luminate.config.configuration import Configuration

class Orionis:

    def __init__(self, config:Configuration = None):
        self.__config = config if config else Configuration()