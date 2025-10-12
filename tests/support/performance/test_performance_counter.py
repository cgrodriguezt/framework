import time
from unittest.mock import patch
from orionis.test.cases.synchronous import SyncTestCase
from orionis.support.performance.counter import PerformanceCounter

class TestPerformanceCounter(SyncTestCase):

    def setUp(self):
        """
        Initialize test environment before each test method.

        Creates a fresh PerformanceCounter instance for each test to ensure
        test isolation and prevent state pollution between test methods.

        Returns
        -------
        None
        """
        self.counter = PerformanceCounter()

    def testInitialization(self):
        """
        Test the initialization of PerformanceCounter instance.

        Verifies that a newly created PerformanceCounter instance has all
        internal attributes properly initialized to None, indicating that
        no timing operations have been performed yet.

        Returns
        -------
        None
        """
        # Verify that internal time attributes are initialized to None
        self.assertIsNone(self.counter._PerformanceCounter__start_time)
        self.assertIsNone(self.counter._PerformanceCounter__end_time)
        self.assertIsNone(self.counter._PerformanceCounter__diff_time)

    def testStartSetsStartTime(self):
        """
        Test that the start method correctly sets the start time.

        Verifies that calling start() records a timestamp using time.perf_counter()
        and stores it in the internal start time attribute. Also ensures that
        the method returns the counter instance for method chaining.

        Returns
        -------
        None
        """
        with patch('time.perf_counter', return_value=1234.5678) as mock_perf_counter:
            result = self.counter.start()

            # Verify perf_counter was called
            mock_perf_counter.assert_called_once()

            # Verify start time was set correctly
            self.assertEqual(self.counter._PerformanceCounter__start_time, 1234.5678)

            # Verify method returns self for chaining
            self.assertIs(result, self.counter)

    def testStopSetsEndTimeAndCalculatesDiff(self):
        """
        Test that the stop method correctly sets end time and calculates elapsed time.

        Verifies that calling stop() after start() records an end timestamp,
        calculates the elapsed time difference, and returns the counter instance
        for method chaining.

        Returns
        -------
        None
        """
        # Mock perf_counter to return specific values for start and stop
        with patch('time.perf_counter', side_effect=[1000.0, 1002.5]) as mock_perf_counter:
            self.counter.start()
            result = self.counter.stop()

            # Verify perf_counter was called twice
            self.assertEqual(mock_perf_counter.call_count, 2)

            # Verify end time was set correctly
            self.assertEqual(self.counter._PerformanceCounter__end_time, 1002.5)

            # Verify elapsed time was calculated correctly
            self.assertEqual(self.counter._PerformanceCounter__diff_time, 2.5)

            # Verify method returns self for chaining
            self.assertIs(result, self.counter)

    def testElapsedTimeReturnsCorrectValue(self):
        """
        Test that elapsedTime returns the correct elapsed time value.

        Verifies that after a complete start-stop cycle, elapsedTime()
        returns the calculated time difference in seconds as a float.

        Returns
        -------
        None
        """
        with patch('time.perf_counter', side_effect=[100.0, 103.5]):
            self.counter.start()
            self.counter.stop()

            elapsed = self.counter.elapsedTime()
            self.assertEqual(elapsed, 3.5)
            self.assertIsInstance(elapsed, float)

    def testElapsedTimeRaisesValueErrorWhenNotStartedAndStopped(self):
        """
        Test that elapsedTime raises ValueError when counter hasn't been properly used.

        Verifies that calling elapsedTime() without a complete start-stop cycle
        raises a ValueError with an appropriate error message.

        Returns
        -------
        None
        """
        # Test when no start/stop has been called
        with self.assertRaises(ValueError) as context:
            self.counter.elapsedTime()

        self.assertIn("Counter has not been started and stopped properly", str(context.exception))

        # Test when only start has been called
        self.counter.start()
        with self.assertRaises(ValueError) as context:
            self.counter.elapsedTime()

        self.assertIn("Counter has not been started and stopped properly", str(context.exception))

    def testGetMicroseconds(self):
        """
        Test the getMicroseconds method returns elapsed time in microseconds.

        Verifies that getMicroseconds() correctly converts the elapsed time
        from seconds to microseconds by multiplying by 1,000,000.

        Returns
        -------
        None
        """
        with patch('time.perf_counter', side_effect=[50.0, 50.001234]):
            self.counter.start()
            self.counter.stop()

            microseconds = self.counter.getMicroseconds()
            self.assertAlmostEqual(microseconds, 1234.0, places=1)
            self.assertIsInstance(microseconds, float)

    def testGetMilliseconds(self):
        """
        Test the getMilliseconds method returns elapsed time in milliseconds.

        Verifies that getMilliseconds() correctly converts the elapsed time
        from seconds to milliseconds by multiplying by 1,000.

        Returns
        -------
        None
        """
        with patch('time.perf_counter', side_effect=[25.0, 27.5]):
            self.counter.start()
            self.counter.stop()

            milliseconds = self.counter.getMilliseconds()
            self.assertEqual(milliseconds, 2500.0)
            self.assertIsInstance(milliseconds, float)

    def testGetSeconds(self):
        """
        Test the getSeconds method returns elapsed time in seconds.

        Verifies that getSeconds() returns the same value as elapsedTime(),
        since both represent time in seconds.

        Returns
        -------
        None
        """
        with patch('time.perf_counter', side_effect=[10.0, 15.75]):
            self.counter.start()
            self.counter.stop()

            seconds = self.counter.getSeconds()
            elapsed = self.counter.elapsedTime()

            self.assertEqual(seconds, 5.75)
            self.assertEqual(seconds, elapsed)
            self.assertIsInstance(seconds, float)

    def testGetMinutes(self):
        """
        Test the getMinutes method returns elapsed time in minutes.

        Verifies that getMinutes() correctly converts the elapsed time
        from seconds to minutes by dividing by 60.

        Returns
        -------
        None
        """
        with patch('time.perf_counter', side_effect=[0.0, 120.0]):
            self.counter.start()
            self.counter.stop()

            minutes = self.counter.getMinutes()
            self.assertEqual(minutes, 2.0)
            self.assertIsInstance(minutes, float)

        # Test with fractional minutes
        with patch('time.perf_counter', side_effect=[0.0, 90.0]):
            fresh_counter = PerformanceCounter()
            fresh_counter.start()
            fresh_counter.stop()

            minutes = fresh_counter.getMinutes()
            self.assertEqual(minutes, 1.5)

    def testRestart(self):
        """
        Test the restart method resets the counter and starts it again.

        Verifies that restart() clears all internal timing attributes,
        starts the counter again, and returns the PerformanceCounter instance.

        Returns
        -------
        None
        """
        # First, do a complete timing cycle
        with patch('time.perf_counter', side_effect=[100.0, 105.0]):
            self.counter.start()
            self.counter.stop()

            # Verify timing data exists
            self.assertIsNotNone(self.counter._PerformanceCounter__start_time)
            self.assertIsNotNone(self.counter._PerformanceCounter__end_time)
            self.assertIsNotNone(self.counter._PerformanceCounter__diff_time)

        # Now restart with a new mock value
        with patch('time.perf_counter', return_value=200.0) as mock_restart:
            result = self.counter.restart()

            # Verify all timing attributes were reset to None and then start_time was set
            self.assertEqual(self.counter._PerformanceCounter__start_time, 200.0)
            self.assertIsNone(self.counter._PerformanceCounter__end_time)
            self.assertIsNone(self.counter._PerformanceCounter__diff_time)

            # Verify method returns self for chaining
            self.assertIs(result, self.counter)

            # Verify perf_counter was called for restart
            mock_restart.assert_called_once()

    def testMethodChaining(self):
        """
        Test that all methods support method chaining by returning self.

        Verifies that start(), stop(), and restart() methods all return
        the PerformanceCounter instance, allowing for fluent method chaining.

        Returns
        -------
        None
        """
        with patch('time.perf_counter', side_effect=[1.0, 2.0, 3.0]):
            # Test chaining start -> stop
            result = self.counter.start().stop()
            self.assertIs(result, self.counter)

            # Test that we can call elapsedTime after chaining
            elapsed = result.elapsedTime()
            self.assertEqual(elapsed, 1.0)

            # Test restart chaining
            restart_result = self.counter.restart()
            self.assertIs(restart_result, self.counter)

    def testMultipleStartStopCycles(self):
        """
        Test multiple start-stop cycles with the same counter instance.

        Verifies that the counter can be reused multiple times and that
        each cycle produces independent timing measurements.

        Returns
        -------
        None
        """
        # First cycle
        with patch('time.perf_counter', side_effect=[10.0, 12.0]):
            self.counter.start()
            self.counter.stop()
            first_elapsed = self.counter.elapsedTime()
            self.assertEqual(first_elapsed, 2.0)

        # Second cycle
        with patch('time.perf_counter', side_effect=[20.0, 25.5]):
            self.counter.start()
            self.counter.stop()
            second_elapsed = self.counter.elapsedTime()
            self.assertEqual(second_elapsed, 5.5)

        # Verify the second cycle overwrote the first
        self.assertNotEqual(first_elapsed, second_elapsed)

    def testRealTimingAccuracy(self):
        """
        Test actual timing functionality without mocks for accuracy verification.

        Performs a real timing test using time.sleep() to verify that the
        counter accurately measures elapsed time within acceptable tolerance.
        This test validates the integration with time.perf_counter().

        Returns
        -------
        None
        """
        sleep_duration = 0.1  # 100 milliseconds
        tolerance = 0.05  # 50 milliseconds tolerance

        self.counter.start()
        time.sleep(sleep_duration)
        self.counter.stop()

        elapsed = self.counter.elapsedTime()

        # Verify elapsed time is within expected range
        self.assertGreaterEqual(elapsed, sleep_duration)
        self.assertLessEqual(elapsed, sleep_duration + tolerance)

        # Test all time unit conversions with real data
        microseconds = self.counter.getMicroseconds()
        milliseconds = self.counter.getMilliseconds()
        seconds = self.counter.getSeconds()
        minutes = self.counter.getMinutes()

        # Verify conversions are mathematically correct
        self.assertAlmostEqual(microseconds, elapsed * 1_000_000, places=2)
        self.assertAlmostEqual(milliseconds, elapsed * 1_000, places=2)
        self.assertAlmostEqual(seconds, elapsed, places=6)
        self.assertAlmostEqual(minutes, elapsed / 60, places=6)

    def testTimeUnitConversionsWithoutStartStop(self):
        """
        Test that time unit conversion methods raise ValueError when not properly initialized.

        Verifies that all time unit conversion methods (getMicroseconds, getMilliseconds,
        getSeconds, getMinutes) raise ValueError when called before a complete
        start-stop cycle.

        Returns
        -------
        None
        """
        # Test all conversion methods raise ValueError when not started/stopped
        with self.assertRaises(ValueError):
            self.counter.getMicroseconds()

        with self.assertRaises(ValueError):
            self.counter.getMilliseconds()

        with self.assertRaises(ValueError):
            self.counter.getSeconds()

        with self.assertRaises(ValueError):
            self.counter.getMinutes()

    def testZeroElapsedTime(self):
        """
        Test behavior when start and stop times are identical (zero elapsed time).

        Verifies that the counter correctly handles the edge case where
        start and stop are called with no measurable time difference.

        Returns
        -------
        None
        """
        with patch('time.perf_counter', return_value=42.0):
            self.counter.start()
            self.counter.stop()

            # All time measurements should be zero
            self.assertEqual(self.counter.elapsedTime(), 0.0)
            self.assertEqual(self.counter.getMicroseconds(), 0.0)
            self.assertEqual(self.counter.getMilliseconds(), 0.0)
            self.assertEqual(self.counter.getSeconds(), 0.0)
            self.assertEqual(self.counter.getMinutes(), 0.0)

    def testVerySmallElapsedTime(self):
        """
        Test behavior with very small elapsed times (nanosecond precision).

        Verifies that the counter maintains precision when dealing with very
        small time intervals, testing the limits of time.perf_counter() precision.

        Returns
        -------
        None
        """
        # Test with 1 microsecond difference
        with patch('time.perf_counter', side_effect=[1000.0, 1000.000001]):
            self.counter.start()
            self.counter.stop()

            elapsed = self.counter.elapsedTime()
            self.assertAlmostEqual(elapsed, 0.000001, places=6)
            self.assertAlmostEqual(self.counter.getMicroseconds(), 1.0, places=1)
            self.assertAlmostEqual(self.counter.getMilliseconds(), 0.001, places=3)

    def testLargeElapsedTime(self):
        """
        Test behavior with large elapsed times (hours/days).

        Verifies that the counter correctly handles large time intervals
        and that all unit conversions work properly with large values.

        Returns
        -------
        None
        """
        # Test with 2 hours (7200 seconds)
        with patch('time.perf_counter', side_effect=[0.0, 7200.0]):
            self.counter.start()
            self.counter.stop()

            elapsed = self.counter.elapsedTime()
            self.assertEqual(elapsed, 7200.0)
            self.assertEqual(self.counter.getSeconds(), 7200.0)
            self.assertEqual(self.counter.getMinutes(), 120.0)
            self.assertEqual(self.counter.getMilliseconds(), 7200000.0)
            self.assertEqual(self.counter.getMicroseconds(), 7200000000.0)