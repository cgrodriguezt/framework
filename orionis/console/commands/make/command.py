from pathlib import Path
import re
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.console.core.contracts.reactor import IReactor
from orionis.foundation.contracts.application import IApplication

class MakeCommand(BaseCommand):

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "make:command"

    # Command description
    description: str = "Creates a new custom console command for the Orionis CLI."

    def options(self) -> list[CLIArgument]:
        """
        Define command-line arguments for the make:command command.

        Specifies required and optional arguments for CLI invocation.

        Returns
        -------
        list[CLIArgument]
            List of CLIArgument objects representing available options.
        """
        return [
            CLIArgument(
                name="name",
                type=str,
                required=True,
                help="The filename where the new command will be created.",
            ),
            CLIArgument(
                flags=["--signature", "-s"],
                type=str,
                required=False,
                help="The signature for the new command.",
            ),
        ]

    def handle(
        self,
        app: IApplication,
        reactor: IReactor,
    ) -> None:
        """
        Create a new custom console command file.

        Validate arguments, check for signature duplication, load a stub template,
        replace placeholders, and write the code to a new file in the commands
        directory. Ensure the file does not already exist.

        Parameters
        ----------
        app : IApplication
            Application instance for path resolution.
        reactor : IReactor
            Reactor instance for command information.

        Returns
        -------
        None
            This method does not return a value.
        """
        try:
            # Retrieve the 'name' and 'signature' arguments
            name: str = self.argument("name")
            signature: str = self.argument("signature", "custom:command")

            # Validate that the name argument is provided
            if not name:
                error_msg = "The 'name' argument is required."
                raise ValueError(error_msg)

            # Check for duplicate command signature
            commands: list[dict] = reactor.info()
            for command in commands:
                if command.get("signature") == signature:
                    error_msg = (
                        f"A command with the signature '{signature}' already exists. "
                        "Please choose another signature."
                    )
                    raise ValueError(error_msg)

            # Validate the file name format
            if not re.match(r"^[a-z][a-z0-9_]*$", name):
                error_msg = "Invalid 'name' format."
                raise ValueError(error_msg)

            # Validate the command signature format
            if not re.match(r"^[a-z][a-z0-9_:]*$", signature):
                error_msg = "Invalid 'signature' format."
                raise ValueError(error_msg)

            # Load the command stub template from the stubs directory
            stub_path = (
                Path(__file__).parent.parent.parent / "stubs" / "command.stub"
            )
            with Path.open(stub_path, encoding="utf-8") as file:
                stub = file.read()

            # Generate the class name by capitalizing each word and appending 'Command'
            class_name = "".join(word.capitalize() for word in name.split("_"))
            if not class_name.endswith("Command"):
                class_name = class_name.rstrip("_") + "Command"

            # Replace placeholders in the stub with the actual class name and signature
            stub = stub.replace("{{class_name}}", class_name)
            stub = stub.replace("{{signature}}", signature)

            # Ensure the commands directory exists
            commands_dir = app.path("console") / "commands"
            commands_dir.mkdir(parents=True, exist_ok=True)

            # Ensure the name ends with 'command' (case-insensitive)
            if not name.lower().endswith("command"):
                name = name.rstrip("_") + "_command"

            # Define the full path for the new command file
            file_path = commands_dir / f"{name}.py"

            # Check if the file already exists to prevent overwriting
            if file_path.exists():
                file_path_rel = file_path.relative_to(app.path("root"))
                error_msg = (
                    f"The file [{file_path_rel}] already exists. "
                    "Please choose another name."
                )
                raise OSError(error_msg)

            # Write the generated command code to the new file
            with Path.open(file_path, "w", encoding="utf-8") as file:
                file.write(stub)
            file_path_rel = file_path.relative_to(app.path("root"))
            self.success(f"Console command [{file_path_rel}] created successfully.")

        except (ValueError, OSError) as e:

            # Handle validation and file I/O errors
            self.error(f"Failed to create command: {e}")
