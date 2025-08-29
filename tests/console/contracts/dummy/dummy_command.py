from orionis.console.contracts.base_command import IBaseCommand

class DummyCommand(IBaseCommand):
	"""
	Dummy implementation of IBaseCommand for testing purposes.
	"""
	signature = "dummy"
	description = "A dummy command for testing."
	arguments = []

	def __init__(self):
		self.executed = False
		self._args = {"foo": "bar"}

	def handle(self) -> None:
		self.executed = True