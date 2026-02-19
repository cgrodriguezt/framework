from app.http.controllers.home_controller import HomeController
from orionis.support.facades.router import Route

Route.get("/ruta-api", [HomeController, "index"])