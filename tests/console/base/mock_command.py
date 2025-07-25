import asyncio
from orionis.console.base.command import BaseCommand

class CustomCommandComplete(BaseCommand):
    """
    CustomCommand is a mock implementation of a console command for testing purposes.
    This class inherits from BaseCommand and provides a set of example arguments
    of various data types, including string, integer, float, boolean, list, and dictionary.
    It is intended to be used as a mock object in unit tests for the console framework.
    Attributes
    ----------
    args : dict
        A dictionary containing example arguments:
            - 'key_str' (str): An example string value.
            - 'key_int' (int): An example integer value.
            - 'key_float' (float): An example float value.
            - 'key_bool' (bool): An example boolean value.
            - 'key_list' (list): An example list of integers.
            - 'key_dict' (dict): An example nested dictionary.
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
        Mock implementation of the handle method for testing purposes.
        This method simulates command execution and can be extended in tests.
        """

        # Simulate some asynchronous operation
        await asyncio.sleep(0.1)

        # Return a success message
        return "Finished Successfully"

class CustomCommandWithoutHandle(BaseCommand):
    """
    CustomCommandWithoutHandle is a mock implementation of a console command
    that does not implement the handle method. It is intended to be used as a
    mock object in unit tests for the console framework.
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