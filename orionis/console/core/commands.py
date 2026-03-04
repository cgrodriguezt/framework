from orionis.console.commands.support.optimize_clear import OptimizeClearCommand
from orionis.console.commands.support.list import HelpCommand
from orionis.console.commands.support.about import VersionCommand
from orionis.console.commands.make.make_command import MakeCommand
from orionis.console.commands.schedule.list_command import ScheduleListCommand
from orionis.console.commands.schedule.work_command import ScheduleWorkCommand
from orionis.console.commands.serve.serve_command import ServerCommand
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
        OptimizeClearCommand,
        HelpCommand,
        MakeCommand,
        ScheduleListCommand,
        ScheduleWorkCommand,
        TestCommand,
        VersionCommand,
        ServerCommand,
    )

CORE_COMMANDS: tuple = get_core_commands_mapping()
