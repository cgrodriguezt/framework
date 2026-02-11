from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.foundation.contracts.application import IApplication
from orionis.test.core.engine import TestingEngine

class TestCommand(BaseCommand):

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "test"

    # Command description
    description: str = "Executes test cases defined in the project."

    def options(self) -> list[CLIArgument]:
        """
        Define command-line options for the test command.

        Parameters
        ----------
        self : TestCommand
            Instance of the TestCommand class.

        Returns
        -------
        list of CLIArgument
            List of CLIArgument objects describing available command-line
            options for the test command.
        """
        # Provide CLI options for test command configuration
        return [
            CLIArgument(
                flags=["--verbosity", "-v"],
                type=int,
                required=False,
                help=(
                    "Level of detail in test output. 0: silent, 1: standard, "
                    "2: detailed. Defaults to 2 (detailed)."
                ),
                dest="verbosity",
            ),
            CLIArgument(
                flags=["--fail-fast", "-f"],
                type=int,
                required=False,
                help=(
                    "1: Stop on first failure. 0: Continue running all tests. "
                    "Defaults to 0 (continue)."
                ),
                dest="fail_fast",
            ),
            CLIArgument(
                flags=["--start-dir", "-s"],
                type=str,
                required=False,
                help=(
                    "Directory to search for tests. Defaults to 'tests'."
                ),
                dest="start_dir",
            ),
            CLIArgument(
                flags=["--file-pattern"],
                type=str,
                required=False,
                help=(
                    "Filename pattern to identify test files. Defaults to 'test_*.py'."
                ),
                dest="file_pattern",
            ),
            CLIArgument(
                flags=["--method-pattern"],
                type=str,
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
        cli_args = self.arguments()

        # Extract verbosity setting from CLI args or app config
        verbosity = (
            cli_args.get("verbosity")
            or app.config("testing.verbosity")
        )

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

        # Set method pattern in application config for use in test case method filtering
        app.config("_runtime.testing.method_pattern", method_pattern)

        # Set verbosity level in application config for use in test result output formatting
        app.config("_runtime.testing.verbosity", verbosity)

        # Configure and execute testing engine
        engine = TestingEngine(app)
        engine.setFailFast(fail_fast)
        engine.setVerbosity(verbosity)
        engine.setStartDir(start_dir)
        engine.setFilePattern(file_pattern)
        engine.setMethodPattern(method_pattern)
        await engine.run()
