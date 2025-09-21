from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.entities.scheduler_error import SchedulerError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted
from tests.console.contracts.dummy.dummy_schedule import DummySchedule, DummyScheduler

class TestIBaseScheduler(AsyncTestCase):

    async def testTasksRegistersTasks(self):
        """
        Test that the `tasks` method registers tasks as expected.

        Returns
        -------
        None
        """
        scheduler = DummyScheduler()
        schedule = DummySchedule()
        await scheduler.tasks(schedule)
        assert hasattr(scheduler, 'tasks_called') and scheduler.tasks_called

    async def testOnStartedHandlesEvent(self):
        """
        Test that `onStarted` handles the SchedulerStarted event correctly.

        Returns
        -------
        None
        """
        scheduler = DummyScheduler()
        event = SchedulerStarted(code=1, time="2025-08-29T00:00:00", tasks=[])
        schedule = DummySchedule()
        await scheduler.onStarted(event, schedule)
        assert scheduler.started_called == (event, schedule)

    async def testOnPausedHandlesEvent(self):
        """
        Test that `onPaused` handles the SchedulerPaused event correctly.

        Returns
        -------
        None
        """
        scheduler = DummyScheduler()
        event = SchedulerPaused(code=2, time="2025-08-29T01:00:00")
        schedule = DummySchedule()
        await scheduler.onPaused(event, schedule)
        assert scheduler.paused_called == (event, schedule)

    async def testOnResumedHandlesEvent(self):
        """
        Test that `onResumed` handles the SchedulerResumed event correctly.

        Returns
        -------
        None
        """
        scheduler = DummyScheduler()
        event = SchedulerResumed(code=3, time="2025-08-29T02:00:00")
        schedule = DummySchedule()
        await scheduler.onResumed(event, schedule)
        assert scheduler.resumed_called == (event, schedule)

    async def testOnFinalizedHandlesEvent(self):
        """
        Test that `onFinalized` handles the SchedulerShutdown event correctly.

        Returns
        -------
        None
        """
        scheduler = DummyScheduler()
        event = SchedulerShutdown(code=4, time="2025-08-29T03:00:00", tasks=[])
        schedule = DummySchedule()
        await scheduler.onFinalized(event, schedule)
        assert scheduler.finalized_called == (event, schedule)

    async def testOnErrorHandlesJobError(self):
        """
        Test that `onError` handles the SchedulerError event correctly.

        Returns
        -------
        None
        """
        scheduler = DummyScheduler()
        event = SchedulerError(code=5, exception=Exception("An error occurred"), traceback="Traceback (most recent call last): ...")
        schedule = DummySchedule()
        await scheduler.onError(event, schedule)
        assert scheduler.error_called == (event, schedule)
