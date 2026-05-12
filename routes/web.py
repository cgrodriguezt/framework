from app.http.controllers.home_controller import HomeController
from orionis.support.facades.router import Route

Route.group(prefix="admin", routes=[
    Route.get("/{slug:str}/{id:int}", [HomeController, "index"]),
])
