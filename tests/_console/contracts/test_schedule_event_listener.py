
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_schedule_event_listener import DummyEventJob, DummySchedule, DummyScheduleEventListener

class TestIScheduleEventListener(AsyncTestCase):

	async def testBeforeIsCalled(self):
		"""
		Test that the 'before' method is called with correct arguments.

		Returns
		-------
		None
		"""
		listener = DummyScheduleEventListener()
		event = DummyEventJob()
		schedule = DummySchedule()
		await listener.before(event, schedule)
		self.assertTrue(hasattr(listener, 'before_called') and listener.before_called)
		self.assertIs(listener.before_event, event)
		self.assertIs(listener.before_schedule, schedule)

	async def testAfterIsCalled(self):
		"""
		Test that the 'after' method is called with correct arguments.

		Returns
		-------
		None
		"""
		listener = DummyScheduleEventListener()
		event = DummyEventJob()
		schedule = DummySchedule()
		await listener.after(event, schedule)
		self.assertTrue(hasattr(listener, 'after_called') and listener.after_called)
		self.assertIs(listener.after_event, event)
		self.assertIs(listener.after_schedule, schedule)

	async def testOnFailureIsCalled(self):
		"""
		Test that the 'onFailure' method is called with correct arguments.

		Returns
		-------
		None
		"""
		listener = DummyScheduleEventListener()
		event = DummyEventJob()
		schedule = DummySchedule()
		await listener.onFailure(event, schedule)
		self.assertTrue(hasattr(listener, 'failure_called') and listener.failure_called)
		self.assertIs(listener.failure_event, event)
		self.assertIs(listener.failure_schedule, schedule)

	async def testOnMissedIsCalled(self):
		"""
		Test that the 'onMissed' method is called with correct arguments.

		Returns
		-------
		None
		"""
		listener = DummyScheduleEventListener()
		event = DummyEventJob()
		schedule = DummySchedule()
		await listener.onMissed(event, schedule)
		self.assertTrue(hasattr(listener, 'missed_called') and listener.missed_called)
		self.assertIs(listener.missed_event, event)
		self.assertIs(listener.missed_schedule, schedule)

	async def testOnMaxInstancesIsCalled(self):
		"""
		Test that the 'onMaxInstances' method is called with correct arguments.

		Returns
		-------
		None
		"""
		listener = DummyScheduleEventListener()
		event = DummyEventJob()
		schedule = DummySchedule()
		await listener.onMaxInstances(event, schedule)
		self.assertTrue(hasattr(listener, 'max_instances_called') and listener.max_instances_called)
		self.assertIs(listener.max_instances_event, event)
		self.assertIs(listener.max_instances_schedule, schedule)

	async def testOnPausedIsCalled(self):
		"""
		Test that the 'onPaused' method is called with correct arguments.

		Returns
		-------
		None
		"""
		listener = DummyScheduleEventListener()
		event = DummyEventJob()
		schedule = DummySchedule()
		await listener.onPaused(event, schedule)
		self.assertTrue(hasattr(listener, 'paused_called') and listener.paused_called)
		self.assertIs(listener.paused_event, event)
		self.assertIs(listener.paused_schedule, schedule)

	async def testOnResumedIsCalled(self):
		"""
		Test that the 'onResumed' method is called with correct arguments.

		Returns
		-------
		None
		"""
		listener = DummyScheduleEventListener()
		event = DummyEventJob()
		schedule = DummySchedule()
		await listener.onResumed(event, schedule)
		self.assertTrue(hasattr(listener, 'resumed_called') and listener.resumed_called)
		self.assertIs(listener.resumed_event, event)
		self.assertIs(listener.resumed_schedule, schedule)

	async def testOnRemovedIsCalled(self):
		"""
		Test that the 'onRemoved' method is called with correct arguments.

		Returns
		-------
		None
		"""
		listener = DummyScheduleEventListener()
		event = DummyEventJob()
		schedule = DummySchedule()
		await listener.onRemoved(event, schedule)
		self.assertTrue(hasattr(listener, 'removed_called') and listener.removed_called)
		self.assertIs(listener.removed_event, event)
		self.assertIs(listener.removed_schedule, schedule)
