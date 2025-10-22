from datetime import datetime, timedelta
from orionis.console.contracts.event import IEvent
from orionis.console.fluent.event import Event
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.synchronous import SyncTestCase

class TestConsoleFluentEvent(SyncTestCase):

	def testValidInitialization(self):
		"""
		Test that Event initializes correctly with valid arguments.

		Returns
		-------
		None
			This test passes if the Event is initialized with the correct attributes.
		"""
		event = Event(
      		signature="my:event",
        	args=["foo", "bar"],
         	purpose="Test event"
        )
		self.assertEqual(event._Event__signature, "my:event")
		self.assertEqual(event._Event__args, ["foo", "bar"])
		self.assertEqual(event._Event__purpose, "Test event")

	def testPurposeSetter(self):
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

	def testStartDateSetter(self):
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

	def testEndDateSetter(self):
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

	def testRandomDelaySetter(self):
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

	def testMaxInstancesSetter(self):
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

	def testOnceAt(self):
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

	def testEverySecond(self):
		"""
		Test scheduling the event to run every N seconds.

		Returns
		-------
		None
			This test passes if the trigger is set as an IntervalTrigger.
		"""
		event = Event("sig", [])
		result = event.everySeconds(2)
		self.assertTrue(result)
		self.assertIsNotNone(event._Event__trigger)

	def testEveryFiveSeconds(self):
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

	def testImplementation(self):
		"""
		Verifies that all methods declared in the `IEvent` interface are implemented
		by the `Event` concrete class.

		Uses reflection to retrieve method names from both the interface and its implementation,
		then checks that each interface method exists in the concrete class.

		Parameters
		----------
		None

		Returns
		-------
		None
			Returns None. Raises AssertionError if any interface method is missing from the concrete class.
		"""
		# Retrieve all method names from the IEvent interface using reflection
		rf_abstract = ReflectionAbstract(IEvent).getMethods()

		# Retrieve all method names from the Event implementation using reflection
		rf_concrete = ReflectionConcrete(Event).getMethods()

		# Assert that every interface method is present in the implementation
		for method in rf_abstract:
			self.assertIn(method, rf_concrete)  # Ensure method exists in concrete class

	def testPropierties(self):
		"""
		Verifies that all properties declared in the `IEvent` interface are implemented
		by the `Event` concrete class.

		Uses reflection to retrieve property names from both the interface and its implementation,
		then checks that each interface property exists in the concrete class.

		Parameters
		----------
		None

		Returns
		-------
		None
			Returns None. Raises AssertionError if any interface property is missing from the concrete class.
		"""
		# Retrieve all property names from the IEvent interface using reflection
		rf_abstract = ReflectionAbstract(IEvent).getProperties()

		# Retrieve all property names from the Event implementation using reflection
		rf_concrete = ReflectionConcrete(Event).getProperties()

		# Assert that every interface property is present in the implementation
		for prop in rf_abstract:
			self.assertIn(prop, rf_concrete)  # Ensure property exists in concrete class
