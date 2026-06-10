from app.http.controllers.user_controller import UserController
from orionis.support.facades.router import Route

Route.group(prefix="admin", routes=[
    Route.get("/{slug:str}/{identifier:int}", [UserController, "index"]),
    Route.post("/store", [UserController, "store"]),
])
