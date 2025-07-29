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
