from typing import ClassVar
from orionis.console.args.argument import Argument
from orionis.console.base.command import BaseCommand
from orionis.foundation.contracts.application import IApplication
from orionis.test.contracts.engine import ITestingEngine

class TestCommand(BaseCommand):

    # ruff: noqa: TC001 (DI)

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "test"

    # Command description
    description: str = "Executes test cases defined in the project."

    # List of Argument instances defining command-line options and arguments
    arguments: ClassVar[list[Argument]] = [
        Argument(
            name_or_flags=["--verbosity", "-v"],
            type_=int,
            required=False,
            help=(
                "Level of detail in test output. 0: silent, 1: standard, "
                "2: detailed. Defaults to 2 (detailed)."
            ),
            dest="verbosity",
        ),
        Argument(
            name_or_flags=["--fail-fast", "-f"],
            type_=int,
            required=False,
            help=(
                "1: Stop on first failure. 0: Continue running all tests. "
                "Defaults to 0 (continue)."
            ),
            dest="fail_fast",
        ),
        Argument(
            name_or_flags=["--start-dir", "-s"],
            type_=str,
            required=False,
            help=(
                "Directory to search for tests. Defaults to 'tests'."
            ),
            dest="start_dir",
        ),
        Argument(
            name_or_flags=["--file-pattern"],
            type_=str,
            required=False,
            help=(
                "Filename pattern to identify test files. Defaults to 'test_*.py'."
            ),
            dest="file_pattern",
        ),
        Argument(
            name_or_flags=["--method-pattern"],
            type_=str,
            required=False,
            help=(
                "Pattern to filter specific test methods. Defaults to 'test*'."
            ),
            dest="method_pattern",
        ),
    ]

    async def handle(
        self,
        app: IApplication,
        test_engine: ITestingEngine,
    ) -> None:
        """
        Execute the test command with configured parameters.

        Parameters
        ----------
        app : IApplication
            Application instance providing configuration and context.

        Returns
        -------
        None
            Method executes tests and outputs results to console.
        """
        # Retrieve command-line arguments for test execution
        cli_args = self.getArguments() or {}

        # Extract verbosity setting from CLI args or app config
        verbosity = int(
            cli_args.get("verbosity")
            or app.config("testing.verbosity"),
        )

        if verbosity not in [0, 1, 2]:
            error_message = (
                "Invalid verbosity level. Allowed values are 0 (silent), "
                "1 (standard), 2 (detailed)."
            )
            raise ValueError(error_message)

        # Determine fail_fast setting from CLI args or app config
        fail_fast = (
            cli_args.get("fail_fast")
            or app.config("testing.fail_fast") in [1, True, "1", "true", "True"]
        )

        # Extract test discovery directory from CLI args or app config
        start_dir = (
            cli_args.get("start_dir")
            or app.config("testing.start_dir")
        )

        # Extract file pattern for test discovery from CLI args or app config
        file_pattern = (
            cli_args.get("file_pattern")
            or app.config("testing.file_pattern")
        )

        # Extract method pattern for test discovery from CLI args or app config
        method_pattern = (
            cli_args.get("method_pattern")
            or app.config("testing.method_pattern")
        )

        # Configure and execute testing engine
        test_engine.setFailFast(fail_fast=fail_fast)
        test_engine.setVerbosity(verbosity)
        test_engine.setStartDir(start_dir)
        test_engine.setFilePattern(file_pattern)
        test_engine.setMethodPattern(method_pattern)
        await test_engine.run()
