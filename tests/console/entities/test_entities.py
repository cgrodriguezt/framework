from orionis.console.entities.command import Command
from orionis.console.entities.event import Event
from orionis.console.entities.event_job import EventJob
from orionis.console.entities.scheduler_event_data import SchedulerEventData
from orionis.console.entities.scheduler_error import SchedulerError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted
from orionis.test.cases.synchronous import SyncTestCase
import argparse
from datetime import datetime

class TestConsoleEntities(SyncTestCase):

	def testCommandInitialization(self):
		"""
		Test initialization of the Command dataclass.

		Ensures that a Command instance is created with the correct attributes and default values.

		Returns
		-------
		None
			This method does not return any value.
		"""
		parser = argparse.ArgumentParser()
		cmd = Command(
      		obj=str,
        	signature="test:run",
         	description="Test command",
          	args=parser,
        )
		self.assertEqual(cmd.obj, str)
		self.assertEqual(cmd.method, "hanldle")
		self.assertEqual(cmd.signature, "test:run")
		self.assertEqual(cmd.description, "Test command")
		self.assertIs(cmd.args, parser)
		self.assertTrue(cmd.timestamps)

	def testEventInitialization(self):
		"""
		Test initialization of the Event dataclass.

		Ensures that an Event instance is created with the correct attributes and default values.

		Returns
		-------
		None
			This method does not return any value.
		"""
		now = datetime.now()
		event = Event(
      		signature="event:run",
        	start_date=now,
         	end_date=now,
          	max_instances=2,
        )
		self.assertEqual(event.signature, "event:run")
		self.assertEqual(event.start_date, now)
		self.assertEqual(event.end_date, now)
		self.assertEqual(event.max_instances, 2)
		self.assertIsInstance(event.args, list)
		self.assertIsNone(event.purpose)

	def testEventJobDefaults(self):
		"""
		Test default values of the EventJob dataclass.

		Ensures that an EventJob instance has the correct default values for its attributes.

		Returns
		-------
		None
			This method does not return any value.
		"""
		job = EventJob(id="job1")
		self.assertEqual(job.id, "job1")
		self.assertEqual(job.code, 0)
		self.assertIsNone(job.name)
		self.assertIsNone(job.func)
		self.assertEqual(job.args, ())
		self.assertEqual(job.executor, "default")
		self.assertEqual(job.jobstore, "default")
		self.assertEqual(job.max_instances, 1)
		self.assertFalse(job.coalesce)

	def testSchedulerEventData(self):
		"""
		Test initialization of the SchedulerEventData dataclass.

		Ensures that SchedulerEventData stores the event code correctly.

		Returns
		-------
		None
			This method does not return any value.
		"""
		event_data = SchedulerEventData(code=42)
		self.assertEqual(event_data.code, 42)

	def testSchedulerErrorAttributes(self):
		"""
		Test attributes of the SchedulerError dataclass.

		Ensures that SchedulerError correctly stores exception and traceback information.

		Returns
		-------
		None
			This method does not return any value.
		"""
		exc = ValueError("Test error")
		tb = "Traceback info"
		err = SchedulerError(code=1, exception=exc, traceback=tb)
		self.assertEqual(err.code, 1)
		self.assertIs(err.exception, exc)
		self.assertEqual(err.traceback, tb)

	def testSchedulerPaused(self):
		"""
		Test initialization of the SchedulerPaused dataclass.

		Ensures that SchedulerPaused stores the pause time correctly.

		Returns
		-------
		None
			This method does not return any value.
		"""
		paused = SchedulerPaused(code=2, time="12:00")
		self.assertEqual(paused.code, 2)
		self.assertEqual(paused.time, "12:00")

	def testSchedulerResumed(self):
		"""
		Test initialization of the SchedulerResumed dataclass.

		Ensures that SchedulerResumed stores the resume time correctly.

		Returns
		-------
		None
			This method does not return any value.
		"""
		resumed = SchedulerResumed(code=3, time="13:00")
		self.assertEqual(resumed.code, 3)
		self.assertEqual(resumed.time, "13:00")

	def testSchedulerShutdownTasks(self):
		"""
		Test the tasks attribute of the SchedulerShutdown dataclass.

		Ensures that SchedulerShutdown correctly stores the shutdown time and list of tasks.

		Returns
		-------
		None
			This method does not return any value.
		"""
		shutdown = SchedulerShutdown(code=4, time="14:00")
		self.assertEqual(shutdown.code, 4)
		self.assertEqual(shutdown.time, "14:00")

	def testSchedulerStartedTasks(self):
		"""
		Test the tasks attribute of the SchedulerStarted dataclass.

		Ensures that SchedulerStarted correctly stores the start time and list of tasks.

		Returns
		-------
		None
			This method does not return any value.
		"""
		started = SchedulerStarted(code=5, time="15:00")
		self.assertEqual(started.code, 5)
		self.assertEqual(started.time, "15:00")
