import contextlib
import inspect
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from orionis.console.base.command import BaseCommand
from orionis.console.core.contracts.reactor import IReactor
from orionis.metadata import framework
from orionis.metadata.framework import VERSION

class PublisherCommand(BaseCommand):

    # ruff: noqa: S603

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "__publisher__"

    # Command description
    description: str = "Publishes Package to the Orionis repository."

    def __init__(self, console: Console) -> None:
        """
        Initialize PublisherCommand with console and essential attributes.

        Parameters
        ----------
        console : Console
            Rich Console instance for formatted output.

        Returns
        -------
        None
            This method initializes instance attributes for use in other methods.
        """
        # Store the console instance for output
        self.__console = console

        # Set the project root to the current working directory
        self.__project_root = Path.cwd()

        # Calculate the width for console panels (3/4 of the console width)
        # self.__with_console = (self.__console.width // 4) * 3
        self.__with_console = 80

        # Retrieve the PyPI token from environment variables
        self.__token: str | None = None

    def __bumpMinorVersion(self) -> None:
        """
        Bump the minor version number in the VERSION constant file.

        Locates the file containing the VERSION constant, reads its contents,
        increments the minor version component, and writes the updated version
        string back to the file. The major and patch components remain unchanged.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method updates the version in-place in the file and prints a message.

        Raises
        ------
        FileNotFoundError
            If the file containing the VERSION constant cannot be found.
        IOError
            If there is an error reading from or writing to the file.
        """
        # Import the module to locate the VERSION constant file
        filepath = Path(inspect.getfile(framework))
        if not filepath.exists():
            error_msg = f"VERSION file not found at {filepath}"
            raise FileNotFoundError(error_msg)

        # Read all lines from the file
        with Path.open(filepath) as f:
            lines = f.readlines()

        # Prepare a list to hold the new lines
        new_lines = []

        # Regex to match the VERSION assignment line
        pattern = re.compile(
            r'^(VERSION\s*=\s*["\'])(\d+)\.(\d+)\.(\d+)(["\'])',
        )

        # Iterate through each line and update the version if matched
        for line in lines:
            match = pattern.match(line)
            if match:
                major, minor, patch = (
                    int(match.group(2)),
                    int(match.group(3)),
                    int(match.group(4)),
                )
                minor += 1
                new_version = (
                    f"{match.group(1)}{major}.{minor}.{patch}{match.group(5)}"
                )
                new_lines.append(new_version + "\n")
            else:
                new_lines.append(line)

        # Write the updated lines back to the file
        with Path.open(filepath, "w") as f:
            f.writelines(new_lines)

        # Print a message indicating the version has been bumped
        self.__console.print(
            Panel(
                f"[green]📦 Bumped minor version to {VERSION}[/]",
                border_style="green",
                width=self.__with_console,
            ),
        )

    def __gitPush(self) -> None:
        """
        Commit and push changes to the Git repository if modifications exist.

        Checks for uncommitted changes in the project directory. If changes are
        detected, stages all modifications, commits them with a message containing
        the current version, and pushes the commit to the remote repository. If
        there are no changes, logs a message indicating no commit or push is needed.

        Returns
        -------
        None
            This method does not return any value. All output is printed to the
            console.

        Raises
        ------
        subprocess.CalledProcessError
            If any subprocess call to Git fails.
        """
        # Check for modified files using Git status
        # Use full executable path for git to avoid S607
        git_executable = shutil.which("git") or "git"
        git_status = subprocess.run(
            [git_executable, "status", "--short"],
            check=False,
            capture_output=True,
            text=True,
            cwd=self.__project_root,
        )

        # Determine if there are modified files
        modified_files = git_status.stdout.strip()

        if modified_files:
            # Notify user about staging files
            self.__console.print(
                Panel(
                    "[cyan]📌 Staging files for commit...[/]",
                    border_style="cyan",
                    width=self.__with_console,
                ),
            )
            # Stage all modified files
            git_executable = shutil.which("git") or "git"
            subprocess.run(
                [git_executable, "add", "."],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.__project_root,
            )

            # Notify user about committing changes
            self.__console.print(
                Panel(
                    f"[cyan]✅ Committing changes: [📦 Release version {VERSION}][/]",
                    border_style="cyan",
                    width=self.__with_console,
                ),
            )

            # Wait briefly to ensure commit registration
            time.sleep(5)

            # Commit the changes with a message
            git_executable = shutil.which("git") or "git"
            subprocess.run(
                [git_executable, "commit", "-m", f"📦 Release version {VERSION}"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.__project_root,
            )

            # Notify user about pushing changes
            self.__console.print(
                Panel(
                    "[cyan]🚀 Pushing changes to the remote repository...[/]",
                    border_style="cyan",
                    width=self.__with_console,
                ),
            )

            # Push the changes to the remote repository
            # Use full executable path for git to avoid S607
            git_executable = shutil.which("git") or "git"
            subprocess.run(
                [git_executable, "push", "-f"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.__project_root,
            )

            # Notify user of successful push
            self.__console.print(
                Panel(
                    "[green]🌟 Git push completed![/]",
                    border_style="green",
                    width=self.__with_console,
                ),
            )
        else:
            # Notify user that there are no changes to commit
            self.__console.print(
                Panel(
                    "[green]✅ No changes to commit.[/]",
                    border_style="green",
                    width=self.__with_console,
                ),
            )

    def __build(self) -> None:
        """
        Build the package distributions using `setup.py`.

        Compiles the package by invoking the `setup.py` script at the project root.
        Generates both source (`sdist`) and wheel (`bdist_wheel`) distributions,
        which are required for publishing the package to a repository. If the
        `setup.py` file is not found, displays an error message and aborts the build.

        Returns
        -------
        None
            This method prints output to the console and does not return a value.

        Raises
        ------
        subprocess.CalledProcessError
            If the `setup.py` build command fails.
        """
        try:
            # Notify the user that the build process is starting
            self.__console.print(
                Panel(
                    "[cyan]🛠️  Building the package...[/]",
                    border_style="cyan",
                    width=self.__with_console,
                ),
            )

            # Define the path to the setup.py file in the project root
            setup_path = self.__project_root / "setup.py"

            # Check if setup.py exists in the project root
            if not setup_path.exists():
                msg = "setup.py not found in the current execution directory."
                self.__console.print(
                    Panel(
                        f"[bold red]❌ Error: {msg}[/]",
                        border_style="red",
                        width=self.__with_console,
                    ),
                )
                return

            # Run the setup.py script to build both sdist and wheel distributions
            subprocess.run(
                [sys.executable, "setup.py", "sdist", "bdist_wheel"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.__project_root,
            )

            # Notify the user that the build was successful
            self.__console.print(
                Panel(
                    "[green]✅ Build process completed successfully![/]",
                    border_style="green",
                    width=self.__with_console,
                ),
            )

        except subprocess.CalledProcessError as e:
            # Notify the user if the build process fails
            self.__console.print(
                Panel(
                    f"[bold red]❌ Build failed: {e}[/]",
                    border_style="red",
                    width=self.__with_console,
                ),
            )

    def __publish(self) -> None:
        """
        Upload built distributions to the PyPI repository using Twine.

        Locates the Twine executable, uploads all files in the `dist/` directory
        to PyPI using the authentication token from the `PYPI_TOKEN` environment
        variable, and cleans up temporary files after publishing.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method prints output to the console and does not return a value.

        Raises
        ------
        subprocess.CalledProcessError
            If the Twine upload or cleanup commands fail.
        ValueError
            If the PyPI token is not found in the environment variables.
        """
        # Retrieve the PyPI token from environment variables
        token: str | None = self.__token

        # Abort if the PyPI token is missing
        if not token:
            msg = "PyPI token not found in environment variables."
            self.__console.print(
                Panel(
                    f"[bold red]❌ Error: {msg}[/]",
                    border_style="red",
                    width=self.__with_console,
                ),
            )
            return

        # Prefer Twine from local virtual environment if available
        venv_twine = self.__project_root / "venv" / "Scripts" / "twine"
        twine_path = str(venv_twine.resolve()) if venv_twine.exists() else "twine"

        # Notify user that the upload process is starting
        self.__console.print(
            Panel(
                "[cyan]📤 Uploading package to PyPI...[/]",
                border_style="cyan",
                width=self.__with_console,
            ),
        )

        # Upload the package distributions to PyPI using Twine
        try:
            subprocess.run(
                [twine_path, "upload", "dist/*", "-u", "__token__", "-p", token],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.__project_root,
            )
            self.__console.print(
                Panel(
                    "[green]✅ Package published successfully![/]",
                    border_style="green",
                    width=self.__with_console,
                ),
            )
        except subprocess.CalledProcessError as e:
            error_msg = (
                f"🔴 Error uploading the package. Try changing the version and "
                f"retry. Error: {e}"
            )
            self.__console.print(
                Panel(
                    f"[bold red]{error_msg}[/]",
                    border_style="red",
                    width=self.__with_console,
                ),
            )
            sys.exit(1)

        # Notify user that cleanup is starting
        self.__console.print(
            Panel(
                "[cyan]🧹 Cleaning up temporary files...[/]",
                border_style="cyan",
                width=self.__with_console,
            ),
        )

        # Remove all .pyc files and __pycache__ directories recursively (cross-platform)
        for root, dirs, files in os.walk(self.__project_root):
            # Remove .pyc files
            for file in files:
                if file.endswith(".pyc"):
                    with contextlib.suppress(Exception):
                        (Path(root) / file).unlink()
            # Remove __pycache__ directories
            for dirname in dirs:
                if dirname == "__pycache__":
                    with contextlib.suppress(OSError):
                        shutil.rmtree(Path(root) / dirname)

        # Remove build artifacts and metadata directories
        self.__clearRepository()

        # Notify user that the publishing process is complete
        self.__console.print(
            Panel(
                "[bold green]✅ Publishing process completed successfully![/]",
                border_style="green",
                width=self.__with_console,
            ),
        )
        self.__console.print()

    def __clearRepository(self) -> None:
        """
        Remove build artifacts and metadata directories from the project root.

        Deletes the following directories if they exist:
        - 'build/': Temporary build files.
        - 'dist/': Distribution archives.
        - 'orionis.egg-info/': Package metadata.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. All output is printed to the
            console.

        Raises
        ------
        PermissionError
            If a directory cannot be deleted due to insufficient permissions.
        Exception
            If any other error occurs during the deletion process.
        """
        # Directories to remove after publishing
        folders: list[str] = ["build", "dist", "orionis.egg-info"]

        for folder in folders:
            folder_path = self.__project_root / folder

            # Remove the directory if it exists
            if folder_path.exists():
                try:
                    shutil.rmtree(folder_path)
                except PermissionError:
                    # Handle insufficient permissions error
                    self.__console.print(
                        Panel(
                            f"[bold red]❌ Error: Could not remove {folder_path} "
                            "due to insufficient permissions.[/]",
                            border_style="red",
                            width=self.__with_console,
                        ),
                    )
                except OSError as e:
                    # Handle other OS-related exceptions that may occur
                    self.__console.print(
                        Panel(
                            f"[bold red]❌ Error removing {folder_path}: {e!s}[/]",
                            border_style="red",
                            width=self.__with_console,
                        ),
                    )

    def handle(self, reactor: IReactor) -> None:
        """
        Execute the publish workflow for the Orionis CLI.

        Runs tests, bumps the minor version, pushes changes to Git, builds the
        package, and publishes it to PyPI. Aborts if tests fail or the PyPI token
        is missing.

        Parameters
        ----------
        reactor : IReactor
            Reactor instance providing command metadata and test execution.

        Returns
        -------
        None
            This method prints output to the console and does not return a value.

        Raises
        ------
        RuntimeError
            If an unexpected error occurs during the publish workflow.
        """
        try:
            # Retrieve the PyPI token from environment variables
            self.__token = os.environ.get("PYPI_TOKEN")
            if self.__token is not None:
                self.__token = self.__token.strip()

            # Ensure the PyPI token is available
            if not self.__token:
                error_msg = "PyPI token not found in environment variables."
                raise ValueError(error_msg)

            # Execute test suite via the reactor
            response: dict = reactor.call("test")

            # Check for failed tests or errors
            failed = response.get("failed", 0)
            errors = response.get("errors", 0)

            # Abort publishing if tests fail
            if failed > 0 or errors > 0:
                console = Console()
                console.print(
                    Panel(
                        f"Tests failed: {failed}, Errors: {errors}",
                        title="Test Suite Results",
                        style="bold red",
                    ),
                )
                return

            # Bump the minor version number
            self.__bumpMinorVersion()

            # Push changes to Git
            self.__gitPush()

            # Build the package
            self.__build()

            # Publish the package to PyPI
            self.__publish()

        except Exception as e:

            # Raise a runtime error for any unexpected exceptions
            error_msg = f"An unexpected error occurred: {e}"
            raise RuntimeError(error_msg) from e
