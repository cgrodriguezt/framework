from unittest.mock import patch
from orionis.services.system.workers import Workers
from orionis.test.cases.synchronous import SyncTestCase

class TestServicesSystemWorkers(SyncTestCase):

    @patch('multiprocessing.cpu_count', return_value=8)
    @patch('psutil.virtual_memory')
    def testCalculateCpuLimited(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test worker calculation when CPU count is the limiting factor.

        Simulates a system with 8 CPUs and 16 GB RAM, where each worker requires 1 GB of RAM.
        Although the available RAM could support up to 16 workers, the CPU count restricts the number
        of workers to 8.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that the calculated number of workers is limited by CPU count.
        """
        # Set the mocked total RAM to 16 GB
        mockVm.return_value.total = 16 * 1024 ** 3

        # Create Workers instance with 1 GB RAM required per worker
        workers = Workers(ram_per_worker=1)

        # Assert that the number of workers is limited to 8 by CPU count
        self.assertEqual(workers.calculate(), 8)

    @patch('multiprocessing.cpu_count', return_value=32)
    @patch('psutil.virtual_memory')
    def testCalculateRamLimited(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test worker calculation when RAM is the limiting factor.

        Simulates a system with 32 CPUs and 4 GB RAM, where each worker requires 1 GB of RAM.
        Although the CPU count could support up to 32 workers, the available RAM restricts the number
        of workers to 4.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that the calculated number of workers is limited by available RAM.
        """
        # Set the mocked total RAM to 4 GB
        mockVm.return_value.total = 4 * 1024 ** 3

        # Create Workers instance with 1 GB RAM required per worker
        workers = Workers(ram_per_worker=1)

        # Assert that the number of workers is limited to 4 by available RAM
        self.assertEqual(workers.calculate(), 4)

    @patch('multiprocessing.cpu_count', return_value=4)
    @patch('psutil.virtual_memory')
    def testCalculateExactFit(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test worker calculation when both CPU count and available RAM allow for the same number of workers.

        Simulates a system with 4 CPUs and 2 GB RAM, where each worker requires 0.5 GB of RAM.
        Both CPU and RAM resources permit exactly 4 workers, so the calculation should return 4.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that the calculated number of workers is 4, matching both CPU and RAM constraints.
        """
        # Set the mocked total RAM to 2 GB
        mockVm.return_value.total = 2 * 1024 ** 3

        # Create Workers instance with 0.5 GB RAM required per worker
        workers = Workers(ram_per_worker=0.5)

        # Assert that the number of workers is limited to 4 by both CPU and RAM
        self.assertEqual(workers.calculate(), 4)

    @patch('multiprocessing.cpu_count', return_value=2)
    @patch('psutil.virtual_memory')
    def testCalculateLowRam(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test worker calculation when available RAM is lower than CPU count, restricting the number of workers.

        Simulates a system with 2 CPUs and 0.7 GB RAM, where each worker requires 0.5 GB of RAM.
        Although the CPU count could support up to 2 workers, the available RAM restricts the number
        of workers to 1.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that the calculated number of workers is limited to 1 by available RAM.
        """
        # Set the mocked total RAM to 0.7 GB
        mockVm.return_value.total = 0.7 * 1024 ** 3

        # Create Workers instance with 0.5 GB RAM required per worker
        workers = Workers(ram_per_worker=0.5)

        # Assert that the number of workers is limited to 1 by available RAM
        self.assertEqual(workers.calculate(), 1)

    def testDefaultRamPerWorker(self):
        """
        Test that the Workers class initializes with the correct default RAM per worker value.

        Verifies that when no ram_per_worker parameter is provided during instantiation,
        the Workers class uses the default value of 0.5 GB per worker.

        Returns
        -------
        None
            Asserts that the default RAM per worker is set to 0.5 GB.
        """
        workers = Workers()

        # Assert that the default RAM per worker is 0.5 GB
        self.assertEqual(workers._ram_per_worker, 0.5)

    def testCustomRamPerWorker(self):
        """
        Test that the Workers class correctly accepts and stores custom RAM per worker values.

        Verifies that when a custom ram_per_worker parameter is provided during instantiation,
        the Workers class correctly stores and uses this value.

        Returns
        -------
        None
            Asserts that the custom RAM per worker value is correctly stored.
        """
        custom_ram = 2.0
        workers = Workers(ram_per_worker=custom_ram)

        # Assert that the custom RAM per worker value is correctly stored
        self.assertEqual(workers._ram_per_worker, custom_ram)

    def testSetRamPerWorker(self):
        """
        Test the setRamPerWorker method functionality.

        Verifies that the setRamPerWorker method correctly updates the RAM allocation
        per worker from the initial value to a new specified value.

        Returns
        -------
        None
            Asserts that the RAM per worker is correctly updated after calling setRamPerWorker.
        """
        workers = Workers(ram_per_worker=1.0)
        new_ram_value = 3.0

        # Update RAM per worker using the setter method
        workers.setRamPerWorker(new_ram_value)

        # Assert that the RAM per worker has been updated correctly
        self.assertEqual(workers._ram_per_worker, new_ram_value)

    @patch('multiprocessing.cpu_count', return_value=1)
    @patch('psutil.virtual_memory')
    def testCalculateMinimumWorkers(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test worker calculation with minimal system resources.

        Simulates a system with 1 CPU and minimal RAM to ensure the calculation
        returns at least 1 worker even in constrained environments.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that at least 1 worker is calculated even with minimal resources.
        """
        # Set minimal RAM (1 GB)
        mockVm.return_value.total = 1 * 1024 ** 3

        # Create Workers instance with 0.5 GB RAM per worker
        workers = Workers(ram_per_worker=0.5)

        # Assert that at least 2 workers can be calculated
        self.assertEqual(workers.calculate(), 1)

    @patch('multiprocessing.cpu_count', return_value=16)
    @patch('psutil.virtual_memory')
    def testCalculateHighRamPerWorker(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test worker calculation with high RAM requirements per worker.

        Simulates a scenario where each worker requires a large amount of RAM,
        significantly limiting the number of workers despite having many CPU cores.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that high RAM requirements per worker correctly limit the worker count.
        """
        # Set total RAM to 8 GB
        mockVm.return_value.total = 8 * 1024 ** 3

        # Create Workers instance with high RAM requirement (4 GB per worker)
        workers = Workers(ram_per_worker=4.0)

        # Assert that only 2 workers can be allocated due to RAM constraints
        self.assertEqual(workers.calculate(), 2)

    @patch('multiprocessing.cpu_count', return_value=8)
    @patch('psutil.virtual_memory')
    def testCalculateVeryLowRamPerWorker(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test worker calculation with very low RAM requirements per worker.

        Simulates a scenario where each worker requires very little RAM,
        allowing CPU count to be the limiting factor.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that low RAM requirements allow CPU count to be the limiting factor.
        """
        # Set total RAM to 4 GB
        mockVm.return_value.total = 4 * 1024 ** 3

        # Create Workers instance with very low RAM requirement (0.1 GB per worker)
        workers = Workers(ram_per_worker=0.1)

        # Assert that CPU count (8) is the limiting factor, not RAM (which could support 40 workers)
        self.assertEqual(workers.calculate(), 8)

    @patch('multiprocessing.cpu_count', return_value=4)
    @patch('psutil.virtual_memory')
    def testCalculateZeroWorkersScenario(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test worker calculation when RAM per worker exceeds total available RAM.

        Simulates a scenario where the RAM requirement per worker is greater than
        the total available system RAM, which should result in 0 workers.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that 0 workers are calculated when RAM per worker exceeds total RAM.
        """
        # Set total RAM to 2 GB
        mockVm.return_value.total = 2 * 1024 ** 3

        # Create Workers instance with RAM requirement exceeding total RAM (5 GB per worker)
        workers = Workers(ram_per_worker=5.0)

        # Assert that 0 workers are calculated when requirements exceed available resources
        self.assertEqual(workers.calculate(), 0)

    @patch('multiprocessing.cpu_count', return_value=8)
    @patch('psutil.virtual_memory')
    def testCalculateAfterRamPerWorkerUpdate(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test that worker calculation is affected by RAM per worker updates.

        Verifies that changing the RAM per worker allocation affects subsequent
        calculations without requiring a new Workers instance.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that worker calculations change appropriately after RAM per worker updates.
        """
        # Set total RAM to 8 GB
        mockVm.return_value.total = 8 * 1024 ** 3

        # Create Workers instance with initial RAM requirement (1 GB per worker)
        workers = Workers(ram_per_worker=1.0)

        # Initial calculation should return 8 workers
        initial_workers = workers.calculate()
        self.assertEqual(initial_workers, 8)

        # Update RAM per worker to 2 GB
        workers.setRamPerWorker(2.0)

        # New calculation should return 4 workers due to increased RAM requirement
        updated_workers = workers.calculate()
        self.assertEqual(updated_workers, 4)

    @patch('multiprocessing.cpu_count', return_value=16)
    @patch('psutil.virtual_memory')
    def testCalculateWithDecimalRamValues(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test worker calculation with decimal RAM values that result in floor division.

        Verifies that the calculation correctly handles scenarios where the division
        of total RAM by RAM per worker results in a decimal value that needs to be floored.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that decimal results are correctly floored to integer worker counts.
        """
        # Set total RAM to 7.5 GB (7.5 * 1024^3 bytes)
        mockVm.return_value.total = int(7.5 * 1024 ** 3)

        # Create Workers instance requiring 2.5 GB per worker
        workers = Workers(ram_per_worker=2.5)

        # 7.5 GB / 2.5 GB = 3 workers (floor of 3.0)
        self.assertEqual(workers.calculate(), 3)

    @patch('multiprocessing.cpu_count', return_value=12)
    @patch('psutil.virtual_memory')
    def testCalculateSystemResourcesConsistency(self, mockVm, mockCpuCount): # NOSONAR
        """
        Test that system resource values are correctly captured during initialization.

        Verifies that the Workers class correctly captures and stores CPU count
        and total RAM values during initialization, and these values remain consistent.

        Parameters
        ----------
        mockVm : unittest.mock.Mock
            Mock object for `psutil.virtual_memory`.
        mockCpuCount : unittest.mock.Mock
            Mock object for `multiprocessing.cpu_count`.

        Returns
        -------
        None
            Asserts that system resource values are correctly captured and stored.
        """
        # Set specific system resource values
        cpu_count = 12
        total_ram_gb = 32.0
        mockVm.return_value.total = int(total_ram_gb * 1024 ** 3)

        # Create Workers instance
        workers = Workers(ram_per_worker=1.0)

        # Assert that internal values match the mocked system resources
        self.assertEqual(workers._cpu_count, cpu_count)
        self.assertAlmostEqual(workers._ram_total_gb, total_ram_gb, places=1)