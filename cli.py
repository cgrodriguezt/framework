from orionis.console import main

if __name__ == "__main__":
    """
    This script serves as the entry point for the Orionis Framework command-line interface (CLI).
    It imports the `main` function from the `orionis.console` module and executes it when the script
    is run directly. The `main` function is responsible for handling CLI commands and orchestrating
    the framework's operations.

    The `main` function provides the following functionality:
    - Displays the current version of Orionis using the `--version` flag.
    - Upgrades Orionis to the latest version using the `--upgrade` flag.
    - Creates a new Orionis application using the `new` command and an optional application name.
    - Displays general information if no specific command is provided.

    Usage:
        Run this script directly to invoke the Orionis Framework CLI.

    Examples:
        Show the current version of Orionis:
            python cli.py --version

        Upgrade Orionis to the latest version:
            python cli.py --upgrade

        Create a new Orionis application:
            python cli.py new my-app-name

        Display general information:
            python cli.py
    """
    main()