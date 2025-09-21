from orionis.console.contracts.schedule import ISchedule

class DummySchedule(ISchedule):

	def cancelScheduledPause(self, *a, **k):
		"""
		Cancels a previously scheduled pause operation.

		This method should be overridden to implement logic for cancelling a pause
		that was scheduled earlier. The flexible arguments allow for different
		implementations depending on the scheduling system.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def cancelScheduledResume(self, *a, **k):
		"""
		Cancels a previously scheduled resume operation.

		Intended to be overridden in subclasses to provide the logic for cancelling
		a scheduled resume action. All arguments are forwarded to the implementation.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def cancelScheduledShutdown(self, *a, **k):
		"""
		Cancels a previously scheduled system shutdown.

		Stops or revokes any pending shutdown operations that were scheduled earlier.
		Additional arguments can be provided as needed for specific implementations.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def command(self, *a, **k):
		"""
		Executes a command with the provided arguments.

		This method should be overridden to execute the desired command using the
		supplied positional and keyword arguments.

		Parameters
		----------
		*a : tuple
			Positional arguments for the command.
		**k : dict
			Keyword arguments for the command.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def events(self, *a, **k):
		"""
		Handles scheduled events.

		Should be overridden by subclasses to define actions that should occur when
		scheduled events are triggered.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def forceStop(self, *a, **k):
		"""
		Forcibly stops the current operation or process.

		Intended to be overridden by subclasses to implement custom logic for
		forcefully stopping an ongoing task or schedule.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def isRunning(self, *a, **k):
		"""
		Checks if the schedule is currently running.

		Returns
		-------
		bool
			Always returns False, indicating the schedule is not running.
		"""
		# Always returns False for this dummy implementation.
		return False

	def pauseEverythingAt(self, *a, **k):
		"""
		Pauses all scheduled activities at a specified time or under certain conditions.

		Should be overridden to implement logic for pausing all activities.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments for additional parameters.
		**k : dict
			Arbitrary keyword arguments for additional options.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def pauseTask(self, *a, **k):
		"""
		Pauses the currently running task.

		Intended to be overridden by subclasses to implement the logic required to
		pause a task. Arguments are forwarded as positional and keyword arguments.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def removeTask(self, *a, **k):
		"""
		Removes a scheduled task.

		Should be overridden to remove specified scheduled tasks.

		Parameters
		----------
		*a : tuple
			Positional arguments specifying the task(s) to remove.
		**k : dict
			Keyword arguments for additional options or filters.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def resumeEverythingAt(self, *a, **k):
		"""
		Resumes all paused or suspended operations at a specified time or under certain conditions.

		Should be overridden to implement logic for resuming all operations.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def resumeTask(self, *a, **k):
		"""
		Resumes a previously paused or stopped task.

		Should be overridden to implement logic for resuming a specific task.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def setListener(self, *a, **k):
		"""
		Sets a listener for the current object.

		Intended to be overridden to handle event listeners.

		Parameters
		----------
		*a : tuple
			Positional arguments for the listener.
		**k : dict
			Keyword arguments for the listener.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def shutdown(self, *a, **k):
		"""
		Shuts down the current process or service.

		Performs any necessary cleanup or resource release operations before shutting
		down. Accepts arbitrary positional and keyword arguments for flexibility.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def shutdownEverythingAt(self, *a, **k):
		"""
		Shuts down all relevant systems or processes at a specified time or under certain conditions.

		Should be overridden with logic to gracefully shut down all necessary components.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def start(self, *a, **k):
		"""
		Starts the scheduled task.

		Should be overridden by subclasses to implement the logic for starting the
		schedule. Additional positional and keyword arguments can be provided as needed.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass

	def stop(self, *a, **k):
		"""
		Stops the current process or operation.

		Can be overridden to implement custom stop logic. Additional positional and
		keyword arguments can be provided as needed.

		Parameters
		----------
		*a : tuple
			Variable length positional arguments.
		**k : dict
			Arbitrary keyword arguments.

		Returns
		-------
		None
			This method does not return any value.
		"""
		# No operation; to be implemented by subclass.
		pass
