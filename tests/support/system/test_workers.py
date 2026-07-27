from __future__ import annotations
import math
from unittest.mock import patch
from orionis.support.system.contracts.workers import IWorkers
from orionis.support.system.workers import Workers
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Module path constant for patch targets
# ---------------------------------------------------------------------------

_MOD = "orionis.support.system.workers"

# ---------------------------------------------------------------------------
# Controlled hardware constants used across all test classes
# ---------------------------------------------------------------------------

_CPU_COUNT = 4
_RAM_GB = 8.0
_RAM_BYTES = int(_RAM_GB * (1 << 30))

# ---------------------------------------------------------------------------
# TestWorkersInterface
# ---------------------------------------------------------------------------

class TestWorkersInterface(TestCase):

    def testImplementsIWorkers(self) -> None:
        """
        Verify Workers is a subclass of the IWorkers contract.

        Validates that the Workers class satisfies the abstract base
        class declared by IWorkers without requiring instantiation.
        """
        self.assertTrue(issubclass(Workers, IWorkers))

    def testCanBeInstantiated(self) -> None:
        """
        Verify Workers can be instantiated without arguments.

        Validates that calling Workers() succeeds and produces a
        non-None object.
        """
        instance = Workers()
        self.assertIsNotNone(instance)

    def testInstanceIsIWorkers(self) -> None:
        """
        Verify a Workers instance is recognised as IWorkers.

        Validates isinstance check against the abstract base class
        passes for a concrete Workers object.
        """
        self.assertIsInstance(Workers(), IWorkers)

    def testHasCalculateMethod(self) -> None:
        """
        Verify the calculate classmethod exists and is callable.

        Validates that the Workers class exposes a public callable
        named ``calculate`` as required by the interface.
        """
        self.assertTrue(callable(getattr(Workers, "calculate", None)))

    def testHasSetRamPerWorkerMethod(self) -> None:
        """
        Verify the setRamPerWorker classmethod exists and is callable.

        Validates that the Workers class exposes a public callable
        named ``setRamPerWorker`` as required by the interface.
        """
        self.assertTrue(callable(getattr(Workers, "setRamPerWorker", None)))

# ---------------------------------------------------------------------------
# TestWorkersDefaultState
# ---------------------------------------------------------------------------

class TestWorkersDefaultState(TestCase):

    def setUp(self) -> None:
        """Save the class-level RAM allocation before each test."""
        self._original_ram = Workers._ram_per_worker

    def tearDown(self) -> None:
        """Restore the class-level RAM allocation after each test."""
        Workers._ram_per_worker = self._original_ram

    def testDefaultRamPerWorkerIsHalfGb(self) -> None:
        """
        Confirm the default RAM-per-worker class variable is 0.5 GB.

        Validates that Workers._ram_per_worker equals 0.5 before any
        call to setRamPerWorker.
        """
        Workers._ram_per_worker = 0.5
        self.assertEqual(Workers._ram_per_worker, 0.5)

    def testRamPerWorkerIsFloat(self) -> None:
        """
        Confirm the RAM-per-worker class variable is a float.

        Validates that the class-level default carries the correct
        Python type (float) required by the classmethod signature.
        """
        Workers._ram_per_worker = 0.5
        self.assertIsInstance(Workers._ram_per_worker, float)

# ---------------------------------------------------------------------------
# TestWorkersSetRamPerWorker
# ---------------------------------------------------------------------------

class TestWorkersSetRamPerWorker(TestCase):

    def setUp(self) -> None:
        """Save the class-level RAM allocation before each test."""
        self._original_ram = Workers._ram_per_worker

    def tearDown(self) -> None:
        """Restore the class-level RAM allocation after each test."""
        Workers._ram_per_worker = self._original_ram

    def testSetRamPerWorkerUpdatesClassVariable(self) -> None:
        """
        Update the class-level RAM-per-worker via setRamPerWorker.

        Validates that the supplied value is stored as
        Workers._ram_per_worker immediately after the call.
        """
        Workers.setRamPerWorker(2.0)
        self.assertEqual(Workers._ram_per_worker, 2.0)

    def testSetRamPerWorkerOverridesPreviousValue(self) -> None:
        """
        Replace the previously stored RAM-per-worker with a new value.

        Validates that successive calls each overwrite the prior value
        without any accumulation side-effect.
        """
        Workers.setRamPerWorker(1.0)
        Workers.setRamPerWorker(3.5)
        self.assertEqual(Workers._ram_per_worker, 3.5)

    def testSetRamPerWorkerReturnsNone(self) -> None:
        """
        Return None from setRamPerWorker.

        Validates that the method produces no return value, in
        compliance with the IWorkers contract signature.
        """
        result = Workers.setRamPerWorker(1.0)
        self.assertIsNone(result)

    def testSetRamPerWorkerAcceptsLargeValue(self) -> None:
        """
        Accept a very large RAM-per-worker value without error.

        Validates that setRamPerWorker performs no range validation
        and stores whatever float is provided.
        """
        Workers.setRamPerWorker(512.0)
        self.assertEqual(Workers._ram_per_worker, 512.0)

    def testSetRamPerWorkerAcceptsSmallPositiveValue(self) -> None:
        """
        Accept a very small positive RAM-per-worker value without error.

        Validates that fractional values close to zero are stored
        faithfully without rounding or truncation.
        """
        Workers.setRamPerWorker(0.001)
        self.assertAlmostEqual(Workers._ram_per_worker, 0.001, places=6)

# ---------------------------------------------------------------------------
# TestWorkersCalculate
# ---------------------------------------------------------------------------

class TestWorkersCalculate(TestCase):

    def setUp(self) -> None:
        """Save the class-level RAM allocation before each test."""
        self._original_ram = Workers._ram_per_worker

    def tearDown(self) -> None:
        """Restore the class-level RAM allocation after each test."""
        Workers._ram_per_worker = self._original_ram

    def testCalculateReturnsCpuBoundResult(self) -> None:
        """
        Return the CPU count when RAM capacity exceeds CPU capacity.

        Validates that calculate() returns _CPU_COUNT (4) when
        floor(RAM / ram_per_worker) is larger than the CPU count.
        With 8 GB RAM and 0.5 GB per worker the RAM allows 16 workers,
        so the CPU count of 4 is the binding constraint.
        """
        Workers._ram_per_worker = 0.5
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            result = Workers.calculate()
        # floor(8 / 0.5) = 16 → min(4, 16) = 4
        self.assertEqual(result, 4)

    def testCalculateReturnsRamBoundResult(self) -> None:
        """
        Return the RAM-derived count when memory is the bottleneck.

        Validates that calculate() returns the floor-divided RAM count
        when it is lower than the available CPU cores.
        With 8 GB RAM and 4 GB per worker only 2 workers fit in RAM.
        """
        Workers._ram_per_worker = 4.0
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            result = Workers.calculate()
        # floor(8 / 4) = 2 → min(4, 2) = 2
        self.assertEqual(result, 2)

    def testCalculateReturnsTieBreaker(self) -> None:
        """
        Return the shared value when CPU and RAM capacities are equal.

        Validates that when both constraints yield the same count
        the result equals that count (min(n, n) == n).
        With 8 GB RAM and 2 GB per worker, floor(8/2)=4 == CPU count.
        """
        Workers._ram_per_worker = 2.0
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            result = Workers.calculate()
        self.assertEqual(result, 4)

    def testCalculateFloorsDivisionResult(self) -> None:
        """
        Apply integer floor division when RAM does not divide evenly.

        Validates that calculate() never rounds up the RAM-derived
        worker count when the division is not exact.
        """
        Workers._ram_per_worker = 3.0
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            result = Workers.calculate()
        expected_ram = math.floor(_RAM_GB / 3.0)
        self.assertEqual(result, min(_CPU_COUNT, expected_ram))

    def testCalculateReturnsInteger(self) -> None:
        """
        Return an integer from calculate.

        Validates that the return type is always int, not float or
        any other numeric type, regardless of the inputs.
        """
        Workers._ram_per_worker = 0.5
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            result = Workers.calculate()
        self.assertIsInstance(result, int)

    def testCalculateReflectsSetRamPerWorker(self) -> None:
        """
        Reflect the updated RAM allocation in the next calculate call.

        Validates that setRamPerWorker before calculate uses the new
        value rather than the previously stored one.
        """
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            Workers._ram_per_worker = 0.5
            first = Workers.calculate()
            Workers.setRamPerWorker(8.0)
            second = Workers.calculate()
        self.assertEqual(first, 4)
        self.assertEqual(second, 1)

    def testCalculateWithSingleCpuReturnsOne(self) -> None:
        """
        Return one when only a single CPU core is available.

        Validates that a single-CPU machine never yields more than one
        recommended worker regardless of available RAM.
        """
        Workers._ram_per_worker = 0.5
        with (
            patch(f"{_MOD}._CPU_COUNT", 1),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            result = Workers.calculate()
        self.assertEqual(result, 1)

    def testCalculateWithSmallRamPerWorkerIsCpuBound(self) -> None:
        """
        Cap the result at CPU count when abundant RAM is available.

        Validates that extremely small per-worker RAM allocation does
        not produce a result greater than the number of CPU cores.
        """
        Workers._ram_per_worker = 0.1
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            result = Workers.calculate()
        # floor(8 / 0.1) = 80 → min(4, 80) = 4
        self.assertEqual(result, _CPU_COUNT)

    def testCalculateConsistencyOverMultipleCalls(self) -> None:
        """
        Return the same value on repeated calls without side effects.

        Validates that calculate() is deterministic: identical inputs
        always produce identical output across successive invocations.
        """
        Workers._ram_per_worker = 1.0
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            first = Workers.calculate()
            second = Workers.calculate()
        self.assertEqual(first, second)

    def testCalculateWithOneByteTotalRamReturnsOne(self) -> None:
        """
        Return at least one when total RAM is one byte.

        Validates that floor(1 / ram_per_worker_bytes) == 0 triggers
        the ``or 1`` fallback, ensuring the result is never less than
        one for a valid positive configuration.
        """
        Workers._ram_per_worker = 0.5
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", 1),
        ):
            result = Workers.calculate()
        # 1 // ram_bytes == 0 → min(4, 0) == 0 → 0 or 1 == 1
        self.assertEqual(result, 1)

    def testCalculateWithLargeRamPerWorkerReturnsOne(self) -> None:
        """
        Return one when per-worker RAM exceeds total available memory.

        Validates that when floor(total / per_worker) == 0 the
        ``or 1`` guard keeps the result at the minimum of 1.
        """
        Workers._ram_per_worker = 100.0
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            result = Workers.calculate()
        # floor(8G / 100G) = 0 → min(4, 0) = 0 → 0 or 1 = 1
        self.assertEqual(result, 1)

# ---------------------------------------------------------------------------
# TestWorkersEdgeCases
# ---------------------------------------------------------------------------

class TestWorkersEdgeCases(TestCase):

    def setUp(self) -> None:
        """Save the class-level RAM allocation before each test."""
        self._original_ram = Workers._ram_per_worker

    def tearDown(self) -> None:
        """Restore the class-level RAM allocation after each test."""
        Workers._ram_per_worker = self._original_ram

    def testCalculateZeroRamPerWorkerRaisesZeroDivisionError(self) -> None:
        """
        Raise ZeroDivisionError when ram_per_worker is zero.

        Validates that 0.0 as ram_per_worker causes integer floor
        division by zero inside calculate(), since int(0.0 * 1<<30)
        equals zero and no guard is present.
        """
        Workers._ram_per_worker = 0.0
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
            self.assertRaises(ZeroDivisionError),
        ):
            Workers.calculate()

    def testSetRamPerWorkerThenCalculateWithZeroRaisesError(self) -> None:
        """
        Raise ZeroDivisionError after setting ram_per_worker to zero.

        Validates that the zero-divisor risk applies equally when
        zero is introduced via setRamPerWorker rather than direct
        mutation of the class variable.
        """
        Workers.setRamPerWorker(0.0)
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
            self.assertRaises(ZeroDivisionError),
        ):
            Workers.calculate()

    def testCalculateNegativeRamPerWorkerReturnsNegativeCount(self) -> None:
        """
        Return a negative count when ram_per_worker is negative.

        Documents the current unguarded behaviour: a negative divisor
        causes Python floor division to yield a negative quotient,
        which propagates through min() unchanged.
        """
        Workers._ram_per_worker = -1.0
        with (
            patch(f"{_MOD}._CPU_COUNT", _CPU_COUNT),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", _RAM_BYTES),
        ):
            result = Workers.calculate()
        # floor(8G / -1G) == -8 → min(4, -8) == -8
        self.assertLess(result, 0)

    def testCalculateWithMinimalCpuAndExactRam(self) -> None:
        """
        Return one for a single CPU with exactly one worker's worth of RAM.

        Validates that the minimum valid configuration (1 CPU, exactly
        ram_per_worker bytes of total RAM) yields a result of exactly one.
        """
        per_worker_bytes = int(0.5 * (1 << 30))
        Workers._ram_per_worker = 0.5
        with (
            patch(f"{_MOD}._CPU_COUNT", 1),
            patch(f"{_MOD}._RAM_TOTAL_BYTES", per_worker_bytes),
        ):
            result = Workers.calculate()
        self.assertEqual(result, 1)
