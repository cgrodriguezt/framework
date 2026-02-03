from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
from orionis.services.log.handlers.advanced_rotating_file_handler import (
    AdvancedRotatingFileHandler,
)
from orionis.services.log.handlers.chunked_suffix_resolver import ChunkedSuffixResolver
from orionis.services.log.handlers.daily_suffix_resolver import DailySuffixResolver
from orionis.services.log.handlers.hourly_suffix_resolver import HourlySuffixResolver
from orionis.services.log.handlers.monthly_suffix_resolver import MonthlySuffixResolver
from orionis.services.log.handlers.weekly_suffix_resolver import WeeklySuffixResolver

if TYPE_CHECKING:
    from logging import Handler

class RotatingHandlerFactory:

    # ruff: noqa: PLC0415, PLR0911

    @staticmethod
    def createHandler(
        channel_name: str,
        channel_config: dict,
        app_root: str,
    ) -> Handler | None:
        """
        Create and return a log handler based on the channel configuration.

        Parameters
        ----------
        channel_name : str
            Name of the channel (e.g., stack, hourly, daily).
        channel_config : dict
            Channel configuration dictionary.
        app_root : str
            Root path of the application.

        Returns
        -------
        Handler | None
            Configured log handler instance, or None if the type is unsupported.
        """
        # Resolve log file path and log level from configuration
        path_template = channel_config.get("path", "storage/logs/default.log")
        level = channel_config.get("level", 20)  # Default to INFO

        if channel_name == "stack":

            # Use a simple file handler without rotation for stack channel
            from logging import FileHandler

            full_path: Path = Path(app_root) / path_template
            full_path.parent.mkdir(parents=True, exist_ok=True)
            handler = FileHandler(str(full_path), encoding="utf-8", delay=True)
            handler.setLevel(level)
            return handler

        if channel_name == "hourly":

            # Use hourly rotation with retention policy
            resolver = HourlySuffixResolver()
            retention_hours = channel_config.get("retention_hours", 24)
            handler = AdvancedRotatingFileHandler(
                path_template=path_template,
                suffix_resolver=resolver,
                backup_count=retention_hours,
                app_root=app_root,
            )
            handler.setLevel(level)
            return handler

        if channel_name == "daily":

            # Use daily rotation with retention policy
            at_time = channel_config.get("at")
            resolver = DailySuffixResolver(at_time)
            retention_days = channel_config.get("retention_days", 7)
            handler = AdvancedRotatingFileHandler(
                path_template=path_template,
                suffix_resolver=resolver,
                backup_count=retention_days,
                app_root=app_root,
            )
            handler.setLevel(level)
            return handler

        if channel_name == "weekly":

            # Use weekly rotation with retention policy
            at_time = channel_config.get("at")
            resolver = WeeklySuffixResolver(at_time)
            retention_weeks = channel_config.get("retention_weeks", 4)
            handler = AdvancedRotatingFileHandler(
                path_template=path_template,
                suffix_resolver=resolver,
                backup_count=retention_weeks,
                app_root=app_root,
            )
            handler.setLevel(level)
            return handler

        if channel_name == "monthly":

            # Use monthly rotation with retention policy
            at_time = channel_config.get("at")
            resolver = MonthlySuffixResolver(at_time)
            retention_months = channel_config.get("retention_months", 4)
            handler = AdvancedRotatingFileHandler(
                path_template=path_template,
                suffix_resolver=resolver,
                backup_count=retention_months,
                app_root=app_root,
            )
            handler.setLevel(level)
            return handler

        if channel_name == "chunked":

            # Use chunked rotation based on file size
            resolver = ChunkedSuffixResolver()
            mb_size = channel_config.get("mb_size", 10)
            max_bytes = mb_size * 1024 * 1024
            files = channel_config.get("files", 5)
            handler = AdvancedRotatingFileHandler(
                path_template=path_template,
                suffix_resolver=resolver,
                max_bytes=max_bytes,
                backup_count=files,
                app_root=app_root,
                compress_rotated=True,
            )
            handler.setLevel(level)
            return handler

        # Return None if channel type is not supported
        return None
