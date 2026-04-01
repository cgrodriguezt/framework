import re
from pathlib import Path
from typing import ClassVar
from orionis.console.args.argument import Argument
from orionis.console.base.command import BaseCommand
from orionis.foundation.contracts.application import IApplication

class MakeProvider(BaseCommand):

    # ruff: noqa: TC001, ASYNC240

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "make:provider"

    # Command description
    description: str = (
        "Creates a new provider class file in the providers directory."
    )

    # Command arguments definition
    arguments: ClassVar[list[Argument]] = [
        Argument(
            name_or_flags="name",
            type_=str,
            required=True,
            help=(
                "The filename and class name for the new provider class"
            ),
        ),
        Argument(
            name_or_flags=["--deferred"],
            type_=bool,
            default=False,
            help=(
                "If set, the provider will be deferred and only loaded "
                "when needed."
            ),
            action="store_true",
        ),
    ]

    async def handle(self, app: IApplication) -> None:
        """
        Create a new provider class file in the providers directory.

        Parameters
        ----------
        app : IApplication
            The application instance used to access paths and configuration.

        Returns
        -------
        None
            Outputs success or error messages to the console.
        """
        # Insert a blank line before the command output for readability
        self.newLine()

        try:

            # Retrieve the 'name' argument from command arguments
            name: str = self.getArgument("name")

            # Validate that the name argument is provided
            if not name:
                error_msg = "The 'name' argument is required."
                raise ValueError(error_msg)

            # Validate the file name format (lowercase alphanumeric/underscore)
            if not re.match(r"^[a-z][a-z0-9_]*$", name):
                error_msg = "Invalid 'name' format."
                raise ValueError(error_msg)

            # Retrieve the 'deferred' flag from command arguments
            deferred: bool = self.getArgument("deferred")

            # Select appropriate stub template based on deferred flag
            stub_name = (
                "eager_provider.stub"
                if not deferred
                else "deferred_provider.stub"
            )

            # Load the command stub template from the stubs directory
            stub_path = (
                Path(__file__).parent.parent.parent / "stubs" / stub_name
            )

            # Read the stub template content as a string
            with Path.open(stub_path, encoding="utf-8") as file: # NOSONAR
                stub: str = file.read()

            # Generate the class name by capitalizing words separated by
            # underscores and appending 'Provider' suffix
            class_name: str = "".join(
                word.capitalize() for word in name.split("_")
            )
            if not class_name.endswith("Provider"):
                class_name = class_name.rstrip("_") + "Provider"

            # Replace class name placeholder in the stub template
            stub = stub.replace("{{class_name}}", class_name)

            # Ensure the providers directory exists, creating if needed
            providers_dir: Path = app.path("providers")
            providers_dir.mkdir(parents=True, exist_ok=True)

            # Append '_provider' suffix if name does not already have it
            if not name.lower().endswith("provider"):
                name = name.rstrip("_") + "_provider"

            # Define the full file path for the new provider file
            file_path: Path = providers_dir / f"{name}.py"

            # Check if the file already exists to prevent overwriting
            if file_path.exists():
                file_path_rel: Path = file_path.relative_to(
                    app.basePath,
                )
                error_msg = (
                    f"The file [{file_path_rel}] already exists. "
                    "Please choose another name."
                )
                raise OSError(error_msg)

            # Write the generated provider code to the new file
            with Path.open(file_path, "w", encoding="utf-8") as file: # NOSONAR
                file.write(stub)

            # Display success message with the relative file path
            file_path_rel = file_path.relative_to(app.basePath)
            self.success(f"Provider [{file_path_rel}] created successfully.")

        except (ValueError, OSError) as e:

            # Handle validation and file I/O errors
            self.error(f"Failed to create provider: {e}")

        finally:

            # Insert a blank line after the command output for readability
            self.newLine()
