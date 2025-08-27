import asyncio
from pathlib import Path
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.console.exceptions.cli_runtime_error import CLIOrionisRuntimeError
from orionis.services.inspirational.contracts.inspire import IInspire
from orionis.support.facades.directory import Directory

class InspireCommand(BaseCommand):

    # Enable timestamps in console output by default
    timestamps: bool = True

    # Nombre del commando, por convención en minúsculas e iniciando con app.
    signature: str = "app:inspire"

    # Descripcion del comando.
    description: str = "Prints a random inspirational quote."

    # Argumentos Posibles Para El Comando.
    # Ejemplo completo usando todas las propiedades de CLIArgument
    arguments = [
        CLIArgument(
            flags=["--export", "-e"],
            type=bool,
            help="Export the quote to a file in the specified format.",
            default=False,
            choices=None,
            required=False,
            metavar="EXPORT",
            dest="export_quote",
            action="store_true",
            nargs=None,
            const=True
        ),
        CLIArgument(
            flags=["--format", "-f"],
            type=str,
            help="Format of the exported file. Choose between text or JSON format.",
            default="txt",
            choices=["txt", "json"],
            required=False,
            metavar="FILE_FORMAT",
            dest="output_format",
            action="store",
            nargs=None,
            const=None
        ),
        CLIArgument(
            flags=["--filename", "-n"],
            type=str,
            help="Custom name for the exported quote file (without extension).",
            default="inspirational_quote",
            choices=None,
            required=False,
            metavar="FILENAME",
            dest="output_filename",
            action="store",
            nargs="?",
            const="default_quote"
        )
    ]

    async def handle(self, inspire: IInspire) -> None:
        """
        Handle the inspire command execution.

        This method retrieves a random inspirational quote from the inspire service
        and displays it in the console with formatting. Optionally exports the quote
        to a file based on command arguments.

        Parameters
        ----------
        inspire : IInspire
            The inspirational service interface used to retrieve random quotes.

        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        CLIOrionisRuntimeError
            If an unexpected error occurs during quote retrieval or processing.
        """

        try:

            # Sleep for 2 seconds to simulate a delay (optional)
            await asyncio.sleep(2)

            # Retrieve a random inspirational quote from the service
            random_quote: dict = inspire.random()

            # Check if the quote was successfully retrieved
            if not random_quote:
                raise CLIOrionisRuntimeError("No inspirational quote found.")

            # Destructure the dictionary to extract quote and author
            quote: str = random_quote.get("quote")
            author: str = random_quote.get("author")

            # Display the quote in console with success formatting (bold green)
            self.textSuccessBold(quote)

            # Display the author with muted formatting (gray text)
            self.textMuted(author)

            # Export the quote to a file if the export flag is set
            if self.argument('export_quote'):

                # Retrieve the output filename and format from command arguments
                output_filename: str = self.argument('output_filename')
                output_format: str = self.argument('output_format')

                # Directory path to store the exported quotes
                path = Path(Directory.storage() / "quotes")
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)

                # Full file path with the specified filename and format
                path = path / f"{output_filename}.{output_format}"

                # Open the file in write mode with UTF-8 encoding
                with open(path, "w", encoding="utf-8") as file:

                    # Write the quote and author in text format
                    if output_format == "txt":
                        file.write(f"{quote}\n- {author}\n")

                    # Write the quote and author in JSON format
                    elif output_format == "json":
                        import json
                        json.dump({"quote": quote, "author": author}, file, ensure_ascii=False, indent=4)

                # Display a success message for export
                self.info(f"Quote exported successfully to {output_filename}.{output_format}")

        except Exception as e:

            # Handle known CLIOrionisRuntimeError exceptions
            if isinstance(e, CLIOrionisRuntimeError):
                raise e

            # Handle any unexpected errors during execution
            raise CLIOrionisRuntimeError(f"An unexpected error occurred: {e}")