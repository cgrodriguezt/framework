import asyncio
import json
from pathlib import Path
from typing import List
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.services.inspirational.contracts.inspire import IInspire
from orionis.support.facades.directory import Directory

class InspireCommand(BaseCommand):

    # Command name, by convention in lowercase and starting with app.
    signature: str = "app:inspire"

    # Description of the command.
    description: str = "Prints a random inspirational quote."

    def options(self) -> List[CLIArgument]:
        """
        Specifies the command-line arguments accepted by the InspireCommand.

        This asynchronous method defines the available options for the command, allowing users
        to customize the behavior of the command-line tool. Options include exporting the quote
        to a file, selecting the export format, and specifying a custom filename for the exported quote.

        Parameters
        ----------
        None

        Returns
        -------
        List[CLIArgument]
            A list of CLIArgument objects, each representing a command-line argument or option
            that can be provided to the InspireCommand.
        """

        return [
            # Option to enable exporting the quote to a file
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
            # Option to specify the format of the exported file (either txt or json)
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
            # Option to specify a custom filename for the exported quote file
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
        Executes the inspire command by retrieving and displaying a random inspirational quote.
        Optionally, exports the quote to a file in the specified format if requested.

        Parameters
        ----------
        inspire : IInspire
            The inspirational service interface used to retrieve random quotes.

        Returns
        -------
        None
            This method does not return any value. It performs actions such as printing to the console
            and writing to a file if export is requested.

        Raises
        ------
        CLIOrionisRuntimeError
            Raised if no inspirational quote is found or if an unexpected error occurs during processing.
        """

        try:

            # Simulate a delay to mimic asynchronous operation (optional)
            await asyncio.sleep(2)

            # Retrieve a random inspirational quote from the service
            random_quote: dict = inspire.random()

            # Raise an error if no quote is retrieved
            if not random_quote:
                raise CLIOrionisRuntimeError("No inspirational quote found.")

            # Extract the quote and author from the dictionary
            quote: str = random_quote.get("quote")
            author: str = random_quote.get("author")

            # Display the quote in the console with bold green formatting
            self.textSuccessBold(quote)

            # Display the author in muted (gray) formatting
            self.textMuted(author)

            # Check if the export flag is set to export the quote to a file
            if self.argument('export_quote'):

                # Retrieve the output filename and format from command arguments
                output_filename: str = self.argument('output_filename')
                output_format: str = self.argument('output_format')

                # Define the directory path to store exported quotes
                path = Path(Directory.storage() / "quotes")

                # Create the directory if it does not exist
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)

                # Construct the full file path with the specified filename and format
                path = path / f"{output_filename}.{output_format}"

                # Open the file in write mode with UTF-8 encoding
                with open(path, "w", encoding="utf-8") as file: # NOSONAR

                    # Write the quote and author in plain text format
                    if output_format == "txt":
                        file.write(f"{quote}\n- {author}\n")

                    # Write the quote and author in JSON format
                    elif output_format == "json":
                        json.dump({"quote": quote, "author": author}, file, ensure_ascii=False, indent=4)

                # Inform the user that the quote was exported successfully
                self.info(f"Quote exported successfully to {output_filename}.{output_format}")

        except Exception as e:

            # Propagate any exceptions that occur as CLIOrionisRuntimeError
            raise CLIOrionisRuntimeError(f"An error occurred: {str(e)}") from e
