from datetime import datetime
import pytest
from orionis.console.base.scheduler import BaseScheduler
from orionis.console.entities.job_error import JobError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.base.dummy.dummy_schedule import DummySchedule

class TestBaseScheduler(AsyncTestCase):

	async def testTasksRaisesNotImplementedError(self):
		"""
		Test that the tasks method raises NotImplementedError.

		Notes
		-----
		The tasks method must be implemented by subclasses. This test ensures
		that calling it directly on BaseScheduler raises the correct exception.
		"""
		scheduler = BaseScheduler()
		schedule = DummySchedule()
		with pytest.raises(NotImplementedError):
			await scheduler.tasks(schedule)

	async def testOnStartedDoesNotRaise(self):
		"""
		Test that onStarted does not raise any exception by default.

		Notes
		-----
		The default implementation should be a no-op and not raise.
		"""
		scheduler = BaseScheduler()
		event = SchedulerStarted(code="STARTED")
		schedule = DummySchedule()
		await scheduler.onStarted(event, schedule)

	async def testOnPausedDoesNotRaise(self):
		"""
		Test that onPaused does not raise any exception by default.

		Notes
		-----
		The default implementation should be a no-op and not raise.
		"""
		scheduler = BaseScheduler()
		event = SchedulerPaused(code="PAUSED", time=datetime.now())
		schedule = DummySchedule()
		await scheduler.onPaused(event, schedule)

	async def testOnResumedDoesNotRaise(self):
		"""
		Test that onResumed does not raise any exception by default.

		Notes
		-----
		The default implementation should be a no-op and not raise.
		"""
		scheduler = BaseScheduler()
		event = SchedulerResumed(code="RESUMED", time=datetime.now())
		schedule = DummySchedule()
		await scheduler.onResumed(event, schedule)

	async def testOnFinalizedDoesNotRaise(self):
		"""
		Test that onFinalized does not raise any exception by default.

		Notes
		-----
		The default implementation should be a no-op and not raise.
		"""
		scheduler = BaseScheduler()
		event = SchedulerShutdown(code="SHUTDOWN")
		schedule = DummySchedule()
		await scheduler.onFinalized(event, schedule)

	async def testOnErrorDoesNotRaise(self):
		"""
		Test that onError does not raise any exception by default.

		Notes
		-----
		The default implementation should be a no-op and not raise.
		"""
		scheduler = BaseScheduler()
		event = JobError(
			code="ERROR",
			job_id="job-1",
			scheduled_run_time=datetime.now(),
			exception=Exception("fail"),
			traceback="traceback info"
		)
		schedule = DummySchedule()
		await scheduler.onError(event, schedule)
