import os
import sys
from orionis.luminate.console.output.console import Console
from orionis.luminate.test.output.contracts.test_std_out import ITestStdOut

class TestStdOut(ITestStdOut):
    """
    TestStdOut is a class that provides methods for printing messages to the console
    and exiting the program. It is designed to be used in a testing environment where
    console output is important for debugging and reporting purposes.
    It includes methods for printing messages with contextual information about the
    file, line number, and method name of the caller. The class also provides a method
    for forcefully exiting the program with a specified exit code.
    """

    def console(self):
        """
        Returns an instance of the Console class for printing messages to the console.
        Ensures that the original stdout and stderr streams are used during the operation.
        """
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        try:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            return Console
        finally:
            # Restore the original stdout and stderr streams
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def exit(self) -> None:
        """
        Force close the program with the specified exit code. This method is a wrapper
        around `os._exit(1)` to ensure that the program terminates immediately without
        """
        os._exit(1)

    def dd(self, *args) -> None:
        """
        Prints the provided arguments to the console with contextual information
        about the file and line number of the caller, and then exits the program.
        Parameters
        ----------
        *args : tuple
            The arguments to be printed. The first argument is ignored, and the
            remaining arguments are printed. If no arguments are provided, the
            method does nothing.
        Notes
        -----
        - The method temporarily redirects `sys.stdout` and `sys.stderr` to their
          original states (`sys.__stdout__` and `sys.__stderr__`) to ensure proper
          console output.
        - The contextual information includes the file path and line number of the
          caller, which is displayed in a muted text format.
        - After printing, the method restores the original `sys.stdout` and
          `sys.stderr` streams.
        """
        self.dump(*args)
        self.exit()

    def dump(*args):
        """
        Prints the provided arguments to the console with contextual information
        about the file and line number of the caller. The output is formatted with
        muted text decorations for better readability.
        Parameters
        ----------
        *args : tuple
            The arguments to be printed. The first argument is ignored, and the
            remaining arguments are printed. If no arguments are provided, the
            method does nothing.
        Notes
        -----
        - The method temporarily redirects `sys.stdout` and `sys.stderr` to their
          original states (`sys.__stdout__` and `sys.__stderr__`) to ensure proper
          console output.
        - The contextual information includes the file path and line number of the
          caller, which is displayed in a muted text format.
        - After printing, the method restores the original `sys.stdout` and
          `sys.stderr` streams.
        """

        # Check if the first argument is a string and remove it from the args tuple
        if len(args) == 0:
            return

        # Change the output stream to the original stdout and stderr
        # to avoid any issues with the console output
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # Get the file name and line number of the caller
        # using sys._getframe(1) to access the caller's frame
        _file = os.path.relpath(sys._getframe(1).f_code.co_filename, start=os.getcwd())
        _method = sys._getframe(1).f_code.co_name
        _line = sys._getframe(1).f_lineno

        # Print the contextual information and the provided arguments
        Console.textMuted(f"File: {_file}, Line: {_line}, Method: {_method}")
        print(*args, end='\n')
        Console.newLine()

        # Restore the original stdout and stderr streams
        sys.stdout = original_stdout
        sys.stderr = original_stderr