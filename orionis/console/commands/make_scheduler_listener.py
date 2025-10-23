import re
from pathlib import Path
from typing import List
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.foundation.contracts.application import IApplication

class MakeSchedulerListenerCommand(BaseCommand):
    """
    Command to create a new custom scheduler listener for scheduled task events.

    Attributes
    ----------
    timestamps : bool
        Indicates whether timestamps will be shown in the command output.
    signature : str
        Command signature.
    description : str
        Command description.

    Methods
    -------
    options() -> List[CLIArgument]
        Returns the CLI arguments required for this command.
    handle(app: IApplication) -> dict
        Handles the creation of the scheduler listener file.
    """

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "make:scheduler-listener"

    # Command description
    description: str = (
        "Creates a new custom scheduler listener to handle events for a scheduled task."
    )

    async def options(self) -> List[CLIArgument]:
        """
        Returns the CLI arguments required for this command.

        Returns
        -------
        List[CLIArgument]
            A list containing the required CLIArgument for the listener name.
        """

        # Define the required CLI argument for the listener name
        return [
            CLIArgument(
                flags=["name"],
                type=str,
                required=True,
                help="The filename where the new command will be created."
            )
        ]

    def handle(self, app: IApplication) -> dict:
        """
        Handles the creation of the scheduler listener file.

        This method validates the listener name, loads the stub template,
        generates the listener class, ensures the listeners directory exists,
        and writes the new listener file. If the file already exists, it
        prevents overwriting and displays an error.

        Parameters
        ----------
        app : IApplication
            The application instance used to resolve paths.

        Returns
        -------
        dict
            An empty dictionary. All output is handled via CLI messaging.
        """

        try:

            # Retrieve the 'name' argument (required)
            listener_name: str = self.argument("name")

            # Validate that the listener_name argument is provided
            if not listener_name:
                self.error("The 'name' argument is required.")

            # Validate that the listener name starts with a lowercase letter and contains only lowercase letters, numbers, or underscores
            if not re.match(r'^[a-z][a-z0-9_]*$', listener_name):
                self.error("The 'name' argument must start with a lowercase letter and contain only lowercase letters, numbers, and underscores (_).")

            # Load the listener stub template from the stubs directory
            stub_path = Path(__file__).parent.parent / "stubs" / "listener.stub"
            with open(stub_path, "r", encoding="utf-8") as file:
                stub_content = file.read()

            # Generate the class name by capitalizing each word and appending 'Listener'
            class_name = ''.join(word.capitalize() for word in listener_name.split('_'))
            if not class_name.endswith("Listener"):
                class_name = class_name.rstrip("_") + "Listener"

            # Replace placeholders in the stub with the actual class name
            stub_content = stub_content.replace("{{class_name}}", class_name)

            # Ensure the listeners directory exists
            listeners_dir = app.path('console') / "listeners"
            listeners_dir.mkdir(parents=True, exist_ok=True)

            # Ensure the listener_name ends with 'listener' (case-insensitive)
            if not listener_name.lower().endswith("listener"):
                listener_name = listener_name.rstrip("_") + "_listener"

            file_path = listeners_dir / f"{listener_name}.py"

            # Check if the file already exists to prevent overwriting
            if file_path.exists():
                relative_path = file_path.relative_to(app.path('root'))
                self.error(f"The file [{relative_path}] already exists. Please choose a different name.")
            else:
                # Write the generated listener code to the new file
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(stub_content)
                relative_path = file_path.relative_to(app.path('root'))
                self.info(f"Listener [{relative_path}] was created successfully.")

        except Exception as exc:

            # Catch any unexpected exceptions and raise a CLI-specific runtime error
            raise CLIOrionisRuntimeError(f"An unexpected error occurred: {exc}") from exc
