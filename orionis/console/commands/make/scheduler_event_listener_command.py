import re
from pathlib import Path
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.foundation.contracts.application import IApplication

class MakeSchedulerListenerCommand(BaseCommand):

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "make:scheduler-event-listener"

    # Command description
    description: str = (
        "Creates a new custom scheduler listener to handle events for a scheduled task."
    )

    def options(self) -> list[CLIArgument]:
        """
        Return the CLI arguments required for this command.

        Returns
        -------
        list[CLIArgument]
            A list containing the required CLIArgument for the listener name.
        """
        return [
            CLIArgument(
                flags=["name"],
                type=str,
                required=True,
                help="The filename where the new command will be created.",
            ),
        ]

    def handle(self, app: IApplication) -> None:
        """
        Create a scheduler listener file.

        Validate the listener name, load the stub template, generate the
        listener class, ensure the listeners directory exists, and write the
        new listener file. Prevent overwriting if the file already exists.

        Parameters
        ----------
        app : IApplication
            The application instance used to resolve paths.

        Returns
        -------
        None
        """
        try:

            # Retrieve the 'name' argument (required)
            listener_name: str = self.argument("name")

            # Validate that the listener_name argument is provided
            if not listener_name:
                error_msg = "The 'name' argument is required."
                raise ValueError(error_msg)

            # Validate listener name format
            if not re.match(r"^[a-z][a-z0-9_]*$", listener_name):
                error_msg = (
                    "The 'name' argument must start with a lowercase letter and "
                    "contain only lowercase letters, numbers, and underscores (_)."
                )
                raise ValueError(error_msg)

            # Load the listener stub template from the stubs directory
            stub_path = Path(__file__).parent.parent / "stubs" / "listener.stub"
            with Path.open(stub_path, encoding="utf-8") as file:
                stub_content = file.read()

            # Generate the class name by capitalizing each word and appending 'Listener'
            class_name = "".join(word.capitalize() for word in listener_name.split("_"))
            if not class_name.endswith("Listener"):
                class_name = class_name.rstrip("_") + "Listener"

            # Replace placeholders in the stub with the actual class name
            stub_content = stub_content.replace("{{class_name}}", class_name)

            # Ensure the listeners directory exists
            listeners_dir = app.path("console") / "listeners"
            listeners_dir.mkdir(parents=True, exist_ok=True)

            # Ensure the listener_name ends with 'listener' (case-insensitive)
            if not listener_name.lower().endswith("listener"):
                listener_name = listener_name.rstrip("_") + "_listener"

            file_path = listeners_dir / f"{listener_name}.py"

            # Check if the file already exists to prevent overwriting
            if file_path.exists():
                relative_path = file_path.relative_to(app.path("root"))
                error_msg = (
                    f"The file [{relative_path}] already exists. "
                    "Please choose a different name."
                )
                raise OSError(error_msg)

            # Write the generated listener code to the new file
            with Path.open(file_path, "w", encoding="utf-8") as file:
                file.write(stub_content)
            relative_path = file_path.relative_to(app.path("root"))
            self.info(f"Listener [{relative_path}] was created successfully.")

        except (ValueError, OSError) as e:

            # Handle validation and file I/O errors
            self.error(f"Failed to create listener: {e}")
