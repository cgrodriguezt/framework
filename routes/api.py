from app.http.controllers.user_controller import HomeController
from orionis.support.facades.router import Route

Route.group(prefix="api/v1", routes=[
    Route.get("/{slug:str}/{identifier:int}", [HomeController, "index"]),
])
