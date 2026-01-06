from __future__ import annotations
from dataclasses import dataclass, field
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
from orionis.services.environment.env import Env

@dataclass(frozen=True, kw_only=True)
class BootstrapLogging(Logging):

    # ----------------------------------------------------------------------------------
    # default : str, optional
    # --- The default logging channel name.
    # --- Uses the LOG_CHANNEL env var or "stack" if not set.
    # ----------------------------------------------------------------------------------
    default: str = field(
        default_factory=lambda: Env.get("LOG_CHANNEL", "stack"),
    )

    # ----------------------------------------------------------------------------------
    # channels : Channels | dict, optional
    # --- Collection of available logging channels.
    # --- Accepts a Channels instance or a dict.
    # ----------------------------------------------------------------------------------
    channels: Channels | dict = field(
        default_factory=lambda: Channels(

            # --------------------------------------------------------------------------
            # stack
            # --- Logs to "storage/logs/stack.log" at INFO level.
            # --- Used as the main stack channel.
            # --------------------------------------------------------------------------
            stack = Stack(
                path = "storage/logs/stack.log",
                level = Level.INFO,
            ),

            # --------------------------------------------------------------------------
            # hourly
            # --- Logs to "storage/logs/hourly_{suffix}.log" at INFO level.
            # --- Keeps logs for 24 hours.
            # --------------------------------------------------------------------------
            hourly = Hourly(
                path = "storage/logs/hourly_{suffix}.log",
                level = Level.INFO,
                retention_hours = 24,
            ),

            # --------------------------------------------------------------------------
            # daily
            # --- Logs to "storage/logs/daily_{suffix}.log" at INFO level.
            # --- Keeps logs for 7 days, rotates at midnight.
            # --------------------------------------------------------------------------
            daily = Daily(
                path = "storage/logs/daily_{suffix}.log",
                level = Level.INFO,
                retention_days = 7,
                at = time(hour=0, minute=0, second=0, microsecond=0),
            ),

            # --------------------------------------------------------------------------
            # weekly
            # --- Logs to "storage/logs/weekly_{suffix}.log" at INFO level.
            # --- Keeps logs for 4 weeks.
            # --------------------------------------------------------------------------
            weekly = Weekly(
                path = "storage/logs/weekly_{suffix}.log",
                level = Level.INFO,
                retention_weeks = 4,
            ),

            # --------------------------------------------------------------------------
            # monthly
            # --- Logs to "storage/logs/monthly_{suffix}.log" at INFO level.
            # --- Keeps logs for 4 months.
            # --------------------------------------------------------------------------
            monthly = Monthly(
                path = "storage/logs/monthly_{suffix}.log",
                level = Level.INFO,
                retention_months = 4,
            ),

            # --------------------------------------------------------------------------
            # chunked
            # --- Logs to "storage/logs/chunked_{suffix}.log" at INFO level.
            # --- Max file size 10 MB, keeps up to 5 files.
            # --------------------------------------------------------------------------
            chunked = Chunked(
                path = "storage/logs/chunked_{suffix}.log",
                level = Level.INFO,
                mb_size = 10,
                files = 5,
            ),
        ),
    )
