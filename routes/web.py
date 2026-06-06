from app.http.controllers.user_controller import HomeController
from orionis.support.facades.router import Route

Route.group(prefix="admin", routes=[
    Route.get("/{slug:str}/{identifier:int}", [HomeController, "index"]),
    Route.post("/store", [HomeController, "store"]),
])
