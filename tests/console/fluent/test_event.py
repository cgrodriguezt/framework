from datetime import datetime, timedelta
from orionis.console.fluent.event import Event
from orionis.test.cases.asynchronous import AsyncTestCase

class TestEvent(AsyncTestCase):

	async def testValidInitialization(self):
		"""
		Test that Event initializes correctly with valid arguments.

		Returns
		-------
		None
			This test passes if the Event is initialized with the correct attributes.
		"""
		event = Event(signature="my:event", args=["foo", "bar"], purpose="Test event")
		self.assertEqual(event._Event__signature, "my:event")
		self.assertEqual(event._Event__args, ["foo", "bar"])
		self.assertEqual(event._Event__purpose, "Test event")

	async def testPurposeSetter(self):
		"""
		Test setting the purpose using the purpose() method.

		Returns
		-------
		None
			This test passes if the purpose is set correctly.
		"""
		event = Event("sig", [])
		event.purpose("Scheduled job")
		self.assertEqual(event._Event__purpose, "Scheduled job")

	async def testStartDateSetter(self):
		"""
		Test setting the start date using startDate().

		Returns
		-------
		None
			This test passes if the start date is set correctly.
		"""
		event = Event("sig", [])
		now = datetime.now()
		event.startDate(now)
		self.assertEqual(event._Event__start_date, now)

	async def testEndDateSetter(self):
		"""
		Test setting the end date using endDate().

		Returns
		-------
		None
			This test passes if the end date is set correctly.
		"""
		event = Event("sig", [])
		end = datetime.now() + timedelta(days=1)
		event.endDate(end)
		self.assertEqual(event._Event__end_date, end)

	async def testRandomDelaySetter(self):
		"""
		Test setting a random delay using randomDelay().

		Returns
		-------
		None
			This test passes if the random delay is within the expected range.
		"""
		event = Event("sig", [])
		event.randomDelay(10)
		self.assertTrue(1 <= event._Event__random_delay <= 10)

	async def testMaxInstancesSetter(self):
		"""
		Test setting the maximum number of instances using maxInstances().

		Returns
		-------
		None
			This test passes if the max_instances attribute is set correctly.
		"""
		event = Event("sig", [])
		event.maxInstances(3)
		self.assertEqual(event._Event__max_instances, 3)

	async def testOnceAt(self):
		"""
		Test scheduling the event to run once at a specific datetime.

		Returns
		-------
		None
			This test passes if the trigger and dates are set correctly.
		"""
		event = Event("sig", [])
		dt = datetime(2025, 8, 30, 12, 0, 0)
		result = event.onceAt(dt)
		self.assertTrue(result)
		self.assertEqual(event._Event__start_date, dt)
		self.assertEqual(event._Event__end_date, dt)
		self.assertIsNotNone(event._Event__trigger)

	async def testEverySecond(self):
		"""
		Test scheduling the event to run every N seconds.

		Returns
		-------
		None
			This test passes if the trigger is set as an IntervalTrigger.
		"""
		event = Event("sig", [])
		result = event.everySecond(2)
		self.assertTrue(result)
		self.assertIsNotNone(event._Event__trigger)

	async def testEveryFiveSeconds(self):
		"""
		Test scheduling the event to run every five seconds.

		Returns
		-------
		None
			This test passes if the trigger is set as an IntervalTrigger for 5 seconds.
		"""
		event = Event("sig", [])
		result = event.everyFiveSeconds()
		self.assertTrue(result)
		self.assertIsNotNone(event._Event__trigger)
