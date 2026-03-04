import asyncio
from orionis.console.args.argument import CLIArgument
from orionis.console.base.command import BaseCommand
from orionis.services.inspirational.inspire import Inspire

class InspireCommand(BaseCommand):

    # --------------------------------------------------------------------------
    # Adding a signature to the command is required to invoke it.
    # The command description clarifies its purpose when running 'help'.
    # If your command takes arguments, define them in the options method.
    # If it does not take arguments, you can omit the options method.
    # The handle method executes the command logic. You can inject any
    # services needed for your logic here. Remember, handle is async,
    # so you can use await to call async service methods. If your logic
    # does not require async, you can omit await and define it as sync.
    # --------------------------------------------------------------------------

    # Command name, by convention in lowercase and starting with app.
    signature: str = "app:inspire"

    # Description of the command.
    description: str = "Prints a random inspirational quote."

    def argumentDefinitions(self) -> list[CLIArgument]:
        """
        Define command-line options for the InspireCommand.

        Parameters
        ----------
        self : InspireCommand
            Instance of the command.

        Returns
        -------
        List[CLIArgument]
            List of CLIArgument objects representing available options.
        """
        # Provide CLI options for capitalization format.
        return [
            CLIArgument(
                flags=["--case", "-c"],
                type=str,
                help="Capitalization format: 'upper', 'lower', 'title'.",
                choices=["upper", "lower", "title"],
                required=False,
            ),
        ]

    async def handle(self, inspire: Inspire) -> None:
        """
        Execute the command to print a random inspirational quote.

        Parameters
        ----------
        inspire : IInspire
            Service providing inspirational quotes.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Retrieve a random inspirational quote from the service.
        quote, author = inspire.random().values()

        # Get the desired capitalization format from arguments.
        text_case: str | None = self.argument("case")

        # Define available capitalization functions.
        case_functions: dict[str, callable] = {
            "upper": str.upper,
            "lower": str.lower,
            "title": str.title,
        }

        # Apply the selected capitalization format if specified.
        if text_case in case_functions:
            quote = case_functions[text_case](quote)

        # Display the quote in the console with bold green formatting.
        self.textSuccessBold(quote)

        # Add a short delay before displaying the author.
        for letter in author:
            await asyncio.sleep(0.04)
            self.write(letter, end="", flush=True)

        # Add a newline after printing the author.
        self.line()
