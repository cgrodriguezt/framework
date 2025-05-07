class FakeUser:
    def __init__(self):
        self.user_data = None

    def get_user(self, user_id):
        return self.user_data

class FakeUserWithPermissions:
    def __init__(self):
        self.permissions = set()

    def add_permission(self, permission: str):
        self.permissions.add(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

class UserController:
    def __init__(self, user_repository: FakeUser):
        self.user_repository = user_repository

    def create_user_with_permissions(self, user_permissions: FakeUserWithPermissions, permissions: list[str]):
        for permission in permissions:
            user_permissions.add_permission(permission)
        return user_permissions