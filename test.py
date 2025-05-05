from orionis.luminate.console.output.console import Console
from orionis.luminate.test.test_suite import TestSuite

if __name__ == "__main__":
    """
    Entry point for executing Orionis tests.

    Runs the test suite, checks results, and exits with:
    - 0 if all tests pass.
    - 1 if any test fails or errors.

    Usage:
        $ python -B test.py
    """
    try:
        Console.newLine()
        Console.textSuccessBold("Orionis Framework - Test Suite")
        TestSuite.load().run(print_result=True, throw_exception=True)
        Console.exitSuccess()
    except Exception as e:
        Console.exitError(f"Test suite execution failed: {e}")
    finally:
        Console.newLine()