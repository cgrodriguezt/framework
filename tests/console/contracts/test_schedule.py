
from datetime import datetime
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_schedule import DummyScheduleTwo

class TestISchedule(AsyncTestCase):

	async def testCommandCreatesEvent(self):
		"""
		Test that the command method returns an event object with correct signature and args.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		event = schedule.command('test:run', ['foo'])
		self.assertEqual(event.signature, 'test:run')
		self.assertEqual(event.args, ['foo'])

	async def testSetListenerRegistersListener(self):
		"""
		Test that setListener correctly registers a listener for an event.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		listener = lambda e: e
		schedule.setListener('event', listener)
		self.assertEqual(schedule.listener_set, ('event', listener))

	async def testPauseEverythingAtSetsPauseTime(self):
		"""
		Test that pauseEverythingAt sets the correct pause time.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		now = datetime.now()
		schedule.pauseEverythingAt(now)
		self.assertEqual(schedule.paused_at, now)

	async def testResumeEverythingAtSetsResumeTime(self):
		"""
		Test that resumeEverythingAt sets the correct resume time.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		now = datetime.now()
		schedule.resumeEverythingAt(now)
		self.assertEqual(schedule.resumed_at, now)

	async def testShutdownEverythingAtSetsShutdownTime(self):
		"""
		Test that shutdownEverythingAt sets the correct shutdown time.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		now = datetime.now()
		schedule.shutdownEverythingAt(now)
		self.assertEqual(schedule.shutdown_at, now)

	async def testStartSetsStartedFlag(self):
		"""
		Test that start sets the started flag to True.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		await schedule.start()
		self.assertTrue(getattr(schedule, 'started', False))

	async def testShutdownSetsShutdownCalled(self):
		"""
		Test that shutdown sets the shutdown_called flag with the correct value.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		await schedule.shutdown(wait=False)
		self.assertEqual(schedule.shutdown_called, False)

	async def testPauseTaskReturnsTrue(self):
		"""
		Test that pauseTask returns True and sets the paused_task attribute.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		result = schedule.pauseTask('job1')
		self.assertTrue(result)
		self.assertEqual(schedule.paused_task, 'job1')

	async def testResumeTaskReturnsTrue(self):
		"""
		Test that resumeTask returns True and sets the resumed_task attribute.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		result = schedule.resumeTask('job2')
		self.assertTrue(result)
		self.assertEqual(schedule.resumed_task, 'job2')

	async def testRemoveTaskReturnsTrue(self):
		"""
		Test that removeTask returns True and sets the removed_task attribute.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		result = schedule.removeTask('job3')
		self.assertTrue(result)
		self.assertEqual(schedule.removed_task, 'job3')

	async def testEventsReturnsList(self):
		"""
		Test that events returns a list of scheduled jobs.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		events = schedule.events()
		self.assertIsInstance(events, list)
		self.assertEqual(events[0]['signature'], 'foo')

	async def testCancelScheduledPauseReturnsTrue(self):
		"""
		Test that cancelScheduledPause returns True and sets the cancel_pause flag.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		result = schedule.cancelScheduledPause()
		self.assertTrue(result)
		self.assertTrue(getattr(schedule, 'cancel_pause', False))

	async def testCancelScheduledResumeReturnsTrue(self):
		"""
		Test that cancelScheduledResume returns True and sets the cancel_resume flag.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		result = schedule.cancelScheduledResume()
		self.assertTrue(result)
		self.assertTrue(getattr(schedule, 'cancel_resume', False))

	async def testCancelScheduledShutdownReturnsTrue(self):
		"""
		Test that cancelScheduledShutdown returns True and sets the cancel_shutdown flag.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		result = schedule.cancelScheduledShutdown()
		self.assertTrue(result)
		self.assertTrue(getattr(schedule, 'cancel_shutdown', False))

	async def testIsRunningReturnsTrue(self):
		"""
		Test that isRunning returns True when scheduler is running.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		self.assertTrue(schedule.isRunning())

	async def testForceStopSetsForcedStop(self):
		"""
		Test that forceStop sets the forced_stop flag.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		schedule.forceStop()
		self.assertTrue(getattr(schedule, 'forced_stop', False))

	async def testStopSetsStopped(self):
		"""
		Test that stop sets the stopped flag.

		Returns
		-------
		None
		"""
		schedule = DummyScheduleTwo()
		schedule.stop()
		self.assertTrue(getattr(schedule, 'stopped', False))
