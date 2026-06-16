from orionis.console.base.command import BaseCommand
from orionis.http.routes.loader import RouteLoader

class RouteListCommand(BaseCommand):

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "route:list"

    # Command description
    description: str = "Show available routes and their handlers."

    async def handle(
        self,
        route_loader: RouteLoader,
    ) -> None:
        self.write(route_loader.load())
