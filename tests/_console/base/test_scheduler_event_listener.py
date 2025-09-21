from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.base.scheduler_event_listener import BaseScheduleEventListener
from unittest.mock import MagicMock

class TestBaseScheduleEventListener(AsyncTestCase):
	"""
	Unit tests for BaseScheduleEventListener methods.
	"""

	async def testBeforeDoesNothing(self):
		"""
		Test that the 'before' method completes without error.

		Ensures that calling 'before' with mock arguments does not raise exceptions.

		Returns
		-------
		None
		"""
		listener = BaseScheduleEventListener()
		event = MagicMock(name='EventJob')
		schedule = MagicMock(name='ISchedule')
		await listener.before(event, schedule)

	async def testAfterDoesNothing(self):
		"""
		Test that the 'after' method completes without error.

		Ensures that calling 'after' with mock arguments does not raise exceptions.

		Returns
		-------
		None
		"""
		listener = BaseScheduleEventListener()
		event = MagicMock(name='EventJob')
		schedule = MagicMock(name='ISchedule')
		await listener.after(event, schedule)

	async def testOnFailureDoesNothing(self):
		"""
		Test that the 'onFailure' method completes without error.

		Ensures that calling 'onFailure' with mock arguments does not raise exceptions.

		Returns
		-------
		None
		"""
		listener = BaseScheduleEventListener()
		event = MagicMock(name='EventJob')
		schedule = MagicMock(name='ISchedule')
		await listener.onFailure(event, schedule)

	async def testOnMissedDoesNothing(self):
		"""
		Test that the 'onMissed' method completes without error.

		Ensures that calling 'onMissed' with mock arguments does not raise exceptions.

		Returns
		-------
		None
		"""
		listener = BaseScheduleEventListener()
		event = MagicMock(name='EventJob')
		schedule = MagicMock(name='ISchedule')
		await listener.onMissed(event, schedule)

	async def testOnMaxInstancesDoesNothing(self):
		"""
		Test that the 'onMaxInstances' method completes without error.

		Ensures that calling 'onMaxInstances' with mock arguments does not raise exceptions.

		Returns
		-------
		None
		"""
		listener = BaseScheduleEventListener()
		event = MagicMock(name='EventJob')
		schedule = MagicMock(name='ISchedule')
		await listener.onMaxInstances(event, schedule)

	async def testOnPausedDoesNothing(self):
		"""
		Test that the 'onPaused' method completes without error.

		Ensures that calling 'onPaused' with mock arguments does not raise exceptions.

		Returns
		-------
		None
		"""
		listener = BaseScheduleEventListener()
		event = MagicMock(name='EventJob')
		schedule = MagicMock(name='ISchedule')
		await listener.onPaused(event, schedule)

	async def testOnResumedDoesNothing(self):
		"""
		Test that the 'onResumed' method completes without error.

		Ensures that calling 'onResumed' with mock arguments does not raise exceptions.

		Returns
		-------
		None
		"""
		listener = BaseScheduleEventListener()
		event = MagicMock(name='EventJob')
		schedule = MagicMock(name='ISchedule')
		await listener.onResumed(event, schedule)

	async def testOnRemovedDoesNothing(self):
		"""
		Test that the 'onRemoved' method completes without error.

		Ensures that calling 'onRemoved' with mock arguments does not raise exceptions.

		Returns
		-------
		None
		"""
		listener = BaseScheduleEventListener()
		event = MagicMock(name='EventJob')
		schedule = MagicMock(name='ISchedule')
		await listener.onRemoved(event, schedule)
