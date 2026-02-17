from app.http.controllers.home_controller import HomeController
from orionis.support.facades.router import Route

Route.prefix("/home").group(
    Route.get("/", [HomeController, "index"])
)