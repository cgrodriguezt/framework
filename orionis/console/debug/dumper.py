from __future__ import annotations
from typing import Any, TYPE_CHECKING
from orionis.console.contracts.dumper import IDumper

if TYPE_CHECKING:
    from orionis.console.contracts.console import IConsole

class Dumper(IDumper):
    def __init__(self, console: IConsole) -> None:
        """
        Initialize Dumper with a console instance.

        Parameters
        ----------
        console : IConsole
            Console implementing the IConsole interface.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__console = console

    # ruff: noqa: PLR0913
    def dd(
        self,
        *args: tuple[Any],
        show_types: bool = False,
        show_index: bool = False,
        expand_all: bool = True,
        max_depth: int | None = None,
        module_path: str | None = None,
        line_number: int | None = None,
        redirect_output: bool = False,
        insert_line: bool = False,
    ) -> None:
        """
        Dump variables to the console and terminate execution.

        Parameters
        ----------
        *args : Any
            Variables to dump.
        show_types : bool, optional
            Whether to show variable types. Default is False.
        show_index : bool, optional
            Whether to show index for each variable. Default is False.
        expand_all : bool, optional
            Whether to expand all nested structures. Default is True.
        max_depth : int or None, optional
            Maximum depth for expansion. Default is None.
        module_path : str or None, optional
            Path of the calling module. Default is None.
        line_number : int or None, optional
            Line number of the call. Default is None.
        redirect_output : bool, optional
            Whether to redirect output. Default is False.
        insert_line : bool, optional
            Whether to insert a separating line before output. Default is False.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__console.dump(
            *args,
            show_types=show_types,
            show_index=show_index,
            expand_all=expand_all,
            max_depth=max_depth,
            module_path=module_path,
            line_number=line_number,
            force_exit=True,
            redirect_output=redirect_output,
            insert_line=insert_line,
        )

    # ruff: noqa: PLR0913
    def dump(
        self,
        *args: tuple[Any],
        show_types: bool = False,
        show_index: bool = False,
        expand_all: bool = True,
        max_depth: int | None = None,
        module_path: str | None = None,
        line_number: int | None = None,
        redirect_output: bool = False,
        insert_line: bool = False,
    ) -> None:
        """
        Dump variables to the console for debugging.

        Parameters
        ----------
        *args : Any
            Variables to dump.
        show_types : bool, optional
            Whether to show variable types. Default is False.
        show_index : bool, optional
            Whether to show index for each variable. Default is False.
        expand_all : bool, optional
            Whether to expand all nested structures. Default is True.
        max_depth : int or None, optional
            Maximum depth for expansion. Default is None.
        module_path : str or None, optional
            Path of the calling module. Default is None.
        line_number : int or None, optional
            Line number of the call. Default is None.
        redirect_output : bool, optional
            Whether to redirect output. Default is False.
        insert_line : bool, optional
            Whether to insert a separating line before output. Default is False.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__console.dump(
            *args,
            show_types=show_types,
            show_index=show_index,
            expand_all=expand_all,
            max_depth=max_depth,
            module_path=module_path,
            line_number=line_number,
            force_exit=False,
            redirect_output=redirect_output,
            insert_line=insert_line,
        )
