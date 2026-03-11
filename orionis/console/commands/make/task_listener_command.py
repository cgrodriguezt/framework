import re
from pathlib import Path
from orionis.console.args.argument import Argument
from orionis.console.base.command import BaseCommand
from orionis.foundation.contracts.application import IApplication

class MakeCommand(BaseCommand):

    # ruff: noqa: TC001 (DI)

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "make:task-listener"

    # Command description
    description: str = "Creates a new task listener class."

    # Command arguments definition
    arguments: list[Argument] = [
        Argument(
            name_or_flags="name",
            type_=str,
            required=True,
            help=(
                "The filename and class name for the new task listener "
                "(e.g., 'send_email_listener')."
            ),
        )
    ]

    async def handle(
        self,
        app: IApplication,
    ) -> None:
        # Insert a blank line before the command output for better readability
        self.newLine()

        try:

            # Retrieve the 'name' from the command arguments
            name: str = self.getArgument("name")

            # Validate that the name argument is provided
            if not name:
                error_msg = "The 'name' argument is required."
                raise ValueError(error_msg)

            # Validate the file name format
            if not re.match(r"^[a-z][a-z0-9_]*$", name):
                error_msg = "Invalid 'name' format."
                raise ValueError(error_msg)

            # Load the task listener stub template from the stubs directory
            stub_path = (
                Path(__file__).parent.parent.parent / "stubs" / "task_listener.stub"
            )
            with Path.open(stub_path, encoding="utf-8") as file:
                stub = file.read()

            # Generate the class name by capitalizing each word and appending 'Command'
            class_name = "".join(word.capitalize() for word in name.split("_"))
            if not class_name.endswith("Listener"):
                class_name = class_name.rstrip("_") + "Listener"

            # Replace placeholders in the stub with the actual class name and signature
            stub = stub.replace("{{class_name}}", class_name)

            # Ensure the listeners directory exists
            listeners_dir = app.path("console") / "listeners"
            listeners_dir.mkdir(parents=True, exist_ok=True)

            # Ensure the name ends with 'listener' (case-insensitive)
            if not name.lower().endswith("listener"):
                name = name.rstrip("_") + "_listener"

            # Define the full path for the new command file
            file_path = listeners_dir / f"{name}.py"

            # Check if the file already exists to prevent overwriting
            if file_path.exists():
                file_path_rel = file_path.relative_to(app.basePath)
                error_msg = (
                    f"The file [{file_path_rel}] already exists. "
                    "Please choose another name."
                )
                raise OSError(error_msg)

            # Write the generated command code to the new file
            with Path.open(file_path, "w", encoding="utf-8") as file:
                file.write(stub)
            file_path_rel = file_path.relative_to(app.basePath)
            self.success(f"Task listener [{file_path_rel}] created successfully.")

        except (ValueError, OSError) as e:

            # Handle validation and file I/O errors
            self.error(f"Failed to create task listener: {e}")

        finally:

            # Insert a blank line after the command output for better readability
            self.newLine()
