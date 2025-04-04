from orionis.luminate.test.tests import Tests

def orionis_tests(print_result:bool=True, throw_exception:bool=False):
    """
    Execute the tests in the specified folders with the given pattern
    and print the results. If an exception occurs, it will not be thrown.
    """

    # Define the test folders and their configurations
    # Each dictionary must contain:
    # - folder_path : str : Path to the folder containing test files
    # - base_path : str : Base path for the tests
    # - pattern : str : File pattern to match test files
    paths = [
        {'base_path': 'tests', 'folder_path': 'example', 'pattern': 'test_*.py'},
        {'base_path': 'tests', 'folder_path': 'support/inspection', 'pattern': 'test_*.py'},
    ]

    # Execute the tests and return the results
    return Tests.execute(paths, print_result, throw_exception)

if __name__ == "__main__":
    orionis_tests()