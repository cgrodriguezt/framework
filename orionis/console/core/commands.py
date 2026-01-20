from types import MappingProxyType
from orionis.console.commands.cache.clear_command import CacheClearCommand
from orionis.console.commands.experimental.__publisher__ import PublisherCommand
from orionis.console.commands.experimental.server import ServerCommand
from orionis.console.commands.help.help_command import HelpCommand
from orionis.console.commands.help.version_command import VersionCommand
from orionis.console.commands.make.command import MakeCommand
from orionis.console.commands.make.scheduler_event_listener_command import (
    MakeSchedulerListenerCommand,
)
from orionis.console.commands.schedule.list_command import ScheduleListCommand
from orionis.console.commands.schedule.work_command import ScheduleWorkCommand
from orionis.console.commands.test.test_command import TestCommand

def get_core_commands_mapping() -> tuple:
    """
    Return a read-only mapping of core command classes.

    Returns
    -------
    tuple
        An immutable tuple of core command classes.
    """
    # Create an immutable mapping of core command classes for the framework.
    return (
        PublisherCommand,
        CacheClearCommand,
        HelpCommand,
        MakeCommand,
        ScheduleListCommand,
        ScheduleWorkCommand,
        TestCommand,
        VersionCommand,
        MakeSchedulerListenerCommand,
        ServerCommand,
    )

CORE_COMMANDS: tuple = get_core_commands_mapping()
