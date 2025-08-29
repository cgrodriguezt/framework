from orionis.console.contracts.schedule import ISchedule

# A dummy implementation of ISchedule for testing purposes
class DummySchedule(ISchedule):
	def cancelScheduledPause(self, *a, **k): pass
	def cancelScheduledResume(self, *a, **k): pass
	def cancelScheduledShutdown(self, *a, **k): pass
	def command(self, *a, **k): pass
	def events(self, *a, **k): pass
	def forceStop(self, *a, **k): pass
	def isRunning(self, *a, **k): return False
	def pauseEverythingAt(self, *a, **k): pass
	def pauseTask(self, *a, **k): pass
	def removeTask(self, *a, **k): pass
	def resumeEverythingAt(self, *a, **k): pass
	def resumeTask(self, *a, **k): pass
	def setListener(self, *a, **k): pass
	def shutdown(self, *a, **k): pass
	def shutdownEverythingAt(self, *a, **k): pass
	def start(self, *a, **k): pass
	def stop(self, *a, **k): pass
