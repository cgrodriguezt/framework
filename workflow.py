"""
Automates the setup, execution, and cleanup of a test environment.

This script performs the following operations:

- Removes the './storage' directory before running tests to ensure a clean environment.
- Executes 'test.py' as a separate process without generating .pyc files.
- Deletes the '.env' file if it exists after the tests complete.
- Removes the './storage' directory again after the tests for cleanup.

Notes
-----
This script is intended to be run as a standalone utility for managing test environments.
"""

import shutil
import os
import subprocess
import sys

# Clean the storage directory before running the tests
shutil.rmtree("./storage", ignore_errors=True)

# Run test.py as a separate process and wait for it to finish without generating pycache
subprocess.run([sys.executable, "-B", "test.py"], check=True)

# Delete .env files after tests
if os.path.exists(".env"):
    os.remove(".env")

# Clean the storage directory after running the tests
shutil.rmtree("./storage", ignore_errors=True)
