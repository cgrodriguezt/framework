from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from orionis.support.entities.base import BaseEntity

if TYPE_CHECKING:
    from orionis.console.args.argument import CLIArgument

@dataclass(kw_only=True)
class Command(BaseEntity):
    """
    Represent a console command and its metadata.

    Parameters
    ----------
    obj : type
        Type or class associated with the command.
    method : str, optional
        Method name to invoke on the object. Defaults to 'hanldle'.
    timestamps : bool, optional
        Enable timestamps for this command. Defaults to True.
    signature : str
        Command usage signature.
    description : str
        Brief description of the command.
    args : argparse.ArgumentParser or None, optional
        Argument parser for command-line arguments. Defaults to None.

    Returns
    -------
    Command
        Instance containing metadata and configuration for a console command.
    """

    # The type or class associated with the command
    obj: type

    # The method name to be invoked on the object (default: 'hanldle')
    method: str = "hanldle"

    # Indicates if timestamps are enabled for this command (default: True)
    timestamps: bool = True

    # The command usage signature
    signature: str

    # Description of the command's purpose
    description: str

    # Optional argument parser for command-line arguments (default: None)
    args: list[CLIArgument] | None = None
