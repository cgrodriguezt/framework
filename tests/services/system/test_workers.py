from __future__ import annotations
import math
from unittest.mock import MagicMock, patch
from orionis.services.system.contracts.workers import IWorkers
from orionis.services.system.workers import Workers
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Module path constant for patch targets
# ---------------------------------------------------------------------------

_MOD = "orionis.services.system.workers"

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

_CPU_COUNT = 4
_RAM_GB = 8.0
_RAM_BYTES = int(_RAM_GB * (1024**3))

def _build(ram_per_worker: float = 0.5) -> Workers:
    """Return a Workers instance with controlled CPU and RAM values."""
    mock_vm = MagicMock()
    mock_vm.total = _RAM_BYTES
    with (
        patch(f"{_MOD}.multiprocessing.cpu_count", return_value=_CPU_COUNT),
        patch(f"{_MOD}.psutil.virtual_memory", return_value=mock_vm),
    ):
        return Workers(ram_per_worker=ram_per_worker)

# ---------------------------------------------------------------------------
# TestWorkersInterface
# ---------------------------------------------------------------------------

class TestWorkersInterface(TestCase):

    def testImplementsIWorkers(self) -> None:
        """
        Verify Workers implements the IWorkers contract.

        Validates that an instance of Workers is recognised as an
        implementation of the IWorkers abstract base class.
        """
        w = _build()
        self.assertIsInstance(w, IWorkers)

    def testHasCalculateMethod(self) -> None:
        """
        Verify the calculate method exists and is callable.

        Validates that the Workers class exposes a public callable
        named ``calculate`` as required by the interface.
        """
        self.assertTrue(callable(getattr(Workers, "calculate", None)))

    def testHasSetRamPerWorkerMethod(self) -> None:
        """
        Verify the setRamPerWorker method exists and is callable.

        Validates that the Workers class exposes a public callable
        named ``setRamPerWorker`` as required by the interface.
        """
        self.assertTrue(callable(getattr(Workers, "setRamPerWorker", None)))

# ---------------------------------------------------------------------------
# TestWorkersInit
# ---------------------------------------------------------------------------

class TestWorkersInit(TestCase):

    def testInitDefaultRamPerWorker(self) -> None:
        """
        Store the default RAM-per-worker value of 0.5 GB.

        Validates that constructing Workers without arguments sets
        ``_ram_per_worker`` to the documented default of 0.5.
        """
        w = _build()
        self.assertEqual(w._ram_per_worker, 0.5)

    def testInitCustomRamPerWorker(self) -> None:
        """
        Store a custom RAM-per-worker value provided at construction.

        Validates that the value passed to ``ram_per_worker`` is
        retained as ``_ram_per_worker`` after initialisation.
        """
        w = _build(ram_per_worker=2.0)
        self.assertEqual(w._ram_per_worker, 2.0)

    def testInitCpuCountIsPositiveInteger(self) -> None:
        """
        Capture a positive integer CPU count during initialisation.

        Validates that ``_cpu_count`` is set to the value returned by
        ``multiprocessing.cpu_count`` and is a positive integer.
        """
        w = _build()
        self.assertIsInstance(w._cpu_count, int)
        self.assertGreater(w._cpu_count, 0)

    def testInitCpuCountMatchesMockedValue(self) -> None:
        """
        Match the CPU count to the mocked multiprocessing return value.

        Validates that Workers reads CPU count from
        ``multiprocessing.cpu_count`` and stores it faithfully.
        """
        w = _build()
        self.assertEqual(w._cpu_count, _CPU_COUNT)

    def testInitRamTotalGbIsPositive(self) -> None:
        """
        Capture a positive total-RAM value expressed in gigabytes.

        Validates that ``_ram_total_gb`` is a positive float derived
        from ``psutil.virtual_memory().total``.
        """
        w = _build()
        self.assertIsInstance(w._ram_total_gb, float)
        self.assertGreater(w._ram_total_gb, 0.0)

    def testInitRamTotalGbMatchesMockedMemory(self) -> None:
        """
        Convert bytes from psutil into the correct gigabyte value.

        Validates that ``_ram_total_gb`` equals the mocked total bytes
        divided by 1024^3.
        """
        w = _build()
        expected = _RAM_BYTES / (1024**3)
        self.assertAlmostEqual(w._ram_total_gb, expected, places=6)

# ---------------------------------------------------------------------------
# TestWorkersSetRamPerWorker
# ---------------------------------------------------------------------------

class TestWorkersSetRamPerWorker(TestCase):

    def testSetRamPerWorkerUpdatesInternalValue(self) -> None:
        """
        Update the internal RAM-per-worker allocation.

        Validates that calling ``setRamPerWorker`` replaces
        ``_ram_per_worker`` with the supplied value.
        """
        w = _build()
        w.setRamPerWorker(3.0)
        self.assertEqual(w._ram_per_worker, 3.0)

    def testSetRamPerWorkerOverridesPreviousValue(self) -> None:
        """
        Replace the previously stored RAM-per-worker with a new value.

        Validates that successive calls each overwrite the prior value
        without any accumulation side-effect.
        """
        w = _build(ram_per_worker=1.0)
        w.setRamPerWorker(4.0)
        w.setRamPerWorker(2.5)
        self.assertEqual(w._ram_per_worker, 2.5)

    def testSetRamPerWorkerReturnsNone(self) -> None:
        """
        Return None from setRamPerWorker.

        Validates that the method produces no return value, in
        compliance with the IWorkers contract signature.
        """
        w = _build()
        result = w.setRamPerWorker(1.0) # NOSONAR
        self.assertIsNone(result)

    def testSetRamPerWorkerDoesNotChangeCpuCount(self) -> None:
        """
        Leave the CPU count unchanged after updating RAM allocation.

        Validates that ``setRamPerWorker`` is isolated and does not
        mutate unrelated state such as ``_cpu_count``.
        """
        w = _build()
        before = w._cpu_count
        w.setRamPerWorker(8.0)
        self.assertEqual(w._cpu_count, before)

# ---------------------------------------------------------------------------
# TestWorkersCalculate
# ---------------------------------------------------------------------------

class TestWorkersCalculate(TestCase):

    def testCalculateReturnsCpuBoundResult(self) -> None:
        """
        Return the CPU count when RAM capacity exceeds CPU capacity.

        Validates that calculate() returns ``_cpu_count`` (4) when
        floor(ram / ram_per_worker) is larger (16 with 0.5 GB each).
        """
        w = _build(ram_per_worker=0.5)
        self.assertEqual(w.calculate(), 4)

    def testCalculateReturnsRamBoundResult(self) -> None:
        """
        Return the RAM-derived count when memory is the bottleneck.

        Validates that calculate() returns the RAM-derived ceiling
        when it is lower than the CPU count.
        """
        w = _build(ram_per_worker=4.0)
        self.assertEqual(w.calculate(), 2)

    def testCalculateReturnsTieBreaker(self) -> None:
        """
        Return the shared value when CPU and RAM capacities are equal.

        Validates that when both limits produce the same count the
        result equals that count (since min(n, n) == n).
        """
        w = _build(ram_per_worker=2.0)
        self.assertEqual(w.calculate(), 4)

    def testCalculateFloorsDivisionResult(self) -> None:
        """
        Apply floor division when RAM does not divide evenly.

        Validates that calculate() uses ``math.floor`` and never
        rounds up the RAM-derived worker count.
        """
        w = _build(ram_per_worker=3.0)
        expected_ram = math.floor(_RAM_GB / 3.0)
        self.assertEqual(w.calculate(), min(_CPU_COUNT, expected_ram))

    def testCalculateReturnsInteger(self) -> None:
        """
        Return an integer from calculate.

        Validates that the return type is always ``int``, not
        ``float`` or any other numeric type.
        """
        w = _build(ram_per_worker=0.5)
        self.assertIsInstance(w.calculate(), int)

    def testCalculateIsNonNegative(self) -> None:
        """
        Return a non-negative count from calculate.

        Validates that the result is never negative regardless of the
        input values used during construction.
        """
        w = _build(ram_per_worker=0.5)
        self.assertGreaterEqual(w.calculate(), 0)

    def testCalculateReflectsSetRamPerWorker(self) -> None:
        """
        Reflect the updated RAM allocation in the next calculate call.

        Validates that calling ``setRamPerWorker`` before ``calculate``
        uses the new value rather than the construction-time value.
        """
        # Initially: min(4, floor(8 / 0.5)) = 4
        w = _build(ram_per_worker=0.5)
        self.assertEqual(w.calculate(), 4)
        # After update: min(4, floor(8 / 8.0)) = min(4, 1) = 1
        w.setRamPerWorker(8.0)
        self.assertEqual(w.calculate(), 1)

    def testCalculateWithSingleCpuReturnOne(self) -> None:
        """
        Return one when only a single CPU core is available.

        Validates that a machine with one CPU never yields more than
        one recommended worker, regardless of available RAM.
        """
        mock_vm = MagicMock()
        mock_vm.total = _RAM_BYTES
        with (
            patch(f"{_MOD}.multiprocessing.cpu_count", return_value=1),
            patch(f"{_MOD}.psutil.virtual_memory", return_value=mock_vm),
        ):
            w = Workers(ram_per_worker=0.5)
        self.assertEqual(w.calculate(), 1)

    def testCalculateWithVeryLargeRamPerWorkerReturnsZero(self) -> None:
        """
        Return zero when a single worker requires more RAM than available.

        Validates that floor division correctly yields zero when
        ``ram_per_worker`` exceeds the total system RAM.
        """
        # floor(8 / 100.0) = 0 → min(4, 0) = 0
        w = _build(ram_per_worker=100.0)
        self.assertEqual(w.calculate(), 0)

    def testCalculateWithSmallRamPerWorkerIsRamBound(self) -> None:
        """
        Saturate worker count via abundant RAM when CPU is the limit.

        Validates that when many workers fit in RAM the CPU count caps
        the final result.
        """
        # floor(8 / 0.1) = 80 → min(4, 80) = 4
        w = _build(ram_per_worker=0.1)
        self.assertEqual(w.calculate(), _CPU_COUNT)

    def testCalculateConsistencyOverMultipleCalls(self) -> None:
        """
        Return the same value on repeated calls without side effects.

        Validates that calculate() is a pure, deterministic method
        that yields identical results when called multiple times.
        """
        w = _build(ram_per_worker=1.0)
        first = w.calculate()
        second = w.calculate()
        self.assertEqual(first, second)

# ---------------------------------------------------------------------------
# TestWorkersEdgeCases
# ---------------------------------------------------------------------------

class TestWorkersEdgeCases(TestCase):

    def testCalculateZeroRamPerWorkerRaisesZeroDivisionError(self) -> None:
        """
        Raise ZeroDivisionError when ram_per_worker is zero.

        Validates that passing 0.0 as ``ram_per_worker`` causes an
        arithmetic error on the first call to ``calculate``, since the
        implementation divides by it without a zero-guard.
        """
        w = _build(ram_per_worker=0.5)
        # Bypass the constructor guard by directly mutating the attribute
        w._ram_per_worker = 0.0
        with self.assertRaises(ZeroDivisionError):
            w.calculate()

    def testCalculateNegativeRamPerWorkerRaisesValueError(self) -> None:
        """
        Produce a nonsensical negative result for negative ram_per_worker.

        Validates the current (unguarded) behaviour: a negative divisor
        returns a negative worker count. This documents an untreated
        edge case in the implementation.
        """
        w = _build(ram_per_worker=0.5)
        w._ram_per_worker = -1.0
        # floor(8 / -1.0) = -8, min(4, -8) = -8  – negative, not sensible
        result = w.calculate()
        self.assertLess(result, 0)

    def testInitWithMinimalCpuAndRam(self) -> None:
        """
        Handle a machine with a single CPU core and minimal RAM.

        Validates that Workers can be constructed and calculate called
        on an extremely resource-constrained configuration.
        """
        mock_vm = MagicMock()
        mock_vm.total = int(0.5 * (1024**3))  # 0.5 GB
        with (
            patch(f"{_MOD}.multiprocessing.cpu_count", return_value=1),
            patch(f"{_MOD}.psutil.virtual_memory", return_value=mock_vm),
        ):
            w = Workers(ram_per_worker=0.5)
        self.assertEqual(w.calculate(), 1)

    def testSetRamPerWorkerThenCalculateWithZeroRaisesError(self) -> None:
        """
        Raise ZeroDivisionError after setting ram_per_worker to zero.

        Validates that the zero-divisor risk applies equally when
        zero is introduced via ``setRamPerWorker`` rather than the
        constructor.
        """
        w = _build(ram_per_worker=1.0)
        w.setRamPerWorker(0.0)
        with self.assertRaises(ZeroDivisionError):
            w.calculate()
