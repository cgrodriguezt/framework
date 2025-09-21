from orionis.console.contracts.base_command import IBaseCommand
from orionis.console.contracts.command import ICommand

class DummyCommand(IBaseCommand):
	"""
	Dummy implementation of the IBaseCommand interface for testing purposes.

	This class provides a minimal implementation of a command, primarily used for
	testing command execution and interface compliance within the framework.

	Attributes
	----------
	signature : str
		The unique identifier for the command.
	description : str
		A brief description of the command.
	arguments : list
		The list of arguments accepted by the command.
	executed : bool
		Indicates whether the command has been executed.
	_args : dict
		Stores default arguments for the command.
	"""

	signature = "dummy"
	description = "A dummy command for testing."
	arguments = []

	def __init__(self):
		"""
		Initialize a DummyCommand instance.

		Sets the 'executed' flag to False and initializes the '_args' dictionary
		with a default key-value pair.

		Returns
		-------
		None
			This constructor does not return any value.
		"""
		self.executed = False  # Flag to indicate if the command has been executed
		self._args = {"foo": "bar"}  # Default arguments for the command

	def handle(self) -> None:
		"""
		Execute the command's logic.

		Sets the 'executed' attribute to True to indicate that the command has been run.

		Returns
		-------
		None
			This method does not return any value.
		"""
		self.executed = True  # Mark the command as executed

class DummyCommandTwo(ICommand):
	"""
	Implements the ICommand interface, providing methods to configure command properties.

	This class allows enabling/disabling timestamping, setting a description, and specifying
	arguments for a command. It is intended for testing and demonstration purposes.

	Attributes
	----------
	_timestamp_enabled : bool
		Indicates whether timestamping is enabled for the command.
	_description : str
		The description of the command.
	_arguments : list
		The list of arguments for the command.
	"""

	def __init__(self):
		"""
		Initialize DummyCommandTwo with default values.

		Sets timestamping to enabled, description to an empty string, and arguments to an empty list.

		Returns
		-------
		None
		"""
		self._timestamp_enabled = True  # Timestamping enabled by default
		self._description = ""          # Default description is empty
		self._arguments = []            # No arguments by default

	def timestamp(self, enabled: bool = True) -> 'ICommand':
		"""
		Enable or disable timestamping for the command.

		Parameters
		----------
		enabled : bool, optional
			If True, enables timestamping; if False, disables it. Default is True.

		Returns
		-------
		ICommand
			The current command instance, allowing method chaining.

		Raises
		------
		TypeError
			If `enabled` is not a boolean.

		Notes
		-----
		This method modifies the internal `_timestamp_enabled` attribute.
		"""
		if not isinstance(enabled, bool):
			raise TypeError("enabled must be a boolean")
		self._timestamp_enabled = enabled  # Set timestamping flag
		return self

	def description(self, desc: str) -> 'ICommand':
		"""
		Set the description for the command.

		Parameters
		----------
		desc : str
			The description text to set for the command.

		Returns
		-------
		ICommand
			The command instance with the updated description, for method chaining.

		Raises
		------
		TypeError
			If `desc` is not a string.

		Notes
		-----
		This method updates the internal `_description` attribute.
		"""
		if not isinstance(desc, str):
			raise TypeError("desc must be a string")
		self._description = desc  # Update description
		return self

	def arguments(self, args: list) -> 'ICommand':
		"""
		Set the list of command-line arguments for the command.

		Parameters
		----------
		args : list
			A list of arguments to be passed to the command.

		Returns
		-------
		ICommand
			The current instance with updated arguments, for method chaining.

		Raises
		------
		TypeError
			If `args` is not a list.

		Notes
		-----
		This method updates the internal `_arguments` attribute.
		"""
		if not isinstance(args, list):
			raise TypeError("args must be a list")
		self._arguments = args  # Set command arguments
		return self