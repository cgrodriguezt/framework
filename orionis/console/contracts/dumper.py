from __future__ import annotations
from abc import ABC, abstractmethod

class IDumper(ABC):

    # ruff: noqa: PLR0913
    @abstractmethod
    def dd(
        self,
        *args: object,
        show_types: bool = False,
        show_index: bool = False,
        expand_all: bool = True,
        max_depth: int | None = None,
        module_path: str | None = None,
        line_number: int | None = None,
        redirect_output: int | bool = False,
        insert_line: bool = False,
    ) -> None:
        """
        Print variables to the console and terminate execution.

        Print the provided variables using the configured console instance and
        stop program execution. Options allow displaying types, indices, expanding
        nested structures, and limiting expansion depth. Module path and line number
        can be included in the output.

        Parameters
        ----------
        *args : object
            Variables to print to the console.

        show_types : bool, optional
            Display the type of each variable.

        show_index : bool, optional
            Display the index for each variable.

        expand_all : bool, optional
            Expand all nested structures.

        max_depth : int or None, optional
            Maximum depth for nested expansion.

        module_path : str or None, optional
            Path of the module where the method is called.

        line_number : int or None, optional
            Line number in the source code where the method is called.

        redirect_output : int or bool, optional
            Redirect the output.

        insert_line : bool, optional
            Insert a separating line before output.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    def dump(
        self,
        *args: object,
        show_types: bool = False,
        show_index: bool = False,
        expand_all: bool = True,
        max_depth: int | None = None,
        module_path: str | None = None,
        line_number: int | None = None,
        redirect_output: int | bool = False,
        insert_line: bool = False,
    ) -> None:
        """
        Output variables to the console for debugging.

        Print variables to the console using the configured console instance.
        Customize output with options for types, indices, expansion, depth,
        module path, and line number. Output can be redirected and a separating
        line can be inserted.

        Parameters
        ----------
        *args : object
            Variables to output to the console.

        show_types : bool, optional
            Display the type of each variable.

        show_index : bool, optional
            Display the index for each variable.

        expand_all : bool, optional
            Expand all nested structures.

        max_depth : int or None, optional
            Maximum depth for nested expansion.

        module_path : str or None, optional
            Path of the module where the method is called.

        line_number : int or None, optional
            Line number in the source code where the method is called.

        redirect_output : int or bool, optional
            Redirect the output.

        insert_line : bool, optional
            Insert a separating line before output.

        Returns
        -------
        None
            This method does not return any value.
        """
