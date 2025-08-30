from orionis.test.cases.asynchronous import AsyncTestCase
from datetime import datetime, timedelta
from unittest.mock import Mock

from tests.console.contracts.dummy.dummy_event import DummyEvent

class TestIEvent(AsyncTestCase):
    async def testMisfireGraceTime(self):
        """
        Test that misfireGraceTime sets the grace period correctly.

        Returns
        -------
        None
        """
        event = DummyEvent()
        result = event.misfireGraceTime(120)
        self.assertEqual(event._misfire_grace_time, 120)
        self.assertIs(result, event)

    async def testPurpose(self):
        """
        Test that purpose sets the event's purpose string.

        Returns
        -------
        None
        """
        event = DummyEvent()
        result = event.purpose("Backup job")
        self.assertEqual(event._purpose, "Backup job")
        self.assertIs(result, event)

    async def testStartDateAndEndDate(self):
        """
        Test that startDate and endDate set the correct datetime values.

        Returns
        -------
        None
        """
        event = DummyEvent()
        start = datetime.now()
        end = start + timedelta(days=1)
        event.startDate(start)
        event.endDate(end)
        self.assertEqual(event._start_date, start)
        self.assertEqual(event._end_date, end)

    async def testRandomDelay(self):
        """
        Test that randomDelay sets the maximum random delay.

        Returns
        -------
        None
        """
        event = DummyEvent()
        result = event.randomDelay(15)
        self.assertEqual(event._random_delay, 15)
        self.assertIs(result, event)

    async def testMaxInstances(self):
        """
        Test that maxInstances sets the maximum number of concurrent instances.

        Returns
        -------
        None
        """
        event = DummyEvent()
        result = event.maxInstances(3)
        self.assertEqual(event._max_instances, 3)
        self.assertIs(result, event)

    async def testSubscribeListener(self):
        """
        Test that subscribeListener attaches a listener to the event.

        Returns
        -------
        None
        """
        event = DummyEvent()
        listener = Mock()
        result = event.subscribeListener(listener)
        self.assertIs(event._listener, listener)
        self.assertIs(result, event)

    async def testOnceAt(self):
        """
        Test that onceAt schedules the event for a single execution.

        Returns
        -------
        None
        """
        event = DummyEvent()
        date = datetime.now()
        result = event.onceAt(date)
        self.assertTrue(result)
        self.assertEqual(event._once_at, date)

    async def testEverySecond(self):
        """
        Test that everySecond schedules the event at a fixed interval in seconds.

        Returns
        -------
        None
        """
        event = DummyEvent()
        result = event.everySecond(5)
        self.assertTrue(result)
        self.assertEqual(event._every_second, 5)

    async def testEveryFiveSeconds(self):
        """
        Test that everyFiveSeconds schedules the event every five seconds.

        Returns
        -------
        None
        """
        event = DummyEvent()
        result = event.everyFiveSeconds()
        self.assertTrue(result)
        self.assertTrue(event._every_five_seconds)
