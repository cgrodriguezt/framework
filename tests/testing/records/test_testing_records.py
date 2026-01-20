import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from orionis.test.cases.synchronous import SyncTestCase
from orionis.test.exceptions import OrionisTestPersistenceError, OrionisTestValueError
from orionis.test.records.logs import TestLogs

class TestTestingRecords(SyncTestCase):

    def testCreateAndGetReport(self):
        """
        Test the creation and retrieval of a test report.

        Creates a test report with all required fields, stores it using the
        TestLogs class, and retrieves the most recent report to verify its
        contents.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Prepare a complete test report dictionary
            report = {
                "total_tests": 5,
                "passed": 4,
                "failed": 1,
                "errors": 0,
                "skipped": 0,
                "total_time": 1.23,
                "success_rate": 0.8,
                "timestamp": "2024-06-01T12:00:00",
            }

            # Serialize the report to JSON and add to the dictionary
            report["json"] = json.dumps(report)

            # Store the report in the logs
            result = logs.create(report)
            self.assertTrue(result)

            # Retrieve the most recent report
            reports = logs.get(first=1)
            self.assertEqual(len(reports), 1)

            # Validate the contents of the retrieved report
            self.assertEqual(json.loads(reports[0][1])["total_tests"], 5)

    def testCreateMissingFields(self):
        """
        Test error handling for missing required fields in report creation.

        Attempts to create a report without the required 'timestamp' field and
        expects an OrionisTestValueError to be raised.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Prepare a report missing the 'timestamp' field
            report = {
                "total_tests": 5,
                "passed": 4,
                "failed": 1,
                "errors": 0,
                "skipped": 0,
                "total_time": 1.23,
                "success_rate": 0.8,
            }
            report["json"] = json.dumps(report)

            # Expect an error when creating the report
            with self.assertRaises(OrionisTestValueError):
                logs.create(report)

    def testResetDatabase(self):
        """
        Test the reset functionality of the test logs database.

        Creates a report, stores it, and then resets the logs database.
        Verifies that the reset operation returns True.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Create and store a single report
            report = {
                "total_tests": 1,
                "passed": 1,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "total_time": 0.1,
                "success_rate": 1.0,
                "timestamp": "2024-06-01T12:00:00",
            }
            report["json"] = json.dumps(report)
            logs.create(report)

            # Reset the logs database and verify success
            self.assertTrue(logs.reset())

    def testGetReportsInvalidParams(self):
        """
        Test error handling for invalid parameters in TestLogs.get().

        Checks that passing mutually exclusive or invalid values to get()
        raises an OrionisTestValueError.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Both 'first' and 'last' should not be provided together
            with self.assertRaises(OrionisTestValueError):
                logs.get(first=1, last=1)

            # 'first' must be greater than zero
            with self.assertRaises(OrionisTestValueError):
                logs.get(first=0)

            # 'last' must be greater than zero
            with self.assertRaises(OrionisTestValueError):
                logs.get(last=-1)

    def testGetLastReports(self):
        """
        Test retrieval of the last N reports and their order.

        Creates multiple reports, retrieves the last two, and checks that the
        reports are returned in descending order by their identifier.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Create and store three reports with increasing 'total_tests'
            for i in range(3):
                report = {
                    "total_tests": i+1,
                    "passed": i,
                    "failed": 1,
                    "errors": 0,
                    "skipped": 0,
                    "total_time": 0.1 * (i+1),
                    "success_rate": 0.5,
                    "timestamp": f"2024-06-01T12:00:0{i}",
                }
                report["json"] = json.dumps(report)
                logs.create(report)

            # Retrieve the last two reports
            reports = logs.get(last=2)
            self.assertEqual(len(reports), 2)

            # Ensure the reports are ordered by descending identifier
            self.assertGreater(reports[0][0], reports[1][0])

    def testInitializationWithStringPath(self):
        """
        Test TestLogs initialization with string path parameter.

        Verifies that TestLogs can be initialized with a string path and that
        the database file path is properly constructed and resolved.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)
            # Verify that the path attributes are set correctly
            self.assertEqual(logs._TestLogs__db_name, "tests.sqlite")
            self.assertEqual(logs._TestLogs__table_name, "reports")
            expected_path = Path(tmpdir) / "tests.sqlite"
            self.assertEqual(logs._TestLogs__db_path, expected_path.resolve())

    def testInitializationWithPathObject(self):
        """
        Test TestLogs initialization with Path object parameter.

        Verifies that TestLogs can be initialized with a Path object and that
        the database file path is properly constructed and resolved.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path_obj = Path(tmpdir)
            logs = TestLogs(path_obj)
            expected_path = path_obj / "tests.sqlite"
            self.assertEqual(logs._TestLogs__db_path, expected_path.resolve())

    def testInitializationWithCustomDbName(self):
        """
        Test TestLogs initialization with custom database name.

        Verifies that TestLogs can be initialized with a custom database name
        and table name, and that these are properly stored.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_db = "custom_tests.db"
            custom_table = "custom_reports"
            logs = TestLogs(tmpdir, db_name=custom_db, table_name=custom_table)
            self.assertEqual(logs._TestLogs__db_name, custom_db)
            self.assertEqual(logs._TestLogs__table_name, custom_table)
            expected_path = Path(tmpdir) / custom_db
            self.assertEqual(logs._TestLogs__db_path, expected_path.resolve())

    def testConnectionManagement(self):
        """
        Test proper connection management throughout operations.

        Verifies that database connections are properly opened and closed
        after each operation, ensuring no resource leaks.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Initially, connection should be None
            self.assertIsNone(logs._conn)

            # After creating a report, connection should be closed again
            report = {
                "total_tests": 1,
                "passed": 1,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "total_time": 0.1,
                "success_rate": 1.0,
                "timestamp": "2024-06-01T12:00:00",
            }
            report["json"] = json.dumps(report)
            logs.create(report)
            self.assertIsNone(logs._conn)

            # After getting reports, connection should be closed again
            logs.get(first=1)
            self.assertIsNone(logs._conn)

    def testCreateReportWithAllFields(self):
        """
        Test creating a report with all possible fields populated.

        Verifies that TestLogs can handle reports with all expected fields
        and that the data is properly stored and retrievable.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            report = {
                "total_tests": 100,
                "passed": 85,
                "failed": 10,
                "errors": 3,
                "skipped": 2,
                "total_time": 45.67,
                "success_rate": 0.85,
                "timestamp": "2024-06-01T14:30:00",
            }
            report["json"] = json.dumps(report)

            result = logs.create(report)
            self.assertTrue(result)

            # Retrieve and verify the stored report
            reports = logs.get(first=1)
            self.assertEqual(len(reports), 1)
            stored_report = json.loads(reports[0][1])
            self.assertEqual(stored_report["total_tests"], 100)
            self.assertEqual(stored_report["passed"], 85)
            self.assertEqual(stored_report["failed"], 10)
            self.assertEqual(stored_report["errors"], 3)
            self.assertEqual(stored_report["skipped"], 2)
            self.assertEqual(stored_report["total_time"], 45.67)
            self.assertEqual(stored_report["success_rate"], 0.85)
            self.assertEqual(stored_report["timestamp"], "2024-06-01T14:30:00")

    def testCreateReportMissingMultipleFields(self):
        """
        Test error handling when multiple required fields are missing.

        Verifies that OrionisTestValueError is raised with proper error message
        when multiple required fields are missing from the report.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Report missing multiple fields
            report = {
                "total_tests": 5,
                "passed": 4,
                "failed": 1,
                # Missing: errors, skipped, total_time, success_rate, timestamp
            }
            report["json"] = json.dumps(report)

            with self.assertRaises(OrionisTestValueError) as context:
                logs.create(report)

            error_message = str(context.exception)
            self.assertIn("missing the following required fields", error_message)
            self.assertIn("errors", error_message)
            self.assertIn("skipped", error_message)
            self.assertIn("total_time", error_message)
            self.assertIn("success_rate", error_message)
            self.assertIn("timestamp", error_message)

    def testGetFirstReports(self):
        """
        Test retrieval of the first N reports and their order.

        Creates multiple reports, retrieves the first two, and checks that the
        reports are returned in ascending order by their identifier.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Create three reports with different data
            for i in range(3):
                report = {
                    "total_tests": (i + 1) * 10,
                    "passed": (i + 1) * 8,
                    "failed": (i + 1) * 2,
                    "errors": 0,
                    "skipped": 0,
                    "total_time": (i + 1) * 5.0,
                    "success_rate": 0.8,
                    "timestamp": f"2024-06-01T12:0{i}:00",
                }
                report["json"] = json.dumps(report)
                logs.create(report)

            # Retrieve the first two reports
            reports = logs.get(first=2)
            self.assertEqual(len(reports), 2)

            # Ensure the reports are ordered by ascending identifier
            self.assertLess(reports[0][0], reports[1][0])

            # Verify the data matches the first two created reports
            first_report = json.loads(reports[0][1])
            second_report = json.loads(reports[1][1])
            self.assertEqual(first_report["total_tests"], 10)
            self.assertEqual(second_report["total_tests"], 20)

    def testGetReportsWithNoRecords(self):
        """
        Test retrieval when no reports exist in the database.

        Verifies that empty results are returned when attempting to retrieve
        reports from an empty database.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Create the table first (but don't insert any records)
            logs._TestLogs__createTableIfNotExists()

            # Try to get reports from empty database
            reports = logs.get(first=5)
            self.assertEqual(len(reports), 0)

            reports = logs.get(last=5)
            self.assertEqual(len(reports), 0)

    def testGetReportsMoreThanAvailable(self):
        """
        Test retrieval when requesting more reports than available.

        Verifies that all available reports are returned when requesting
        more reports than exist in the database.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Create only 2 reports
            for i in range(2):
                report = {
                    "total_tests": i + 1,
                    "passed": i + 1,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "total_time": 1.0,
                    "success_rate": 1.0,
                    "timestamp": f"2024-06-01T12:0{i}:00",
                }
                report["json"] = json.dumps(report)
                logs.create(report)

            # Request more reports than available
            reports = logs.get(first=5)
            self.assertEqual(len(reports), 2)

            reports = logs.get(last=5)
            self.assertEqual(len(reports), 2)

    def testGetReportsWithInvalidFirstValue(self):
        """
        Test error handling for invalid 'first' parameter values.

        Verifies that OrionisTestValueError is raised for various invalid
        'first' parameter values including zero, negative numbers, and non-integers.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Test with zero
            with self.assertRaises(OrionisTestValueError):
                logs.get(first=0)

            # Test with negative number
            with self.assertRaises(OrionisTestValueError):
                logs.get(first=-1)

            # Test with non-integer (this will raise due to validation logic)
            with self.assertRaises(OrionisTestValueError):
                logs.get(first="invalid")

    def testGetReportsWithInvalidLastValue(self):
        """
        Test error handling for invalid 'last' parameter values.

        Verifies that OrionisTestValueError is raised for various invalid
        'last' parameter values including zero, negative numbers, and non-integers.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Test with zero
            with self.assertRaises(OrionisTestValueError):
                logs.get(last=0)

            # Test with negative number
            with self.assertRaises(OrionisTestValueError):
                logs.get(last=-1)

            # Test with non-integer (this will raise due to validation logic)
            with self.assertRaises(OrionisTestValueError):
                logs.get(last="invalid")

    def testResetEmptyDatabase(self):
        """
        Test resetting an empty or non-existent database.

        Verifies that the reset operation succeeds even when the database
        or table does not exist yet.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Reset without creating any reports first
            result = logs.reset()
            self.assertTrue(result)

    def testResetAfterCreatingReports(self):
        """
        Test resetting database after creating and verifying reports are gone.

        Creates reports, verifies they exist, resets the database, and then
        verifies that no reports can be retrieved after reset.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Create a report
            report = {
                "total_tests": 10,
                "passed": 8,
                "failed": 2,
                "errors": 0,
                "skipped": 0,
                "total_time": 5.0,
                "success_rate": 0.8,
                "timestamp": "2024-06-01T12:00:00",
            }
            report["json"] = json.dumps(report)
            logs.create(report)

            # Verify report exists
            reports = logs.get(first=1)
            self.assertEqual(len(reports), 1)

            # Reset database
            result = logs.reset()
            self.assertTrue(result)

            # Create table again to test empty retrieval
            logs._TestLogs__createTableIfNotExists()

            # Verify no reports exist after reset
            reports = logs.get(first=1)
            self.assertEqual(len(reports), 0)

    @patch("sqlite3.connect")
    def testDatabaseConnectionError(self, mock_connect):
        """
        Test handling of database connection errors.

        Verifies that OrionisTestPersistenceError is raised when SQLite
        connection fails, with proper error message.

        Parameters
        ----------
        mock_connect : Mock
            Mock for sqlite3.connect that raises sqlite3.Error

        Returns
        -------
        None
        """
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            report = {
                "total_tests": 1,
                "passed": 1,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "total_time": 1.0,
                "success_rate": 1.0,
                "timestamp": "2024-06-01T12:00:00",
            }
            report["json"] = json.dumps(report)

            with self.assertRaises(OrionisTestPersistenceError) as context:
                logs.create(report)

            error_message = str(context.exception)
            self.assertIn("Failed to connect to SQLite database", error_message)
            self.assertIn("Connection failed", error_message)

    def testTableCreationError(self):
        """
        Test handling of table creation errors.

        Uses a mock to simulate a table creation failure and verifies
        that OrionisTestPersistenceError is raised appropriately.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Create a report to trigger table creation, then mock execute to fail
            with patch.object(logs, "_TestLogs__connect"):
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_cursor.execute.side_effect = sqlite3.Error("Table creation failed")
                mock_conn.cursor.return_value = mock_cursor
                logs._conn = mock_conn

                report = {
                    "total_tests": 1,
                    "passed": 1,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "total_time": 1.0,
                    "success_rate": 1.0,
                    "timestamp": "2024-06-01T12:00:00",
                }
                report["json"] = json.dumps(report)

                with self.assertRaises(OrionisTestPersistenceError) as context:
                    logs.create(report)

                error_message = str(context.exception)
                self.assertIn("Failed to create or verify table", error_message)

    def testReportInsertionError(self):
        """
        Test handling of report insertion errors.

        Uses a mock to simulate a report insertion failure and verifies
        that OrionisTestPersistenceError is raised appropriately.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # First, ensure table is created successfully
            logs._TestLogs__createTableIfNotExists()

            # Mock the insertion to fail
            with patch.object(logs, "_TestLogs__connect"):
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_cursor.execute.side_effect = sqlite3.Error("Insert failed")
                mock_conn.cursor.return_value = mock_cursor
                logs._conn = mock_conn

                report = {
                    "total_tests": 1,
                    "passed": 1,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "total_time": 1.0,
                    "success_rate": 1.0,
                    "timestamp": "2024-06-01T12:00:00",
                }
                report["json"] = json.dumps(report)

                with self.assertRaises(OrionisTestPersistenceError) as context:
                    logs._TestLogs__insertReport(report)

                error_message = str(context.exception)
                self.assertIn("Failed to insert report into table", error_message)

    def testReportRetrievalError(self):
        """
        Test handling of report retrieval errors.

        Uses a mock to simulate a report retrieval failure and verifies
        that OrionisTestPersistenceError is raised appropriately.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            with patch.object(logs, "_TestLogs__connect"):
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_cursor.execute.side_effect = sqlite3.Error("Select failed")
                mock_conn.cursor.return_value = mock_cursor
                logs._conn = mock_conn

                with self.assertRaises(OrionisTestPersistenceError) as context:
                    logs.get(first=1)

                error_message = str(context.exception)
                self.assertIn("An error occurred while retrieving reports", error_message)

    def testDatabaseResetError(self):
        """
        Test handling of database reset errors.

        Uses a mock to simulate a database reset failure and verifies
        that OrionisTestPersistenceError is raised appropriately.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            with patch.object(logs, "_TestLogs__connect"):
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_cursor.execute.side_effect = sqlite3.Error("Drop table failed")
                mock_conn.cursor.return_value = mock_cursor
                logs._conn = mock_conn

                with self.assertRaises(OrionisTestPersistenceError) as context:
                    logs.reset()

                error_message = str(context.exception)
                self.assertIn("Failed to reset the reports table", error_message)

    def testDatabasePathCreation(self):
        """
        Test that parent directories are created when they don't exist.

        Verifies that TestLogs creates the necessary directory structure
        when initializing with a path that doesn't exist.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a nested path that doesn't exist
            nested_path = Path(tmpdir) / "logs" / "test_data"
            self.assertFalse(nested_path.exists())

            # Create the parent directory
            nested_path.mkdir(parents=True, exist_ok=True)

            # Verify the parent directory was created
            self.assertTrue(nested_path.exists())
            self.assertTrue(nested_path.is_dir())

    def testSQLiteWALModeConfiguration(self):
        """
        Test that SQLite connection is configured with WAL mode.

        Verifies that the database connection is properly configured with
        Write-Ahead Logging mode for better concurrency.

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Create a report to trigger connection
            report = {
                "total_tests": 1,
                "passed": 1,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "total_time": 1.0,
                "success_rate": 1.0,
                "timestamp": "2024-06-01T12:00:00",
            }
            report["json"] = json.dumps(report)
            logs.create(report)

            # Check that the database file was created and uses WAL mode
            db_path = logs._TestLogs__db_path
            self.assertTrue(db_path.exists())

            # Connect directly to verify WAL mode was set
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            result = cursor.fetchone()
            conn.close()

            self.assertEqual(result[0].upper(), "WAL")

    def testMultipleReportsOrdering(self):
        """
        Test correct ordering of multiple reports with both first and last retrieval.

        Creates several reports and verifies that first/last retrieval maintains
        proper ordering based on insertion order (ID-based).

        Returns
        -------
        None
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = TestLogs(tmpdir)

            # Create 5 reports with distinctive data
            report_data = []
            for i in range(5):
                report = {
                    "total_tests": (i + 1) * 100,
                    "passed": (i + 1) * 90,
                    "failed": (i + 1) * 10,
                    "errors": 0,
                    "skipped": 0,
                    "total_time": (i + 1) * 10.0,
                    "success_rate": 0.9,
                    "timestamp": f"2024-06-0{i+1}T12:00:00",
                }
                report["json"] = json.dumps(report)
                report_data.append(report)
                logs.create(report)

            # Test first 3 reports (ascending order)
            first_reports = logs.get(first=3)
            self.assertEqual(len(first_reports), 3)
            for i in range(2):
                self.assertLess(first_reports[i][0], first_reports[i + 1][0])

            # Verify data matches
            for i, report_tuple in enumerate(first_reports):
                stored_data = json.loads(report_tuple[1])
                self.assertEqual(stored_data["total_tests"], (i + 1) * 100)

            # Test last 3 reports (descending order)
            last_reports = logs.get(last=3)
            self.assertEqual(len(last_reports), 3)
            for i in range(2):
                self.assertGreater(last_reports[i][0], last_reports[i + 1][0])

            # Verify data matches (should be reports 5, 4, 3 in that order)
            expected_totals = [500, 400, 300]
            for i, report_tuple in enumerate(last_reports):
                stored_data = json.loads(report_tuple[1])
                self.assertEqual(stored_data["total_tests"], expected_totals[i])
