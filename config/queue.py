from dataclasses import dataclass
from orionis.foundation.config.queue.entities.database import Database
from orionis.foundation.config.queue.enums.strategy import Strategy
from orionis.foundation.config.queue.entities.brokers import Brokers
from orionis.foundation.config.queue.entities.queue import Queue
from orionis.services.environment.env import Env

@dataclass
class BootstrapQueue(Queue):

    # -------------------------------------------------------------------------
    # default : str
    #    - The default queue connection to use.
    #    - Defaults to "sync".
    # -------------------------------------------------------------------------
    default: str = Env.get('QUEUE_CONNECTION', 'sync')

    # -------------------------------------------------------------------------
    # brokers : Brokers | dict
    #    - A collection of available queue broker configurations.
    #    - Defaults to an instance of Brokers with default values if not set.
    # -------------------------------------------------------------------------
    brokers: Brokers | dict = Brokers(

        # ---------------------------------------------------------------------
        # sync : InLine
        #    - Configuration for the synchronous queue broker.
        # ---------------------------------------------------------------------
        sync = True,

        # ---------------------------------------------------------------------
        # database : Database
        #    - Configuration for the database queue broker.
        #    - Defaults to a database connection with specific settings.
        # ---------------------------------------------------------------------
        database = Database(
            table = "jobs",
            queue = "default",
            retry_after = 90,
            strategy = Strategy.FIFO
        )
    )