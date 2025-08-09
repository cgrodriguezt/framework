import asyncio
from orionis.console.base.command import BaseCommand

class CustomCommandComplete(BaseCommand):
    """
    Mock implementation of a console command for testing.

    This class extends `BaseCommand` and provides a set of example arguments
    of various data types, including string, integer, float, boolean, list, and dictionary.
    It is intended for use as a mock object in unit tests for the console framework.

    Attributes
    ----------
    args : dict
        Dictionary containing example arguments:
            - 'key_str' (str): Example string value.
            - 'key_int' (int): Example integer value.
            - 'key_float' (float): Example float value.
            - 'key_bool' (bool): Example boolean value.
            - 'key_list' (list): Example list of integers.
            - 'key_dict' (dict): Example nested dictionary.
    """

    args = {
        'key_str': 'example_value',
        'key_int': 42,
        'key_float': 3.14,
        'key_bool': True,
        'key_list': [1, 2, 3],
        'key_dict': {'nested_key': 'nested_value'}
    }

    async def handle(self) -> str:
        """
        Simulates asynchronous command execution for testing.

        Returns
        -------
        str
            A success message indicating the command finished successfully.
        """
        # Simulate some asynchronous operation
        await asyncio.sleep(0.1)

        # Return a success message
        return "Finished Successfully"

class CustomCommandWithoutHandle(BaseCommand):
    """
    Mock implementation of a console command without a handle method.

    This class extends `BaseCommand` and provides example arguments, but does not
    implement the `handle` method. It is intended for use as a mock object in unit
    tests to represent an incomplete command implementation.

    Attributes
    ----------
    args : dict
        Dictionary containing example arguments:
            - 'key_str' (str): Example string value.
            - 'key_int' (int): Example integer value.
            - 'key_float' (float): Example float value.
            - 'key_bool' (bool): Example boolean value.
            - 'key_list' (list): Example list of integers.
            - 'key_dict' (dict): Example nested dictionary.
    """

    args = {
        'key_str': 'example_value',
        'key_int': 42,
        'key_float': 3.14,
        'key_bool': True,
        'key_list': [1, 2, 3],
        'key_dict': {'nested_key': 'nested_value'}
    }

    # No handle method implemented, this class serves as an example of an incomplete command.