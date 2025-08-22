from dataclasses import dataclass
from datetime import time
from orionis.foundation.config.logging.entities.channels import Channels
from orionis.foundation.config.logging.entities.chunked import Chunked
from orionis.foundation.config.logging.entities.daily import Daily
from orionis.foundation.config.logging.entities.hourly import Hourly
from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.logging.entities.monthly import Monthly
from orionis.foundation.config.logging.entities.stack import Stack
from orionis.foundation.config.logging.entities.weekly import Weekly
from orionis.foundation.config.logging.enums.levels import Level

@dataclass
class BootstrapLogging(Logging):

    # -------------------------------------------------------------------------
    # default : str
    #    - The default logging channel to use.
    #    - Defaults to "stack".
    # -------------------------------------------------------------------------
    default: str = "stack"

    # -------------------------------------------------------------------------
    # channels : Channels | dict
    #    - A collection of available logging channels.
    #    - Defaults to an instance of Channels with default values if not set.
    # -------------------------------------------------------------------------
    channels = Channels(

        # ---------------------------------------------------------------------
        # stack : Stack
        #    - Configuration for the stack logging channel.
        #    - Defaults to logging to "storage/log/stack.log" at INFO level.
        # ---------------------------------------------------------------------
        stack = Stack(
            path = 'storage/log/stack.log',
            level = Level.INFO
        ),

        # ---------------------------------------------------------------------
        # hourly : Hourly
        #    - Configuration for the hourly logging channel.
        #    - Defaults to logging to "storage/log/hourly.log" at INFO level with a retention of 24 hours.
        # ---------------------------------------------------------------------
        hourly = Hourly(
            path = 'storage/log/hourly.log',
            level = Level.INFO,
            retention_hours = 24
        ),

        # ---------------------------------------------------------------------
        # daily : Daily
        #    - Configuration for the daily logging channel.
        #    - Defaults to logging to "storage/log/daily.log" at INFO level with a retention of 7 days.
        # ---------------------------------------------------------------------
        daily = Daily(
            path = 'storage/log/daily.log',
            level = Level.INFO,
            retention_days = 7,
            at = time(0, 0)
        ),

        # ---------------------------------------------------------------------
        # weekly : Weekly
        #    - Configuration for the weekly logging channel.
        #    - Defaults to logging to "storage/log/weekly.log" at INFO level with a retention of 4 weeks.
        # ---------------------------------------------------------------------
        weekly = Weekly(
            path = 'storage/log/weekly.log',
            level = Level.INFO,
            retention_weeks = 4
        ),

        # ---------------------------------------------------------------------
        # monthly : Monthly
        #    - Configuration for the monthly logging channel.
        #    - Defaults to logging to "storage/log/monthly.log" at INFO level with a retention of 4 months.
        # ---------------------------------------------------------------------
        monthly = Monthly(
            path = 'storage/log/monthly.log',
            level = Level.INFO,
            retention_months = 4
        ),

        # ---------------------------------------------------------------------
        # chunked : Chunked
        #    - Configuration for the chunked logging channel.
        #    - Defaults to logging to "storage/log/chunked.log" at INFO level
        #    - with a maximum file size of 10 MB and a maximum of 5 files.
        # ---------------------------------------------------------------------
        chunked = Chunked(
            path = 'storage/log/chunked.log',
            level = Level.INFO,
            mb_size = 10,
            files = 5
        )
    )